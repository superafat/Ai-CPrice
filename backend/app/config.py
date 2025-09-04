"""
系統配置管理
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 基本設定
    app_name: str = "OCR Math Problem Solution System"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 資料庫與快取
    redis_url: str = "redis://localhost:6379"
    
    # OCR 引擎設定
    paddleocr_enabled: bool = True
    tesseract_enabled: bool = True
    doctr_enabled: bool = True
    pix2tex_enabled: bool = True
    trocr_enabled: bool = True
    mathpix_enabled: bool = True
    
    # Mathpix API (兜底引擎)
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None
    mathpix_daily_limit: int = 100
    mathpix_account_limit: int = 1000
    
    # 影像處理參數
    min_width_text: int = 1200      # 題幹區最小寬度
    min_width_formula: int = 800    # 公式區最小寬度
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: list = ["jpg", "jpeg", "png", "webp", "pdf"]
    
    # OCR 置信度閾值
    text_confidence_threshold: float = 0.8
    formula_confidence_threshold: float = 0.7
    
    # 重試策略
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 2
    task_timeout_seconds: int = 300
    
    # 並發控制
    max_concurrent_tasks: int = 10
    max_upload_concurrent: int = 5
    
    # 匯出設定
    default_problem_font_size: int = 11
    default_solution_font_size: int = 9
    min_font_size: int = 8
    max_font_size: int = 16
    max_image_width_cm: float = 14.0
    
    # 安全設定
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    secret_key: str = "your-secret-key-change-in-production"
    
    # 日誌設定
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全域設定實例
settings = Settings()


# OCR 引擎優先級配置
OCR_ENGINE_CONFIG = {
    "text": {
        "primary": "paddleocr" if settings.paddleocr_enabled else "tesseract",
        "fallback": ["tesseract", "doctr"] if settings.paddleocr_enabled else ["doctr"],
    },
    "formula": {
        "primary": "pix2tex" if settings.pix2tex_enabled else "trocr", 
        "fallback": ["trocr"] if settings.pix2tex_enabled else [],
        "emergency": "mathpix" if settings.mathpix_enabled else None,
    }
}


# 品質等級定義
QUALITY_LEVELS = {
    "A": {"min_resolution": 2000, "min_contrast": 0.8, "noise_level": "low"},
    "B": {"min_resolution": 1200, "min_contrast": 0.6, "noise_level": "medium"},
    "C": {"min_resolution": 800, "min_contrast": 0.4, "noise_level": "high"},
}


# 區塊分類規則
BLOCK_CLASSIFICATION = {
    "formula_keywords": ["\\frac", "\\sqrt", "\\int", "\\sum", "\\lim", "^", "_", "\\alpha", "\\beta"],
    "option_patterns": [r"\([A-D]\)", r"[A-D]\."],
    "problem_indicators": ["題", "問", "求", "計算", "證明"],
}


# Word 樣式配置
WORD_STYLES = {
    "problem": {
        "name": "CCH-Problem",
        "font_family": "Times New Roman",
        "default_size": settings.default_problem_font_size,
    },
    "options": {
        "name": "CCH-Options", 
        "font_family": "Times New Roman",
        "default_size": settings.default_problem_font_size,
    },
    "solution": {
        "name": "CCH-Solution",
        "font_family": "Times New Roman", 
        "default_size": settings.default_solution_font_size,
    }
}