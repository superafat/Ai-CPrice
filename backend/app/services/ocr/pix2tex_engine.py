"""
pix2tex 引擎實作 - 主要用於 LaTeX 公式識別
"""
import asyncio
from typing import Dict, Any
from loguru import logger

try:
    from pix2tex.cli import LatexOCR
except ImportError:
    logger.warning("pix2tex 未安裝，將使用模擬模式")
    LatexOCR = None


class Pix2TexEngine:
    """pix2tex 引擎封裝"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化 pix2tex 模型"""
        try:
            if LatexOCR is None:
                logger.warning("pix2tex 不可用，使用模擬模式")
                self.is_initialized = True
                return
            
            # 在執行緒中載入模型（避免阻塞）
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: LatexOCR()
            )
            self.is_initialized = True
            logger.info("pix2tex 引擎初始化完成")
            
        except Exception as e:
            logger.error(f"pix2tex 初始化失敗: {e}")
            self.is_initialized = False
            raise
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """
        pix2tex 不適合一般文字識別，返回低置信度結果
        """
        return {
            "text": "",
            "confidence": 0.1,
            "details": [],
            "note": "pix2tex 不適用於一般文字識別"
        }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """識別 LaTeX 公式"""
        if not self.is_initialized:
            raise RuntimeError("pix2tex 引擎未初始化")
        
        try:
            if self.model is None:
                # 模擬模式
                return {
                    "text": "\\frac{x^2 + y^2}{2}",
                    "confidence": 0.88,
                    "details": {"engine": "pix2tex_simulation"}
                }
            
            # 在執行緒中執行識別（避免阻塞）
            loop = asyncio.get_event_loop()
            latex_result = await loop.run_in_executor(
                None,
                self.model,
                image_path
            )
            
            if latex_result:
                # 計算置信度（pix2tex 通常不提供置信度，需要自行評估）
                confidence = self._estimate_confidence(latex_result)
                
                return {
                    "text": latex_result,
                    "confidence": confidence,
                    "details": {
                        "engine": "pix2tex",
                        "latex": latex_result
                    }
                }
            else:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "details": {"engine": "pix2tex"}
                }
                
        except Exception as e:
            logger.error(f"pix2tex 公式識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "pix2tex"},
                "error": str(e)
            }
    
    def _estimate_confidence(self, latex_text: str) -> float:
        """估算 LaTeX 結果的置信度"""
        if not latex_text or latex_text.strip() == "":
            return 0.0
        
        confidence = 0.5  # 基礎分數
        
        # 長度加分
        if len(latex_text) > 10:
            confidence += 0.1
        
        # 包含常見 LaTeX 指令加分
        common_commands = ["\\frac", "\\sqrt", "\\sum", "\\int", "^", "_"]
        for cmd in common_commands:
            if cmd in latex_text:
                confidence += 0.1
        
        # 括號平衡檢查
        if latex_text.count('{') == latex_text.count('}'):
            confidence += 0.1
        
        # 沒有明顯錯誤字符
        error_chars = ['?', '|', '@', '#']
        if not any(char in latex_text for char in error_chars):
            confidence += 0.1
        
        return min(confidence, 0.95)  # 最高 0.95
    
    async def cleanup(self):
        """清理資源"""
        if self.model:
            # pix2tex 通常不需要顯式清理
            pass
        logger.info("pix2tex 引擎資源已清理")