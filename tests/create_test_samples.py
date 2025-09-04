#!/usr/bin/env python3
"""
建立測試樣本檔案
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def create_mock_test_images():
    """建立模擬測試圖片"""
    
    # 確保目錄存在
    os.makedirs("test_cases", exist_ok=True)
    os.makedirs("expected_outputs", exist_ok=True)
    
    # 測試案例資料
    test_cases = [
        {
            "file": "clear_chinese_problem.jpg",
            "content": "求解方程式 x² + 2x + 1 = 0\n(A) x = -1\n(B) x = 1\n(C) x = 0\n(D) 無解",
            "quality": "high"
        },
        {
            "file": "dark_chinese_problem.jpg", 
            "content": "計算積分 ∫(x² + 1)dx\n(A) x³/3 + x + C\n(B) x³ + x + C\n(C) 2x + C\n(D) x² + C",
            "quality": "low"
        },
        {
            "file": "multiple_formulas.jpg",
            "content": "已知 f(x) = sin(x) + cos(x)\n求 f'(x) = ?\n解: f'(x) = cos(x) - sin(x)",
            "quality": "medium"
        },
        {
            "file": "handwritten_formula.jpg",
            "content": "√(x² + y²) = r\n其中 x = r·cos(θ), y = r·sin(θ)",
            "quality": "medium"
        },
        {
            "file": "skewed_image.jpg",
            "content": "三角函數恆等式\nsin²(x) + cos²(x) = 1\ntan(x) = sin(x)/cos(x)",
            "quality": "medium"
        }
    ]
    
    for i, case in enumerate(test_cases):
        create_test_image(case, i + 1)
    
    # 建立預期輸出
    create_expected_outputs()


def create_test_image(case_data: dict, case_number: int):
    """建立單一測試圖片"""
    
    # 圖片尺寸
    width = 800 if case_data["quality"] == "low" else 1200
    height = 600 if case_data["quality"] == "low" else 900
    
    # 建立白色背景
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        # 嘗試載入字體（可能不存在）
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        # 使用預設字體
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # 添加題號
    draw.text((50, 50), f"{case_number}.", fill='black', font=font_large)
    
    # 添加內容
    lines = case_data["content"].split('\n')
    y_pos = 100
    
    for line in lines:
        draw.text((50, y_pos), line, fill='black', font=font_medium)
        y_pos += 40
    
    # 根據品質等級調整
    if case_data["quality"] == "low":
        # 降低對比度模擬偏暗圖片
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.7)
    elif case_data["quality"] == "medium":
        # 添加輕微模糊
        image = image.filter(ImageFilter.BLUR)
    
    # 儲存圖片
    output_path = f"test_cases/{case_data['file']}"
    image.save(output_path, 'JPEG', quality=85)
    
    print(f"已建立測試圖片: {output_path}")


def create_expected_outputs():
    """建立預期輸出檔案"""
    
    expected_results = {
        "test_01": {
            "markdown": """## 題目
求解方程式 x² + 2x + 1 = 0

### 選項
(A) x = -1
(B) x = 1  
(C) x = 0
(D) 無解

### 解析
$$x^2 + 2x + 1 = (x + 1)^2 = 0$$
因此 $x = -1$，答案是 (A)。""",
            "expected_confidence": 0.95,
            "expected_blocks": 3
        },
        
        "test_02": {
            "markdown": """## 題目
計算積分 ∫(x² + 1)dx

### 選項
(A) x³/3 + x + C
(B) x³ + x + C
(C) 2x + C  
(D) x² + C

### 解析
$$\\int (x^2 + 1) dx = \\frac{x^3}{3} + x + C$$
答案是 (A)。""",
            "expected_confidence": 0.85,
            "expected_blocks": 3
        }
    }
    
    # 儲存預期結果
    with open("expected_outputs/expected_results.json", 'w', encoding='utf-8') as f:
        json.dump(expected_results, f, ensure_ascii=False, indent=2)
    
    print("已建立預期輸出檔案")


if __name__ == "__main__":
    print("正在建立測試樣本...")
    create_mock_test_images()
    print("測試樣本建立完成")


from PIL import ImageEnhance, ImageFilter