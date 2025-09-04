"""
日誌設定工具
"""
import sys
import os
from loguru import logger
from ..config import settings


def setup_logging():
    """設定應用程式日誌"""
    
    # 移除預設處理器
    logger.remove()
    
    # 控制台輸出
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 檔案輸出
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="gz"
    )
    
    # 錯誤日誌單獨檔案
    error_log_file = settings.log_file.replace('.log', '_error.log')
    logger.add(
        error_log_file,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        rotation="5 MB",
        retention="60 days"
    )
    
    logger.info("日誌系統初始化完成")