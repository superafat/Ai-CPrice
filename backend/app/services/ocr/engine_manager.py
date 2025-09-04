"""
OCR 引擎管理器 - 統一管理所有 OCR 引擎
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from loguru import logger
import time

from .paddleocr_engine import PaddleOCREngine
from .tesseract_engine import TesseractEngine
from .doctr_engine import DocTREngine
from .pix2tex_engine import Pix2TexEngine
from .trocr_engine import TrOCREngine
from .mathpix_engine import MathpixEngine
from ...config import settings, OCR_ENGINE_CONFIG
from ...models.ocr_result import OCRResult, ConfidenceLevel


@dataclass
class OCRAttempt:
    """OCR 嘗試記錄"""
    engine: str
    attempt_number: int
    image_quality: str
    start_time: float
    end_time: Optional[float] = None
    confidence: float = 0.0
    result: Optional[str] = None
    is_compilable: bool = False
    error: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


class OCREngineManager:
    """OCR 引擎管理器"""
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "fallback_usage": 0,
            "emergency_usage": 0,
            "mathpix_daily_usage": 0,
        }
    
    async def initialize(self):
        """初始化所有啟用的 OCR 引擎"""
        logger.info("正在初始化 OCR 引擎...")
        
        # 文字 OCR 引擎
        if settings.paddleocr_enabled:
            self.engines["paddleocr"] = PaddleOCREngine()
            await self.engines["paddleocr"].initialize()
            
        if settings.tesseract_enabled:
            self.engines["tesseract"] = TesseractEngine()
            await self.engines["tesseract"].initialize()
            
        if settings.doctr_enabled:
            self.engines["doctr"] = DocTREngine()
            await self.engines["doctr"].initialize()
        
        # 公式 OCR 引擎
        if settings.pix2tex_enabled:
            self.engines["pix2tex"] = Pix2TexEngine()
            await self.engines["pix2tex"].initialize()
            
        if settings.trocr_enabled:
            self.engines["trocr"] = TrOCREngine()
            await self.engines["trocr"].initialize()
            
        if settings.mathpix_enabled and settings.mathpix_app_id:
            self.engines["mathpix"] = MathpixEngine()
            await self.engines["mathpix"].initialize()
        
        logger.info(f"已初始化 {len(self.engines)} 個 OCR 引擎")
    
    async def process_text_block(self, image_path: str, quality_level: str = "B") -> OCRResult:
        """處理文字區塊（題幹/選項）"""
        attempts = []
        
        # 第一輪：主引擎 + 壓縮圖
        primary_engine = OCR_ENGINE_CONFIG["text"]["primary"]
        result = await self._attempt_ocr(
            engine_name=primary_engine,
            image_path=image_path,
            block_type="text",
            quality_level=quality_level,
            attempt_number=1
        )
        attempts.append(result)
        
        if result.confidence >= settings.text_confidence_threshold:
            return OCRResult(
                text=result.result,
                confidence=result.confidence,
                engine_used=primary_engine,
                attempts=attempts,
                is_successful=True
            )
        
        # 第二輪：備援引擎
        for fallback_engine in OCR_ENGINE_CONFIG["text"]["fallback"]:
            if fallback_engine in self.engines:
                result = await self._attempt_ocr(
                    engine_name=fallback_engine,
                    image_path=image_path,
                    block_type="text",
                    quality_level=quality_level,
                    attempt_number=len(attempts) + 1
                )
                attempts.append(result)
                
                if result.confidence >= settings.text_confidence_threshold:
                    self.usage_stats["fallback_usage"] += 1
                    return OCRResult(
                        text=result.result,
                        confidence=result.confidence,
                        engine_used=fallback_engine,
                        attempts=attempts,
                        is_successful=True
                    )
        
        # 第三輪：原圖重試
        if quality_level != "A":
            result = await self._attempt_ocr(
                engine_name=primary_engine,
                image_path=image_path,
                block_type="text",
                quality_level="A",
                attempt_number=len(attempts) + 1
            )
            attempts.append(result)
            
            if result.confidence >= settings.text_confidence_threshold:
                return OCRResult(
                    text=result.result,
                    confidence=result.confidence,
                    engine_used=primary_engine,
                    attempts=attempts,
                    is_successful=True
                )
        
        # 返回最佳結果（即使未達閾值）
        best_attempt = max(attempts, key=lambda x: x.confidence)
        return OCRResult(
            text=best_attempt.result or "",
            confidence=best_attempt.confidence,
            engine_used=best_attempt.engine,
            attempts=attempts,
            is_successful=False
        )
    
    async def process_formula_block(self, image_path: str, quality_level: str = "B") -> OCRResult:
        """處理公式區塊"""
        attempts = []
        
        # 第一輪：主引擎
        primary_engine = OCR_ENGINE_CONFIG["formula"]["primary"]
        result = await self._attempt_ocr(
            engine_name=primary_engine,
            image_path=image_path,
            block_type="formula",
            quality_level=quality_level,
            attempt_number=1
        )
        attempts.append(result)
        
        # 檢查 LaTeX 可編譯性
        if result.result and await self._validate_latex(result.result):
            result.is_compilable = True
            if result.confidence >= settings.formula_confidence_threshold:
                return OCRResult(
                    text=result.result,
                    confidence=result.confidence,
                    engine_used=primary_engine,
                    attempts=attempts,
                    is_successful=True,
                    is_compilable=True
                )
        
        # 第二輪：備援引擎
        for fallback_engine in OCR_ENGINE_CONFIG["formula"]["fallback"]:
            if fallback_engine in self.engines:
                result = await self._attempt_ocr(
                    engine_name=fallback_engine,
                    image_path=image_path,
                    block_type="formula",
                    quality_level=quality_level,
                    attempt_number=len(attempts) + 1
                )
                attempts.append(result)
                
                if result.result and await self._validate_latex(result.result):
                    result.is_compilable = True
                    if result.confidence >= settings.formula_confidence_threshold:
                        self.usage_stats["fallback_usage"] += 1
                        return OCRResult(
                            text=result.result,
                            confidence=result.confidence,
                            engine_used=fallback_engine,
                            attempts=attempts,
                            is_successful=True,
                            is_compilable=True
                        )
        
        # 第三輪：原圖重試
        if quality_level != "A":
            result = await self._attempt_ocr(
                engine_name=primary_engine,
                image_path=image_path,
                block_type="formula",
                quality_level="A",
                attempt_number=len(attempts) + 1
            )
            attempts.append(result)
            
            if result.result and await self._validate_latex(result.result):
                result.is_compilable = True
                if result.confidence >= settings.formula_confidence_threshold:
                    return OCRResult(
                        text=result.result,
                        confidence=result.confidence,
                        engine_used=primary_engine,
                        attempts=attempts,
                        is_successful=True,
                        is_compilable=True
                    )
        
        # 第四輪：Mathpix 兜底（配額保護）
        emergency_engine = OCR_ENGINE_CONFIG["formula"]["emergency"]
        if (emergency_engine and 
            emergency_engine in self.engines and
            self.usage_stats["mathpix_daily_usage"] < settings.mathpix_daily_limit):
            
            result = await self._attempt_ocr(
                engine_name=emergency_engine,
                image_path=image_path,
                block_type="formula",
                quality_level="A",
                attempt_number=len(attempts) + 1
            )
            attempts.append(result)
            self.usage_stats["mathpix_daily_usage"] += 1
            self.usage_stats["emergency_usage"] += 1
            
            if result.result and await self._validate_latex(result.result):
                result.is_compilable = True
                return OCRResult(
                    text=result.result,
                    confidence=result.confidence,
                    engine_used=emergency_engine,
                    attempts=attempts,
                    is_successful=True,
                    is_compilable=True
                )
        
        # 返回最佳可編譯結果
        compilable_attempts = [a for a in attempts if a.is_compilable]
        if compilable_attempts:
            best_attempt = max(compilable_attempts, key=lambda x: x.confidence)
        else:
            best_attempt = max(attempts, key=lambda x: x.confidence)
        
        return OCRResult(
            text=best_attempt.result or "",
            confidence=best_attempt.confidence,
            engine_used=best_attempt.engine,
            attempts=attempts,
            is_successful=best_attempt.is_compilable,
            is_compilable=best_attempt.is_compilable
        )
    
    async def _attempt_ocr(
        self, 
        engine_name: str, 
        image_path: str, 
        block_type: str,
        quality_level: str,
        attempt_number: int
    ) -> OCRAttempt:
        """執行單次 OCR 嘗試"""
        start_time = time.time()
        attempt = OCRAttempt(
            engine=engine_name,
            attempt_number=attempt_number,
            image_quality=quality_level,
            start_time=start_time
        )
        
        try:
            if engine_name not in self.engines:
                raise ValueError(f"引擎 {engine_name} 未啟用或未初始化")
            
            engine = self.engines[engine_name]
            
            if block_type == "text":
                result = await engine.recognize_text(image_path)
            else:  # formula
                result = await engine.recognize_formula(image_path)
            
            attempt.end_time = time.time()
            attempt.result = result.get("text", "")
            attempt.confidence = result.get("confidence", 0.0)
            
            logger.debug(f"OCR 嘗試 {attempt_number}: {engine_name} -> 信心度 {attempt.confidence:.3f}")
            
        except Exception as e:
            attempt.end_time = time.time()
            attempt.error = str(e)
            logger.error(f"OCR 引擎 {engine_name} 失敗: {e}")
        
        return attempt
    
    async def _validate_latex(self, latex_text: str) -> bool:
        """驗證 LaTeX 公式是否可編譯"""
        try:
            # 使用 MathJax 或簡單的語法檢查
            if not latex_text.strip():
                return False
            
            # 基本語法檢查
            open_braces = latex_text.count('{')
            close_braces = latex_text.count('}')
            if open_braces != close_braces:
                return False
            
            # 檢查常見的 LaTeX 指令格式
            forbidden_chars = ['<', '>', '&', '%', '#']
            if any(char in latex_text for char in forbidden_chars):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"LaTeX 驗證失敗: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """獲取使用統計"""
        total = self.usage_stats["total_requests"]
        successful = self.usage_stats["successful_requests"]
        
        return {
            "total_requests": total,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "fallback_rate": (self.usage_stats["fallback_usage"] / total * 100) if total > 0 else 0,
            "emergency_rate": (self.usage_stats["emergency_usage"] / total * 100) if total > 0 else 0,
            "mathpix_daily_usage": self.usage_stats["mathpix_daily_usage"],
            "mathpix_remaining": settings.mathpix_daily_limit - self.usage_stats["mathpix_daily_usage"]
        }
    
    async def cleanup(self):
        """清理資源"""
        logger.info("正在清理 OCR 引擎資源...")
        for engine_name, engine in self.engines.items():
            try:
                if hasattr(engine, 'cleanup'):
                    await engine.cleanup()
            except Exception as e:
                logger.error(f"清理引擎 {engine_name} 時發生錯誤: {e}")


# 全域 OCR 管理器實例
ocr_manager = OCREngineManager()