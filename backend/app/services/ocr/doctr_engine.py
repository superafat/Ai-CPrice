"""
docTR 引擎實作 - 備援文字識別引擎
"""
import asyncio
from typing import Dict, Any
from loguru import logger

try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
except ImportError:
    logger.warning("docTR 未安裝，將使用模擬模式")
    DocumentFile = None
    ocr_predictor = None


class DocTREngine:
    """docTR 引擎封裝"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化 docTR 模型"""
        try:
            if DocumentFile is None or ocr_predictor is None:
                logger.warning("docTR 不可用，使用模擬模式")
                self.is_initialized = True
                return
            
            # 在執行緒中載入模型
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: ocr_predictor(pretrained=True)
            )
            
            self.is_initialized = True
            logger.info("docTR 引擎初始化完成")
            
        except Exception as e:
            logger.error(f"docTR 初始化失敗: {e}")
            self.is_initialized = False
            raise
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """識別文字內容"""
        if not self.is_initialized:
            raise RuntimeError("docTR 引擎未初始化")
        
        try:
            if self.model is None:
                # 模擬模式
                return {
                    "text": "模擬 docTR 文字識別結果",
                    "confidence": 0.78,
                    "details": {"engine": "doctr_simulation"}
                }
            
            # 載入文檔
            doc = DocumentFile.from_images([image_path])
            
            # 在執行緒中執行識別
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.model,
                doc
            )
            
            # 提取文字和置信度
            text_blocks = []
            confidences = []
            
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            text_blocks.append(word.value)
                            confidences.append(word.confidence)
            
            # 組合結果
            combined_text = ' '.join(text_blocks)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "text": combined_text,
                "confidence": avg_confidence,
                "details": {
                    "engine": "doctr",
                    "word_count": len(text_blocks),
                    "avg_confidence": avg_confidence
                }
            }
            
        except Exception as e:
            logger.error(f"docTR 文字識別失敗: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": {"engine": "doctr"},
                "error": str(e)
            }
    
    async def recognize_formula(self, image_path: str) -> Dict[str, Any]:
        """
        docTR 不適合公式識別，返回低置信度結果
        """
        return {
            "text": "",
            "confidence": 0.1,
            "details": {"engine": "doctr"},
            "note": "docTR 不適用於公式識別"
        }
    
    async def cleanup(self):
        """清理資源"""
        if self.model:
            # docTR 通常不需要顯式清理
            pass
        logger.info("docTR 引擎資源已清理")