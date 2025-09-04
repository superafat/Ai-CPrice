"""
Mathpix 引擎實作 - 兜底公式識別引擎（配額保護）
"""
import asyncio
import base64
from typing import Dict, Any
from loguru import logger
import httpx

from ...config import settings


class MathpixEngine:
    """Mathpix 引擎封裝"""
    
    def __init__(self):
        self.app_id = settings.mathpix_app_id
        self.app_key = settings.mathpix_app_key
        self.is_initialized = False
        self.api_url = "https://api.mathpix.com/v3/text"
    
    async def initialize(self):
        """初始化 Mathpix 引擎"""
        try:
            if not self.app_id or not self.app_key:
                logger.warning("Mathpix API 金鑰未設定，使用模擬模式")
                self.is_initialized = True
                return
            
            # 測試 API 連線
            async with httpx.AsyncClient() as client:
                headers = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "Content-type": "application/json"
                }
                
                # 發送測試請求
                test_data = {
                    "src": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gASTEVBRCBUZWNobm9sb2dpZXM=",
                    "formats": ["latex_simplified"],
                    "data_options": {"include_asciimath": False}
                }
                
                response = await client.post(
                    self.api_url,
                    json=test_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    self.is_initialized = True
                    logger.info("Mathpix 引擎初始化完成")
                else:
                    logger.warning(f"Mathpix API 測試失敗: {response.status_code}")
                    self.is_initialized = True  # 仍標記為初始化，但會在實際使用時處理錯誤
            
        except Exception as e:
            logger.error(f"Mathpix 初始化失敗: {e}")
            self.is_initialized = True  # 允許模擬模式運行
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """
        Mathpix 主要用於公式，文字識別效果一般
        """
        return {
            "text": "",
            "confidence": 0.3,
            "details": {"engine": "mathpix"},
            "note": "Mathpix 主要用於公式識別"
        }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """識別 LaTeX 公式"""
        if not self.is_initialized:
            raise RuntimeError("Mathpix 引擎未初始化")
        
        try:
            if not self.app_id or not self.app_key:
                # 模擬模式
                return {
                    "text": "\\int_{a}^{b} f(x) dx",
                    "confidence": 0.92,
                    "details": {"engine": "mathpix_simulation"}
                }
            
            # 讀取並編碼影像
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 準備請求資料
            data = {
                "src": f"data:image/jpeg;base64,{image_base64}",
                "formats": ["latex_simplified"],
                "data_options": {
                    "include_asciimath": False,
                    "include_mathml": False,
                    "include_tsv": False
                }
            }
            
            headers = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "Content-type": "application/json"
            }
            
            # 發送請求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                latex_text = result.get("latex_simplified", "")
                confidence = result.get("confidence", 0.0)
                
                # Mathpix 置信度通常很高，但我們需要保守估計
                adjusted_confidence = min(confidence * 0.9, 0.95)
                
                return {
                    "text": latex_text,
                    "confidence": adjusted_confidence,
                    "details": {
                        "engine": "mathpix",
                        "original_confidence": confidence,
                        "request_id": result.get("request_id"),
                        "latex": latex_text
                    }
                }
            else:
                error_msg = f"Mathpix API 錯誤: {response.status_code}"
                logger.error(error_msg)
                return {
                    "text": "",
                    "confidence": 0.0,
                    "details": {"engine": "mathpix"},
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Mathpix 公式識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "mathpix"},
                "error": str(e)
            }
    
    async def cleanup(self):
        """清理資源"""
        # Mathpix 是 API 服務，不需要特殊清理
        logger.info("Mathpix 引擎資源已清理")