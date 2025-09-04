"""
Celery 任務佇列配置
"""
from celery import Celery
from ..config import settings

# 建立 Celery 應用
celery_app = Celery(
    "ocr_system",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.services.queue.tasks"]
)

# Celery 配置
celery_app.conf.update(
    # 任務設定
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    
    # 併發設定
    worker_concurrency=4,
    worker_max_tasks_per_child=100,
    
    # 任務路由
    task_routes={
        "app.services.queue.tasks.process_ocr": {"queue": "ocr"},
        "app.services.queue.tasks.export_word": {"queue": "export"},
    },
    
    # 結果過期時間
    result_expires=3600,  # 1小時
    
    # 任務時間限制
    task_time_limit=300,  # 5分鐘
    task_soft_time_limit=240,  # 4分鐘
)