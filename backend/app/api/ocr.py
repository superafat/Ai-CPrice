"""
OCR 處理 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

from ..models.ocr_result import OCRResult, ProcessingTask, ImageBlock
from ..services.ocr.engine_manager import ocr_manager
from ..services.image_processing.preprocessor import ImagePreprocessor, BlockClassifier


router = APIRouter()


class OCRRequest(BaseModel):
    """OCR 請求模型"""
    image_path: str
    block_type: str  # "text" or "formula"
    quality_level: str = "B"


class BatchOCRRequest(BaseModel):
    """批次 OCR 請求"""
    task_id: str
    force_retry: bool = False


class ValidationRequest(BaseModel):
    """LaTeX 驗證請求"""
    latex_text: str


@router.post("/ocr/text")
async def process_text_ocr(request: OCRRequest):
    """處理文字 OCR 請求"""
    try:
        if request.block_type != "text":
            raise HTTPException(status_code=400, detail="此端點僅處理文字區塊")
        
        result = await ocr_manager.process_text_block(
            request.image_path, 
            request.quality_level
        )
        
        return {
            "success": result.is_successful,
            "text": result.text,
            "confidence": result.confidence,
            "confidence_level": result.confidence_level,
            "engine_used": result.engine_used,
            "processing_time_ms": result.processing_time_ms,
            "attempts": len(result.attempts)
        }
        
    except Exception as e:
        logger.error(f"文字 OCR 處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"OCR 處理失敗: {str(e)}")


@router.post("/ocr/formula")
async def process_formula_ocr(request: OCRRequest):
    """處理公式 OCR 請求"""
    try:
        if request.block_type != "formula":
            raise HTTPException(status_code=400, detail="此端點僅處理公式區塊")
        
        result = await ocr_manager.process_formula_block(
            request.image_path,
            request.quality_level
        )
        
        return {
            "success": result.is_successful,
            "latex": result.text,
            "confidence": result.confidence,
            "confidence_level": result.confidence_level,
            "engine_used": result.engine_used,
            "is_compilable": result.is_compilable,
            "processing_time_ms": result.processing_time_ms,
            "attempts": len(result.attempts)
        }
        
    except Exception as e:
        logger.error(f"公式 OCR 處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"公式 OCR 處理失敗: {str(e)}")


@router.post("/ocr/batch")
async def process_batch_ocr(request: BatchOCRRequest):
    """批次處理任務的所有區塊"""
    try:
        # 這裡應該從資料庫獲取任務，簡化為模擬
        logger.info(f"開始批次 OCR 處理任務 {request.task_id}")
        
        # 模擬處理結果
        return {
            "task_id": request.task_id,
            "total_blocks": 4,
            "successful_blocks": 3,
            "failed_blocks": 1,
            "processing_time_ms": 4500,
            "message": "批次 OCR 處理完成"
        }
        
    except Exception as e:
        logger.error(f"批次 OCR 處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批次處理失敗: {str(e)}")


@router.post("/ocr/retry")
async def retry_ocr_block(
    task_id: str,
    block_id: str,
    use_high_quality: bool = True,
    force_emergency_engine: bool = False
):
    """重試特定區塊的 OCR 處理"""
    try:
        logger.info(f"重試任務 {task_id} 的區塊 {block_id}")
        
        # 這裡應該實作重試邏輯
        # 1. 獲取原始區塊資訊
        # 2. 使用更高品質或備援引擎重新處理
        # 3. 更新結果
        
        quality_level = "A" if use_high_quality else "B"
        
        # 模擬重試結果
        return {
            "task_id": task_id,
            "block_id": block_id,
            "retry_successful": True,
            "new_confidence": 0.89,
            "quality_level": quality_level,
            "engine_used": "mathpix" if force_emergency_engine else "primary",
            "message": "重試成功"
        }
        
    except Exception as e:
        logger.error(f"OCR 重試失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重試失敗: {str(e)}")


@router.post("/validate/latex")
async def validate_latex(request: ValidationRequest):
    """驗證 LaTeX 公式是否可編譯"""
    try:
        # 使用 OCR 管理器的驗證功能
        is_valid = await ocr_manager._validate_latex(request.latex_text)
        
        return {
            "latex": request.latex_text,
            "is_valid": is_valid,
            "message": "LaTeX 語法正確" if is_valid else "LaTeX 語法有誤"
        }
        
    except Exception as e:
        logger.error(f"LaTeX 驗證失敗: {e}")
        raise HTTPException(status_code=500, detail=f"驗證失敗: {str(e)}")


@router.get("/ocr/stats")
async def get_ocr_stats():
    """獲取 OCR 引擎使用統計"""
    try:
        stats = await ocr_manager.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"無法獲取統計: {str(e)}")


@router.post("/segment")
async def segment_image(
    task_id: str,
    force_single_problem: bool = False
):
    """影像切塊處理"""
    try:
        # 這裡應該從任務中獲取影像路徑
        logger.info(f"開始切塊處理任務 {task_id}")
        
        # 模擬切塊結果
        return {
            "task_id": task_id,
            "total_problems_detected": 1 if force_single_problem else 2,
            "blocks_created": 4,
            "message": "切塊完成",
            "suggestion": "偵測到多個題目，建議裁成單題可提升準確率與速度" if not force_single_problem else None
        }
        
    except Exception as e:
        logger.error(f"影像切塊失敗: {e}")
        raise HTTPException(status_code=500, detail=f"切塊失敗: {str(e)}")


@router.post("/classify")
async def classify_blocks(task_id: str):
    """區塊分類處理"""
    try:
        logger.info(f"開始區塊分類任務 {task_id}")
        
        # 模擬分類結果
        return {
            "task_id": task_id,
            "classified_blocks": [
                {"block_id": "problem_0", "type": "problem", "confidence": 0.95},
                {"block_id": "options_0", "type": "options", "confidence": 0.88},
                {"block_id": "formula_0", "type": "formula", "confidence": 0.92},
                {"block_id": "solution_0", "type": "solution", "confidence": 0.85}
            ],
            "classification_accuracy": 0.92,
            "message": "區塊分類完成"
        }
        
    except Exception as e:
        logger.error(f"區塊分類失敗: {e}")
        raise HTTPException(status_code=500, detail=f"分類失敗: {str(e)}")