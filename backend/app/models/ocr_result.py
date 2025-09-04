"""
OCR 結果資料模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ConfidenceLevel(str, Enum):
    """置信度等級"""
    HIGH = "high"      # >= 0.9
    MEDIUM = "medium"  # 0.7-0.9
    LOW = "low"        # < 0.7


class QualityLevel(str, Enum):
    """影像品質等級"""
    A = "A"  # 高品質原圖
    B = "B"  # 中等品質
    C = "C"  # 低品質壓縮圖


class BlockType(str, Enum):
    """區塊類型"""
    PROBLEM = "problem"      # 題幹
    OPTIONS = "options"      # 選項
    FORMULA = "formula"      # 公式
    FIGURE = "figure"        # 圖片
    SOLUTION = "solution"    # 詳解


class ProcessingStage(str, Enum):
    """處理階段"""
    UPLOADED = "uploaded"
    PREPROCESSING = "preprocessing"
    SEGMENTED = "segmented"
    CLASSIFIED = "classified"
    OCR_PROCESSING = "ocr_processing"
    STANDARDIZING = "standardizing"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class OCRAttemptResult(BaseModel):
    """單次 OCR 嘗試結果"""
    engine: str
    attempt_number: int
    image_quality: QualityLevel
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    confidence: float = 0.0
    result: Optional[str] = None
    is_compilable: bool = False
    error: Optional[str] = None


class OCRResult(BaseModel):
    """OCR 最終結果"""
    text: str
    confidence: float
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.LOW)
    engine_used: str
    attempts: List[OCRAttemptResult] = Field(default_factory=list)
    is_successful: bool = False
    is_compilable: bool = False
    processing_time_ms: float = 0.0
    
    def __post_init__(self):
        # 自動計算置信度等級
        if self.confidence >= 0.9:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence >= 0.7:
            self.confidence_level = ConfidenceLevel.MEDIUM
        else:
            self.confidence_level = ConfidenceLevel.LOW


class ImageBlock(BaseModel):
    """影像區塊"""
    id: str
    type: BlockType
    bbox: List[int]  # [x1, y1, x2, y2]
    image_path: str
    original_image_path: str
    quality_level: QualityLevel
    order_in_document: int
    ocr_result: Optional[OCRResult] = None
    manual_correction: Optional[str] = None


class ProcessingTask(BaseModel):
    """處理任務"""
    task_id: str
    original_filename: str
    original_file_path: str
    stage: ProcessingStage = ProcessingStage.UPLOADED
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 處理結果
    blocks: List[ImageBlock] = Field(default_factory=list)
    standardized_markdown: Optional[str] = None
    export_settings: Optional[Dict[str, Any]] = None
    output_file_path: Optional[str] = None
    
    # 統計資訊
    total_blocks: int = 0
    successful_blocks: int = 0
    failed_blocks: int = 0
    total_processing_time_ms: float = 0.0
    
    # 錯誤資訊
    error_message: Optional[str] = None
    failed_at_stage: Optional[ProcessingStage] = None


class ExportSettings(BaseModel):
    """匯出設定"""
    problem_font_size: int = Field(default=11, ge=8, le=16)
    solution_font_size: int = Field(default=9, ge=8, le=16)
    include_figure_captions: bool = True
    image_max_width_cm: float = Field(default=14.0, gt=0, le=20)
    maintain_aspect_ratio: bool = True
    anchor_images_inline: bool = True


class ValidationResult(BaseModel):
    """驗證結果"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)