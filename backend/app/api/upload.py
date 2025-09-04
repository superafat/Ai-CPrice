"""
檔案上傳 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import aiofiles
from loguru import logger

from ..models.ocr_result import ProcessingTask, ProcessingStage, QualityLevel
from ..services.image_processing.preprocessor import ImagePreprocessor, ImageSegmenter, BlockClassifier
from ..services.ocr.engine_manager import ocr_manager
from ..config import settings


router = APIRouter()

# 全域服務實例
preprocessor = ImagePreprocessor()
segmenter = ImageSegmenter()
classifier = BlockClassifier()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    auto_process: bool = Form(True)
):
    """
    上傳檔案端點
    支援圖片和 PDF 格式
    """
    try:
        # 驗證檔案類型
        if not file.filename:
            raise HTTPException(status_code=400, detail="檔案名稱不能為空")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.supported_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"不支援的檔案格式。支援格式: {', '.join(settings.supported_formats)}"
            )
        
        # 檢查檔案大小
        contents = await file.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"檔案大小超過限制 ({settings.max_file_size / 1024 / 1024:.1f}MB)"
            )
        
        # 生成任務 ID
        task_id = str(uuid.uuid4())
        
        # 儲存檔案
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # 建立處理任務
        task = ProcessingTask(
            task_id=task_id,
            original_filename=file.filename,
            original_file_path=file_path,
            stage=ProcessingStage.UPLOADED
        )
        
        logger.info(f"檔案上傳成功: {file.filename}, 任務ID: {task_id}")
        
        # 如果啟用自動處理，立即開始處理
        if auto_process:
            # 這裡應該使用 Celery 任務佇列，簡化為直接處理
            try:
                await process_uploaded_file(task)
            except Exception as e:
                logger.error(f"自動處理失敗: {e}")
                task.stage = ProcessingStage.FAILED
                task.error_message = str(e)
        
        return {
            "task_id": task_id,
            "filename": file.filename,
            "file_size": len(contents),
            "stage": task.stage,
            "message": "檔案上傳成功" + ("，正在處理中..." if auto_process else "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"檔案上傳失敗: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.get("/upload/status/{task_id}")
async def get_upload_status(task_id: str):
    """獲取上傳任務狀態"""
    try:
        # 這裡應該從資料庫或快取中獲取任務狀態
        # 簡化實作：檢查檔案是否存在
        upload_files = [f for f in os.listdir("uploads") if f.startswith(task_id)]
        
        if not upload_files:
            raise HTTPException(status_code=404, detail="任務不存在")
        
        # 模擬任務狀態
        return {
            "task_id": task_id,
            "stage": "completed",  # 實際應該從任務狀態獲取
            "progress": 100,
            "message": "處理完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取任務狀態失敗: {e}")
        raise HTTPException(status_code=500, detail="無法獲取任務狀態")


async def process_uploaded_file(task: ProcessingTask):
    """處理上傳的檔案（完整流程）"""
    try:
        logger.info(f"開始處理任務 {task.task_id}")
        
        # 1. 影像前處理
        task.stage = ProcessingStage.PREPROCESSING
        processed_path = await preprocessor.preprocess_image(
            task.original_file_path, 
            QualityLevel.B
        )
        
        # 2. 影像切塊
        task.stage = ProcessingStage.SEGMENTED
        blocks = await segmenter.segment_problems(processed_path)
        
        # 3. 區塊分類
        task.stage = ProcessingStage.CLASSIFIED
        classified_blocks = await classifier.batch_classify(blocks)
        task.blocks = classified_blocks
        task.total_blocks = len(classified_blocks)
        
        # 4. OCR 處理
        task.stage = ProcessingStage.OCR_PROCESSING
        successful_blocks = 0
        
        for block in task.blocks:
            try:
                if block.type in [BlockType.PROBLEM, BlockType.OPTIONS]:
                    # 文字 OCR
                    ocr_result = await ocr_manager.process_text_block(block.image_path)
                elif block.type == BlockType.FORMULA:
                    # 公式 OCR
                    ocr_result = await ocr_manager.process_formula_block(block.image_path)
                else:
                    continue
                
                block.ocr_result = ocr_result
                if ocr_result.is_successful:
                    successful_blocks += 1
                    
            except Exception as e:
                logger.error(f"區塊 {block.id} OCR 處理失敗: {e}")
                task.failed_blocks += 1
        
        task.successful_blocks = successful_blocks
        task.failed_blocks = task.total_blocks - successful_blocks
        
        # 5. 標準化
        task.stage = ProcessingStage.STANDARDIZING
        task.standardized_markdown = await generate_standardized_markdown(task)
        
        # 6. 完成
        task.stage = ProcessingStage.COMPLETED
        logger.info(f"任務 {task.task_id} 處理完成")
        
    except Exception as e:
        logger.error(f"任務處理失敗: {e}")
        task.stage = ProcessingStage.FAILED
        task.error_message = str(e)
        raise


async def generate_standardized_markdown(task: ProcessingTask) -> str:
    """生成標準化的 Markdown 內容"""
    markdown_lines = []
    
    # 按順序處理區塊
    sorted_blocks = sorted(task.blocks, key=lambda x: x.order_in_document)
    
    for block in sorted_blocks:
        if not block.ocr_result or not block.ocr_result.text:
            continue
        
        text = block.ocr_result.text
        
        if block.type == BlockType.PROBLEM:
            markdown_lines.append(f"## 題目\n{text}\n")
        elif block.type == BlockType.OPTIONS:
            # 標準化選項格式
            options = text.split('\n')
            for i, option in enumerate(options):
                if option.strip():
                    label = ['(A)', '(B)', '(C)', '(D)'][i % 4]
                    markdown_lines.append(f"{label} {option.strip()}")
            markdown_lines.append("")
        elif block.type == BlockType.FORMULA:
            # 包裝 LaTeX 公式
            if text.strip():
                markdown_lines.append(f"$$\n{text}\n$$\n")
        elif block.type == BlockType.SOLUTION:
            markdown_lines.append(f"### 解析\n{text}\n")
    
    return "\n".join(markdown_lines)


from ..models.ocr_result import BlockType