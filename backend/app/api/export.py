"""
匯出 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from loguru import logger

from ..models.ocr_result import ExportSettings, ProcessingTask
from ..services.export.word_exporter import WordExporter


router = APIRouter()

# 全域匯出器實例
word_exporter = WordExporter()


class ExportRequest(BaseModel):
    """匯出請求模型"""
    task_id: str
    export_settings: ExportSettings


class BatchExportRequest(BaseModel):
    """批次匯出請求"""
    task_ids: List[str]
    export_settings: ExportSettings


@router.post("/export/word")
async def export_single_word(request: ExportRequest):
    """匯出單一任務為 Word 文檔"""
    try:
        logger.info(f"開始匯出任務 {request.task_id} 為 Word 文檔")
        
        # 這裡應該從資料庫獲取任務資料
        # 模擬任務資料
        task = ProcessingTask(
            task_id=request.task_id,
            original_filename="test_problem.jpg",
            original_file_path="uploads/test_problem.jpg"
        )
        
        # 執行匯出
        output_path = await word_exporter.export_to_word(task, request.export_settings)
        
        # 驗證 OMML 公式
        validation_result = await word_exporter.validate_omml_formulas(output_path)
        
        return {
            "task_id": request.task_id,
            "output_file": output_path,
            "file_size": os.path.getsize(output_path),
            "export_settings": request.export_settings.dict(),
            "omml_validation": validation_result,
            "message": "Word 文檔匯出成功"
        }
        
    except Exception as e:
        logger.error(f"Word 匯出失敗: {e}")
        raise HTTPException(status_code=500, detail=f"匯出失敗: {str(e)}")


@router.post("/export/batch")
async def export_batch_word(request: BatchExportRequest):
    """批次匯出多個任務為單一 Word 文檔"""
    try:
        logger.info(f"開始批次匯出 {len(request.task_ids)} 個任務")
        
        # 獲取所有任務資料（模擬）
        tasks = []
        for task_id in request.task_ids:
            task = ProcessingTask(
                task_id=task_id,
                original_filename=f"problem_{task_id}.jpg",
                original_file_path=f"uploads/problem_{task_id}.jpg"
            )
            tasks.append(task)
        
        # 執行批次匯出
        output_path = await word_exporter.batch_export(tasks, request.export_settings)
        
        return {
            "task_ids": request.task_ids,
            "output_file": output_path,
            "file_size": os.path.getsize(output_path),
            "total_problems": len(tasks),
            "export_settings": request.export_settings.dict(),
            "message": "批次匯出完成"
        }
        
    except Exception as e:
        logger.error(f"批次匯出失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批次匯出失敗: {str(e)}")


@router.get("/export/download/{task_id}")
async def download_word_file(task_id: str):
    """下載生成的 Word 檔案"""
    try:
        file_path = os.path.join("outputs", f"{task_id}.docx")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        return FileResponse(
            path=file_path,
            filename=f"problem_solution_{task_id}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"檔案下載失敗: {e}")
        raise HTTPException(status_code=500, detail=f"下載失敗: {str(e)}")


@router.get("/export/preview/{task_id}")
async def preview_markdown(task_id: str):
    """預覽標準化的 Markdown 內容"""
    try:
        # 這裡應該從任務中獲取 Markdown 內容
        # 模擬預覽內容
        markdown_content = """## 題目
求解下列方程式：

$$\\frac{x^2 + 2x + 1}{x - 1} = 0$$

### 選項
(A) x = -1
(B) x = 1  
(C) x = 0
(D) 無解

### 解析
由於分母不能為零，所以 $x \\neq 1$。

分子 $x^2 + 2x + 1 = (x + 1)^2 = 0$

因此 $x = -1$

答案是 (A)。"""
        
        return {
            "task_id": task_id,
            "markdown_content": markdown_content,
            "preview_url": f"/api/export/preview/render/{task_id}",
            "message": "預覽內容已生成"
        }
        
    except Exception as e:
        logger.error(f"預覽生成失敗: {e}")
        raise HTTPException(status_code=500, detail=f"預覽失敗: {str(e)}")


@router.get("/export/settings/default")
async def get_default_export_settings():
    """獲取預設匯出設定"""
    return ExportSettings().dict()


@router.post("/export/settings/validate")
async def validate_export_settings(settings: ExportSettings):
    """驗證匯出設定"""
    try:
        # 驗證字級範圍
        errors = []
        warnings = []
        
        if settings.problem_font_size < 8 or settings.problem_font_size > 16:
            errors.append("題幹字級必須在 8-16 之間")
        
        if settings.solution_font_size < 8 or settings.solution_font_size > 16:
            errors.append("詳解字級必須在 8-16 之間")
        
        if settings.image_max_width_cm <= 0 or settings.image_max_width_cm > 20:
            errors.append("圖片最大寬度必須在 0-20cm 之間")
        
        # 建議
        if settings.problem_font_size == settings.solution_font_size:
            warnings.append("建議詳解字級小於題幹字級以提升可讀性")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "settings": settings.dict()
        }
        
    except Exception as e:
        logger.error(f"設定驗證失敗: {e}")
        raise HTTPException(status_code=500, detail=f"驗證失敗: {str(e)}")


@router.get("/export/formats")
async def get_supported_formats():
    """獲取支援的匯出格式"""
    return {
        "formats": [
            {
                "name": "Word 文檔 (.docx)",
                "extension": "docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "features": [
                    "OMML 公式（可編輯）",
                    "自訂字體大小",
                    "圖片原位插入",
                    "段落樣式"
                ]
            }
        ],
        "default_format": "docx"
    }