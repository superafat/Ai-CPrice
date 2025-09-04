"""
系統管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
from loguru import logger

from ..services.ocr.engine_manager import ocr_manager
from ..config import settings


router = APIRouter()


class SystemStats(BaseModel):
    """系統統計資料"""
    total_requests: int
    success_rate: float
    average_processing_time: float
    fallback_usage_rate: float
    emergency_usage_rate: float
    mathpix_daily_usage: int
    mathpix_remaining: int


class ErrorReport(BaseModel):
    """錯誤回報"""
    task_id: str
    error_type: str
    error_message: str
    user_feedback: Optional[str] = None
    timestamp: datetime


@router.get("/management/stats")
async def get_system_stats():
    """獲取系統統計資料"""
    try:
        # 獲取 OCR 引擎統計
        ocr_stats = await ocr_manager.get_stats()
        
        # 模擬額外統計資料
        system_stats = {
            **ocr_stats,
            "average_processing_time": 4.2,  # 秒
            "uptime_hours": 24.5,
            "active_tasks": 3,
            "completed_today": 156,
            "error_rate": 2.1,
            "top_failure_reasons": [
                {"reason": "影像品質過低", "count": 12, "percentage": 45.5},
                {"reason": "公式過於複雜", "count": 8, "percentage": 30.3},
                {"reason": "文字模糊不清", "count": 6, "percentage": 24.2}
            ]
        }
        
        return system_stats
        
    except Exception as e:
        logger.error(f"獲取系統統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"無法獲取統計: {str(e)}")


@router.get("/management/health")
async def health_check():
    """系統健康檢查"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ocr_engines": {
                    "paddleocr": settings.paddleocr_enabled,
                    "tesseract": settings.tesseract_enabled,
                    "pix2tex": settings.pix2tex_enabled,
                    "trocr": settings.trocr_enabled,
                    "mathpix": settings.mathpix_enabled and bool(settings.mathpix_app_id)
                },
                "storage": {
                    "uploads_dir": os.path.exists("uploads"),
                    "processed_dir": os.path.exists("processed"),
                    "outputs_dir": os.path.exists("outputs")
                },
                "external_services": {
                    "pandoc": True,  # 應該實際檢查
                    "redis": True    # 應該實際檢查
                }
            },
            "resource_usage": {
                "disk_usage_mb": sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(".")
                    for filename in filenames
                ) / 1024 / 1024,
                "active_connections": 5,  # 模擬
                "queue_length": 2         # 模擬
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/management/error-report")
async def submit_error_report(report: ErrorReport):
    """提交錯誤回報"""
    try:
        logger.warning(f"收到錯誤回報 - 任務: {report.task_id}, 類型: {report.error_type}")
        
        # 這裡應該將錯誤回報儲存到資料庫
        # 簡化為日誌記錄
        error_log = {
            "task_id": report.task_id,
            "error_type": report.error_type,
            "error_message": report.error_message,
            "user_feedback": report.user_feedback,
            "timestamp": report.timestamp.isoformat()
        }
        
        logger.info(f"錯誤回報已記錄: {error_log}")
        
        return {
            "report_id": f"error_{report.task_id}_{int(report.timestamp.timestamp())}",
            "status": "received",
            "message": "錯誤回報已收到，我們將儘快處理"
        }
        
    except Exception as e:
        logger.error(f"錯誤回報處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"回報失敗: {str(e)}")


@router.get("/management/errors")
async def get_error_list(
    limit: int = Query(50, ge=1, le=200),
    error_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=30)
):
    """獲取錯誤清單"""
    try:
        # 模擬錯誤清單
        errors = [
            {
                "id": "error_001",
                "task_id": "task_123",
                "error_type": "ocr_failure",
                "error_message": "公式識別失敗",
                "timestamp": datetime.now() - timedelta(hours=2),
                "resolved": False
            },
            {
                "id": "error_002", 
                "task_id": "task_124",
                "error_type": "image_quality",
                "error_message": "影像品質過低",
                "timestamp": datetime.now() - timedelta(hours=5),
                "resolved": True
            }
        ]
        
        # 過濾條件
        if error_type:
            errors = [e for e in errors if e["error_type"] == error_type]
        
        # 限制數量
        errors = errors[:limit]
        
        return {
            "errors": errors,
            "total_count": len(errors),
            "filter": {
                "error_type": error_type,
                "days": days,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"獲取錯誤清單失敗: {e}")
        raise HTTPException(status_code=500, detail=f"無法獲取錯誤清單: {str(e)}")


@router.post("/management/quota/reset")
async def reset_daily_quota():
    """重置每日配額"""
    try:
        # 重置 Mathpix 每日使用量
        ocr_manager.usage_stats["mathpix_daily_usage"] = 0
        
        logger.info("每日配額已重置")
        
        return {
            "message": "每日配額已重置",
            "mathpix_remaining": settings.mathpix_daily_limit,
            "reset_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"配額重置失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重置失敗: {str(e)}")


@router.get("/management/quota/status")
async def get_quota_status():
    """獲取配額使用狀態"""
    try:
        stats = await ocr_manager.get_stats()
        
        return {
            "mathpix": {
                "daily_limit": settings.mathpix_daily_limit,
                "daily_used": stats["mathpix_daily_usage"],
                "daily_remaining": stats["mathpix_remaining"],
                "usage_percentage": (stats["mathpix_daily_usage"] / settings.mathpix_daily_limit * 100) if settings.mathpix_daily_limit > 0 else 0
            },
            "general": {
                "total_requests": stats["total_requests"],
                "success_rate": stats["success_rate"],
                "fallback_rate": stats["fallback_rate"],
                "emergency_rate": stats["emergency_rate"]
            }
        }
        
    except Exception as e:
        logger.error(f"獲取配額狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"無法獲取配額狀態: {str(e)}")


@router.post("/management/cleanup")
async def cleanup_old_files(days_old: int = 7):
    """清理舊檔案"""
    try:
        cleanup_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 清理目錄
        directories = ["uploads", "processed", "outputs", "temp_export"]
        
        for directory in directories:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            cleanup_count += 1
        
        logger.info(f"已清理 {cleanup_count} 個舊檔案")
        
        return {
            "cleaned_files": cleanup_count,
            "cutoff_days": days_old,
            "message": f"已清理 {cleanup_count} 個超過 {days_old} 天的檔案"
        }
        
    except Exception as e:
        logger.error(f"檔案清理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"清理失敗: {str(e)}")


@router.get("/management/dashboard")
async def get_dashboard_data():
    """獲取管理儀表板資料"""
    try:
        # 綜合各種統計資料
        ocr_stats = await ocr_manager.get_stats()
        
        dashboard_data = {
            "overview": {
                "total_requests_today": 156,
                "success_rate": ocr_stats["success_rate"],
                "average_processing_time": 4.2,
                "active_tasks": 3
            },
            "ocr_performance": {
                "text_ocr_success": 96.5,
                "formula_ocr_success": 89.2,
                "fallback_usage": ocr_stats["fallback_rate"],
                "emergency_usage": ocr_stats["emergency_rate"]
            },
            "resource_usage": {
                "mathpix_quota_used": ocr_stats["mathpix_daily_usage"],
                "mathpix_quota_limit": settings.mathpix_daily_limit,
                "disk_usage_mb": 1250.5,
                "memory_usage_mb": 890.2
            },
            "recent_errors": [
                {
                    "time": "10:30",
                    "type": "影像品質過低",
                    "count": 3
                },
                {
                    "time": "09:45", 
                    "type": "公式識別失敗",
                    "count": 1
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"獲取儀表板資料失敗: {e}")
        raise HTTPException(status_code=500, detail=f"無法獲取儀表板資料: {str(e)}")