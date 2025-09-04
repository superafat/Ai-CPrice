"""
影像前處理服務
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
from typing import Tuple, List, Dict
from loguru import logger

from ...config import QUALITY_LEVELS
from ...models.ocr_result import QualityLevel, ImageBlock, BlockType


class ImagePreprocessor:
    """影像前處理器"""
    
    def __init__(self):
        self.temp_dir = "processed"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def preprocess_image(self, image_path: str, target_quality: QualityLevel = QualityLevel.B) -> str:
        """
        影像前處理主流程
        返回處理後的影像路徑
        """
        try:
            # 載入影像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"無法載入影像: {image_path}")
            
            original_shape = image.shape
            logger.info(f"原始影像尺寸: {original_shape}")
            
            # 前處理步驟
            processed = await self._apply_preprocessing(image, target_quality)
            
            # 品質評估
            quality_score = self._assess_quality(processed)
            logger.info(f"處理後品質評分: {quality_score}")
            
            # 儲存處理後影像
            output_path = self._generate_output_path(image_path, target_quality)
            cv2.imwrite(output_path, processed)
            
            return output_path
            
        except Exception as e:
            logger.error(f"影像前處理失敗: {e}")
            raise
    
    async def _apply_preprocessing(self, image: np.ndarray, quality: QualityLevel) -> np.ndarray:
        """應用前處理步驟"""
        
        # 1. 轉灰階
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 2. 去噪
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 3. 對比度增強
        enhanced = self._enhance_contrast(denoised)
        
        # 4. 自適應二值化
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 5. 去陰影
        shadow_free = self._remove_shadows(enhanced)
        
        # 6. 傾斜矯正（如需要）
        corrected = self._correct_skew(shadow_free)
        
        # 7. 尺寸調整（根據品質等級）
        resized = self._resize_for_quality(corrected, quality)
        
        return resized
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """對比度增強"""
        # CLAHE (限制對比度自適應直方圖均衡化)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
    
    def _remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """去除陰影"""
        # 使用形態學操作去除陰影
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        background = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # 計算差值
        diff = cv2.subtract(background, image)
        
        # 正規化
        normalized = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        
        return normalized
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """傾斜矯正"""
        # 使用霍夫變換檢測線條
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # 計算平均角度
            angles = []
            for rho, theta in lines[:10]:  # 只使用前10條線
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # 只有角度偏差超過0.5度才矯正
                    # 旋轉影像
                    center = (image.shape[1] // 2, image.shape[0] // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    corrected = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
                    return corrected
        
        return image
    
    def _resize_for_quality(self, image: np.ndarray, quality: QualityLevel) -> np.ndarray:
        """根據品質等級調整尺寸"""
        height, width = image.shape[:2]
        
        if quality == QualityLevel.A:
            # 高品質：保持原始尺寸
            return image
        elif quality == QualityLevel.B:
            # 中等品質：適度壓縮
            if width > 2000:
                scale = 2000 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        else:  # Quality C
            # 低品質：較大壓縮
            if width > 1200:
                scale = 1200 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        return image
    
    def _assess_quality(self, image: np.ndarray) -> float:
        """評估影像品質"""
        # 計算對比度
        contrast = image.std()
        
        # 計算清晰度 (Laplacian variance)
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        
        # 綜合評分 (0-1)
        contrast_score = min(contrast / 50.0, 1.0)
        sharpness_score = min(laplacian_var / 1000.0, 1.0)
        
        overall_score = (contrast_score + sharpness_score) / 2
        return overall_score
    
    def _generate_output_path(self, original_path: str, quality: QualityLevel) -> str:
        """生成輸出檔案路徑"""
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        output_name = f"{base_name}_processed_{quality.value}.png"
        return os.path.join(self.temp_dir, output_name)


class ImageSegmenter:
    """影像切塊器 - 單題切塊與版面分析"""
    
    def __init__(self):
        pass
    
    async def segment_problems(self, image_path: str) -> List[ImageBlock]:
        """
        將影像切分為單題區塊
        返回區塊列表，每個區塊包含類型、位置、影像路徑
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"無法載入影像: {image_path}")
            
            # 1. 偵測題號
            problem_regions = await self._detect_problem_numbers(image)
            
            # 2. 分析版面結構
            blocks = []
            for i, region in enumerate(problem_regions):
                problem_blocks = await self._analyze_problem_layout(image, region, i)
                blocks.extend(problem_blocks)
            
            # 3. 移除頁眉頁腳與冗餘留白
            cleaned_blocks = await self._clean_layout(blocks)
            
            # 4. 儲存切塊影像
            for block in cleaned_blocks:
                block.image_path = await self._save_block_image(image, block)
                block.original_image_path = image_path
            
            logger.info(f"成功切分 {len(cleaned_blocks)} 個區塊")
            return cleaned_blocks
            
        except Exception as e:
            logger.error(f"影像切塊失敗: {e}")
            raise
    
    async def _detect_problem_numbers(self, image: np.ndarray) -> List[Dict]:
        """偵測題號位置"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 使用輪廓檢測尋找可能的題號區域
        # 這裡簡化實作，實際應該使用更sophisticated的方法
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        problem_regions = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # 過濾太小的區域
            if w * h > 10000:  # 最小面積閾值
                problem_regions.append({
                    "id": i,
                    "bbox": [x, y, x + w, y + h],
                    "area": w * h
                })
        
        # 按位置排序（從上到下，從左到右）
        problem_regions.sort(key=lambda x: (x["bbox"][1], x["bbox"][0]))
        
        return problem_regions
    
    async def _analyze_problem_layout(self, image: np.ndarray, region: Dict, problem_index: int) -> List[ImageBlock]:
        """分析單題的版面結構"""
        x1, y1, x2, y2 = region["bbox"]
        problem_image = image[y1:y2, x1:x2]
        
        blocks = []
        
        # 簡化的版面分析 - 實際應該使用更精確的方法
        height, width = problem_image.shape[:2]
        
        # 假設題幹在上半部
        problem_block = ImageBlock(
            id=f"problem_{problem_index}",
            type=BlockType.PROBLEM,
            bbox=[x1, y1, x2, y1 + height // 2],
            image_path="",  # 稍後填入
            original_image_path="",
            quality_level=QualityLevel.B,
            order_in_document=problem_index * 10
        )
        blocks.append(problem_block)
        
        # 假設選項在下半部
        options_block = ImageBlock(
            id=f"options_{problem_index}",
            type=BlockType.OPTIONS,
            bbox=[x1, y1 + height // 2, x2, y2],
            image_path="",
            original_image_path="",
            quality_level=QualityLevel.B,
            order_in_document=problem_index * 10 + 1
        )
        blocks.append(options_block)
        
        return blocks
    
    async def _clean_layout(self, blocks: List[ImageBlock]) -> List[ImageBlock]:
        """清理版面，移除冗餘區域"""
        # 過濾太小的區塊
        cleaned = []
        for block in blocks:
            x1, y1, x2, y2 = block.bbox
            width = x2 - x1
            height = y2 - y1
            
            # 最小尺寸檢查
            min_width = QUALITY_LEVELS["B"]["min_resolution"] if block.type == BlockType.PROBLEM else 400
            if width >= min_width and height >= 100:
                cleaned.append(block)
        
        return cleaned
    
    async def _save_block_image(self, full_image: np.ndarray, block: ImageBlock) -> str:
        """儲存區塊影像"""
        x1, y1, x2, y2 = block.bbox
        block_image = full_image[y1:y2, x1:x2]
        
        output_path = os.path.join("processed", f"{block.id}.png")
        cv2.imwrite(output_path, block_image)
        
        return output_path


class BlockClassifier:
    """區塊分類器 - 判斷區塊類型（題幹/選項/公式）"""
    
    def __init__(self):
        self.formula_keywords = [
            "\\frac", "\\sqrt", "\\int", "\\sum", "\\lim", "\\alpha", "\\beta", 
            "\\gamma", "\\delta", "\\theta", "\\pi", "\\sin", "\\cos", "\\tan",
            "\\log", "\\ln", "\\exp", "^", "_", "\\cdot", "\\times", "\\div"
        ]
        self.option_patterns = [r"\([A-D]\)", r"[A-D]\."]
    
    async def classify_block(self, block: ImageBlock) -> BlockType:
        """
        分類區塊類型
        使用規則 + 輕量分類模型
        """
        try:
            # 載入區塊影像進行初步分析
            image = cv2.imread(block.image_path, cv2.IMREAD_GRAYSCALE)
            
            # 1. 基於影像特徵的初步判斷
            has_complex_math = self._detect_math_symbols(image)
            has_options = self._detect_option_patterns(image)
            
            # 2. 基於位置的判斷
            position_hint = self._analyze_position(block)
            
            # 3. 綜合判斷
            if has_complex_math:
                return BlockType.FORMULA
            elif has_options:
                return BlockType.OPTIONS
            elif position_hint == "top":
                return BlockType.PROBLEM
            else:
                return BlockType.SOLUTION
                
        except Exception as e:
            logger.error(f"區塊分類失敗: {e}")
            # 預設返回題幹類型
            return BlockType.PROBLEM
    
    def _detect_math_symbols(self, image: np.ndarray) -> bool:
        """檢測數學符號特徵"""
        # 檢測分數線（水平線）
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal_score = cv2.countNonZero(horizontal_lines)
        
        # 檢測根號等曲線
        edges = cv2.Canny(image, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        complex_shapes = 0
        for contour in contours:
            # 計算輪廓複雜度
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) > 6:  # 複雜形狀
                complex_shapes += 1
        
        # 綜合判斷
        return horizontal_score > 100 or complex_shapes > 3
    
    def _detect_option_patterns(self, image: np.ndarray) -> bool:
        """檢測選項模式"""
        # 使用模板匹配檢測 (A) (B) (C) (D) 模式
        # 這裡簡化實作
        height, width = image.shape
        
        # 檢查影像是否有多行結構（選項特徵）
        horizontal_projection = np.sum(image, axis=1)
        peaks = []
        for i in range(1, len(horizontal_projection) - 1):
            if (horizontal_projection[i] > horizontal_projection[i-1] and 
                horizontal_projection[i] > horizontal_projection[i+1]):
                peaks.append(i)
        
        # 如果有3-4個明顯的峰值，可能是選項
        return len(peaks) >= 3 and len(peaks) <= 6
    
    def _analyze_position(self, block: ImageBlock) -> str:
        """分析區塊在文檔中的位置"""
        # 根據 order_in_document 判斷位置
        if block.order_in_document % 10 == 0:
            return "top"  # 題幹通常在最上方
        else:
            return "bottom"  # 其他部分
    
    async def batch_classify(self, blocks: List[ImageBlock]) -> List[ImageBlock]:
        """批次分類所有區塊"""
        classified_blocks = []
        
        for block in blocks:
            block.type = await self.classify_block(block)
            classified_blocks.append(block)
            logger.debug(f"區塊 {block.id} 分類為: {block.type}")
        
        return classified_blocks