"""
Tesseract 引擎實作 - 備援文字識別引擎
"""
import asyncio
from typing import Dict, Any
from loguru import logger
import os

try:
    import pytesseract
    from PIL import Image
except ImportError:
    logger.warning("Tesseract 相關套件未安裝，將使用模擬模式")
    pytesseract = None
    Image = None


class TesseractEngine:
    """Tesseract 引擎封裝"""
    
    def __init__(self):
        self.is_initialized = False
        self.config = "--oem 3 --psm 6"  # OCR Engine Mode 3, Page Segmentation Mode 6
    
    async def initialize(self):
        """初始化 Tesseract 引擎"""
        try:
            if pytesseract is None:
                logger.warning("Tesseract 不可用，使用模擬模式")
                self.is_initialized = True
                return
            
            # 檢查 Tesseract 是否可用
            loop = asyncio.get_event_loop()
            version = await loop.run_in_executor(
                None,
                pytesseract.get_tesseract_version
            )
            
            self.is_initialized = True
            logger.info(f"Tesseract 引擎初始化完成，版本: {version}")
            
        except Exception as e:
            logger.error(f"Tesseract 初始化失敗: {e}")
            self.is_initialized = False
            raise
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """識別文字內容"""
        if not self.is_initialized:
            raise RuntimeError("Tesseract 引擎未初始化")
        
        try:
            if pytesseract is None:
                # 模擬模式
                return {
                    "text": "模擬 Tesseract 文字識別結果",
                    "confidence": 0.75,
                    "details": {"engine": "tesseract_simulation"}
                }
            
            # 載入影像
            image = Image.open(image_path)
            
            # 在執行緒中執行 OCR
            loop = asyncio.get_event_loop()
            
            # 獲取文字和置信度
            text_result = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(image, lang='chi_tra+eng', config=self.config)
            )
            
            # 獲取詳細資訊（包含置信度）
            data_result = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_data(image, lang='chi_tra+eng', config=self.config, output_type=pytesseract.Output.DICT)
            )
            
            # 計算平均置信度
            confidences = [conf for conf in data_result['conf'] if conf > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            
            # 清理文字
            cleaned_text = self._clean_text(text_result)
            
            return {
                "text": cleaned_text,
                "confidence": avg_confidence,
                "details": {
                    "engine": "tesseract",
                    "word_count": len([w for w in data_result['text'] if w.strip()]),
                    "avg_confidence": avg_confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Tesseract 文字識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "tesseract"},
                "error": str(e)
            }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """
        Tesseract 不適合公式識別，返回低置信度結果
        """
        return {
            "text": "",
            "confidence": 0.1,
            "details": {"engine": "tesseract"},
            "note": "Tesseract 不適用於公式識別"
        }
    
    def _clean_text(self, text: str) -> str:
        """清理 OCR 文字結果"""
        if not text:
            return ""
        
        # 移除多餘空白
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # 只保留非空行
                # 移除多餘空格
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def cleanup(self):
        """清理資源"""
        # Tesseract 通常不需要顯式清理
        logger.info("Tesseract 引擎資源已清理")