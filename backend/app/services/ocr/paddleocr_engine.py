"""
PaddleOCR 引擎實作 - 主要用於中文文字識別
"""
import asyncio
from typing import Dict, Any
from loguru import logger

try:
    from paddleocr import PaddleOCR
except ImportError:
    logger.warning("PaddleOCR 未安裝，將使用模擬模式")
    PaddleOCR = None


class PaddleOCREngine:
    """PaddleOCR 引擎封裝"""
    
    def __init__(self):
        self.ocr = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化 PaddleOCR 引擎"""
        try:
            if PaddleOCR is None:
                logger.warning("PaddleOCR 不可用，使用模擬模式")
                self.is_initialized = True
                return
            
            # 在執行緒中初始化（避免阻塞）
            loop = asyncio.get_event_loop()
            self.ocr = await loop.run_in_executor(
                None, 
                lambda: PaddleOCR(
                    use_angle_cls=True,
                    lang='ch',  # 中文
                    use_gpu=False,  # 根據環境調整
                    show_log=False
                )
            )
            self.is_initialized = True
            logger.info("PaddleOCR 引擎初始化完成")
            
        except Exception as e:
            logger.error(f"PaddleOCR 初始化失敗: {e}")
            self.is_initialized = False
            raise
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """識別文字內容"""
        if not self.is_initialized:
            raise RuntimeError("PaddleOCR 引擎未初始化")
        
        try:
            if self.ocr is None:
                # 模擬模式
                return {
                    "text": "模擬文字識別結果",
                    "confidence": 0.85,
                    "details": []
                }
            
            # 在執行緒中執行 OCR（避免阻塞）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.ocr.ocr, 
                image_path
            )
            
            # 解析結果
            if result and result[0]:
                texts = []
                confidences = []
                details = []
                
                for line in result[0]:
                    bbox, (text, confidence) = line
                    texts.append(text)
                    confidences.append(confidence)
                    details.append({
                        "bbox": bbox,
                        "text": text,
                        "confidence": confidence
                    })
                
                # 組合文字
                combined_text = "\n".join(texts)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return {
                    "text": combined_text,
                    "confidence": avg_confidence,
                    "details": details
                }
            else:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "details": []
                }
                
        except Exception as e:
            logger.error(f"PaddleOCR 文字識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": [],
                "error": str(e)
            }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """
        PaddleOCR 不適合公式識別，返回低置信度結果
        """
        return {
            "text": "",
            "confidence": 0.1,
            "details": [],
            "note": "PaddleOCR 不適用於公式識別"
        }
    
    async def cleanup(self):
        """清理資源"""
        if self.ocr:
            # PaddleOCR 通常不需要顯式清理
            pass
        logger.info("PaddleOCR 引擎資源已清理")