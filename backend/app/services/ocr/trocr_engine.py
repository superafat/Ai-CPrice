"""
TrOCR 引擎實作 - 備援公式識別引擎
"""
import asyncio
from typing import Dict, Any
from loguru import logger

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from PIL import Image
except ImportError:
    logger.warning("TrOCR 相關套件未安裝，將使用模擬模式")
    TrOCRProcessor = None
    VisionEncoderDecoderModel = None
    Image = None


class TrOCREngine:
    """TrOCR 引擎封裝"""
    
    def __init__(self):
        self.processor = None
        self.model = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化 TrOCR 模型"""
        try:
            if TrOCRProcessor is None or VisionEncoderDecoderModel is None:
                logger.warning("TrOCR 不可用，使用模擬模式")
                self.is_initialized = True
                return
            
            # 在執行緒中載入模型（避免阻塞）
            loop = asyncio.get_event_loop()
            
            # 載入處理器和模型
            self.processor = await loop.run_in_executor(
                None,
                lambda: TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
            )
            
            self.model = await loop.run_in_executor(
                None,
                lambda: VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
            )
            
            self.is_initialized = True
            logger.info("TrOCR 引擎初始化完成")
            
        except Exception as e:
            logger.error(f"TrOCR 初始化失敗: {e}")
            self.is_initialized = False
            raise
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """識別文字內容"""
        if not self.is_initialized:
            raise RuntimeError("TrOCR 引擎未初始化")
        
        try:
            if self.processor is None or self.model is None:
                # 模擬模式
                return {
                    "text": "模擬 TrOCR 文字識別結果",
                    "confidence": 0.72,
                    "details": {"engine": "trocr_simulation"}
                }
            
            # 載入影像
            image = Image.open(image_path).convert('RGB')
            
            # 在執行緒中執行識別
            loop = asyncio.get_event_loop()
            
            # 預處理影像
            pixel_values = await loop.run_in_executor(
                None,
                lambda: self.processor(image, return_tensors="pt").pixel_values
            )
            
            # 生成文字
            generated_ids = await loop.run_in_executor(
                None,
                lambda: self.model.generate(pixel_values)
            )
            
            # 解碼結果
            generated_text = await loop.run_in_executor(
                None,
                lambda: self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            )
            
            # TrOCR 不提供置信度，需要自行估算
            confidence = self._estimate_confidence(generated_text)
            
            return {
                "text": generated_text,
                "confidence": confidence,
                "details": {
                    "engine": "trocr",
                    "model": "microsoft/trocr-base-printed"
                }
            }
            
        except Exception as e:
            logger.error(f"TrOCR 文字識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "trocr"},
                "error": str(e)
            }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """識別公式（TrOCR 可用於公式但效果有限）"""
        if not self.is_initialized:
            raise RuntimeError("TrOCR 引擎未初始化")
        
        try:
            # 使用相同的文字識別邏輯，但調整置信度
            result = await self.recognize_text(image_path)
            
            # 如果結果看起來像 LaTeX，提高置信度
            text = result.get("text", "")
            if self._looks_like_latex(text):
                result["confidence"] = min(result["confidence"] * 1.2, 0.85)
                result["details"]["note"] = "可能的 LaTeX 公式"
            else:
                result["confidence"] *= 0.7  # 降低非公式內容的置信度
            
            return result
            
        except Exception as e:
            logger.error(f"TrOCR 公式識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "trocr"},
                "error": str(e)
            }
    
    def _estimate_confidence(self, text: str) -> float:
        """估算 TrOCR 結果置信度"""
        if not text or text.strip() == "":
            return 0.0
        
        confidence = 0.6  # 基礎分數
        
        # 長度合理性
        if 5 <= len(text) <= 200:
            confidence += 0.1
        
        # 包含常見字符
        if any(char.isalnum() for char in text):
            confidence += 0.1
        
        # 沒有明顯的識別錯誤
        error_indicators = ['###', '???', '|||']
        if not any(indicator in text for indicator in error_indicators):
            confidence += 0.1
        
        return min(confidence, 0.85)
    
    def _looks_like_latex(self, text: str) -> bool:
        """判斷文字是否像 LaTeX 公式"""
        latex_indicators = [
            "\\frac", "\\sqrt", "\\int", "\\sum", "\\lim",
            "^{", "_{", "\\alpha", "\\beta", "\\pi",
            "\\sin", "\\cos", "\\tan", "\\log"
        ]
        
        return any(indicator in text for indicator in latex_indicators)
    
    async def cleanup(self):
        """清理資源"""
        # TrOCR 模型通常不需要顯式清理
        logger.info("TrOCR 引擎資源已清理")