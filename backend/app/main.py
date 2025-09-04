"""
FastAPI 主應用程式
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from loguru import logger

from .config import settings
from .api import upload, ocr, export, management
from .utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時初始化
    logger.info("正在啟動 OCR 系統...")
    
    # 確保必要目錄存在
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 初始化 OCR 引擎
    from .services.ocr.engine_manager import OCREngineManager
    ocr_manager = OCREngineManager()
    await ocr_manager.initialize()
    
    logger.info("OCR 系統啟動完成")
    
    yield
    
    # 關閉時清理
    logger.info("正在關閉 OCR 系統...")
    await ocr_manager.cleanup()


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.app_name,
    description="物理/數學題目 OCR 識別與 Word 匯出系統",
    version="1.0.0",
    lifespan=lifespan
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案服務
app.mount("/static", StaticFiles(directory="static"), name="static")

# 註冊 API 路由
app.include_router(upload.router, prefix="/api", tags=["上傳"])
app.include_router(ocr.router, prefix="/api", tags=["OCR"])
app.include_router(export.router, prefix="/api", tags=["匯出"])
app.include_router(management.router, prefix="/api", tags=["管理"])


@app.get("/")
async def root():
    """根路由 - 系統狀態"""
    return {
        "message": "OCR 數學題目解析系統",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "ocr_engines": {
            "paddleocr": settings.paddleocr_enabled,
            "tesseract": settings.tesseract_enabled,
            "pix2tex": settings.pix2tex_enabled,
            "mathpix": settings.mathpix_enabled,
        }
    }


if __name__ == "__main__":
    # 設定日誌
    setup_logging()
    
    # 啟動服務
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )