#!/usr/bin/env python3
"""
建立簡化的測試樣本檔案（不依賴 PIL）
"""
import os
import json


def create_mock_test_files():
    """建立模擬測試檔案"""
    
    # 確保目錄存在
    os.makedirs("test_cases", exist_ok=True)
    os.makedirs("expected_outputs", exist_ok=True)
    
    # 建立最小的 JPEG 檔案標頭
    jpeg_header = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xC0, 0x00, 0x11,
        0x08, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11,
        0x01, 0x03, 0x11, 0x01, 0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x08, 0xFF, 0xC4, 0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0xFF, 0xDA, 0x00, 0x0C, 0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00,
        0x3F, 0x00, 0xB2, 0xC0, 0x07, 0xFF, 0xD9
    ])
    
    # 測試案例清單
    test_files = [
        "clear_chinese_problem.jpg",
        "dark_chinese_problem.jpg", 
        "multiline_options.jpg",
        "multiple_formulas.jpg",
        "handwritten_formula.jpg",
        "skewed_image.jpg",
        "two_problems.jpg",
        "compressed_image.jpg",
        "formula_with_typos.jpg",
        "complex_formula.jpg",
        "problem_with_images.jpg",
        "long_problem_two_images.jpg"
    ]
    
    # 建立測試檔案
    for filename in test_files:
        file_path = f"test_cases/{filename}"
        with open(file_path, 'wb') as f:
            f.write(jpeg_header)
            # 添加一些隨機資料讓檔案大小不同
            f.write(b'\x00' * (1000 + len(filename) * 100))
        
        print(f"已建立測試檔案: {file_path}")
    
    # 建立預期輸出
    expected_results = {}
    
    for i, filename in enumerate(test_files, 1):
        test_id = f"test_{i:02d}"
        expected_results[test_id] = {
            "filename": filename,
            "expected_blocks": 3 + (i % 3),  # 3-5 個區塊
            "expected_confidence": 0.8 + (i % 20) / 100,  # 0.8-0.99
            "expected_processing_time": 3.0 + (i % 10) / 10,  # 3-4 秒
            "contains_formulas": i in [4, 5, 9, 10, 11, 12],
            "contains_images": i in [11, 12],
            "description": f"測試案例 {i}: {filename}"
        }
    
    # 儲存預期結果
    with open("expected_outputs/expected_results.json", 'w', encoding='utf-8') as f:
        json.dump(expected_results, f, ensure_ascii=False, indent=2)
    
    print(f"已建立 {len(test_files)} 個測試檔案")
    print("已建立預期輸出檔案: expected_outputs/expected_results.json")


if __name__ == "__main__":
    print("正在建立簡化測試樣本...")
    create_mock_test_files()
    print("測試樣本建立完成")