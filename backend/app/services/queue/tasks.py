"""
Celery 異步任務
"""
from celery import current_task
from loguru import logger
import time

from .celery_app import celery_app
from ..ocr.engine_manager import ocr_manager
from ..image_processing.preprocessor import ImagePreprocessor, ImageSegmenter, BlockClassifier
from ..export.word_exporter import WordExporter
from ...models.ocr_result import ProcessingTask, ProcessingStage, ExportSettings


@celery_app.task(bind=True)
def process_ocr_task(self, task_data: dict):
    """
    異步 OCR 處理任務
    """
    task_id = task_data["task_id"]
    
    try:
        logger.info(f"開始處理 OCR 任務: {task_id}")
        
        # 更新任務狀態
        self.update_state(
            state="PROGRESS",
            meta={"stage": "preprocessing", "progress": 10}
        )
        
        # 模擬處理流程
        stages = [
            ("preprocessing", 20),
            ("segmentation", 40),
            ("classification", 50),
            ("ocr_processing", 80),
            ("standardizing", 90),
        ]
        
        for stage, progress in stages:
            # 模擬處理時間
            time.sleep(1)
            
            self.update_state(
                state="PROGRESS", 
                meta={"stage": stage, "progress": progress}
            )
        
        # 完成處理
        result = {
            "task_id": task_id,
            "stage": "completed",
            "progress": 100,
            "total_blocks": 4,
            "successful_blocks": 3,
            "failed_blocks": 1,
            "processing_time": 4.2
        }
        
        logger.info(f"OCR 任務 {task_id} 處理完成")
        return result
        
    except Exception as e:
        logger.error(f"OCR 任務 {task_id} 處理失敗: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "failed"}
        )
        raise


@celery_app.task(bind=True)
def export_word_task(self, task_id: str, export_settings: dict):
    """
    異步 Word 匯出任務
    """
    try:
        logger.info(f"開始匯出任務: {task_id}")
        
        self.update_state(
            state="PROGRESS",
            meta={"stage": "generating_markdown", "progress": 20}
        )
        
        # 模擬匯出流程
        time.sleep(2)
        
        self.update_state(
            state="PROGRESS",
            meta={"stage": "converting_to_word", "progress": 60}
        )
        
        time.sleep(3)
        
        self.update_state(
            state="PROGRESS", 
            meta={"stage": "validating_omml", "progress": 90}
        )
        
        time.sleep(1)
        
        # 完成匯出
        result = {
            "task_id": task_id,
            "output_file": f"outputs/{task_id}.docx",
            "file_size": 2048000,
            "omml_validation": {
                "total_formulas": 5,
                "omml_formulas": 5,
                "omml_ratio": 1.0,
                "all_formulas_omml": True
            }
        }
        
        logger.info(f"Word 匯出任務 {task_id} 完成")
        return result
        
    except Exception as e:
        logger.error(f"Word 匯出任務 {task_id} 失敗: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task
def cleanup_old_files(days_old: int = 7):
    """
    清理舊檔案任務
    """
    try:
        logger.info(f"開始清理 {days_old} 天前的檔案")
        
        import os
        from datetime import datetime, timedelta
        
        cleanup_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
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
        
        logger.info(f"清理完成，刪除了 {cleanup_count} 個檔案")
        return {"cleaned_files": cleanup_count}
        
    except Exception as e:
        logger.error(f"檔案清理失敗: {e}")
        raise


@celery_app.task
def generate_daily_report():
    """
    生成每日報告任務
    """
    try:
        logger.info("開始生成每日報告")
        
        # 這裡應該從資料庫收集統計資料
        # 簡化為模擬報告
        report = {
            "date": time.strftime("%Y-%m-%d"),
            "total_requests": 156,
            "success_rate": 95.2,
            "average_processing_time": 4.2,
            "top_errors": [
                {"type": "影像品質過低", "count": 8},
                {"type": "公式過於複雜", "count": 3},
                {"type": "網路連線問題", "count": 1}
            ]
        }
        
        # 儲存報告
        import json
        report_file = f"reports/daily_report_{report['date']}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"每日報告已生成: {report_file}")
        return report
        
    except Exception as e:
        logger.error(f"每日報告生成失敗: {e}")
        raise