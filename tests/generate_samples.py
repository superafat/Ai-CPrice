#!/usr/bin/env python3
"""
生成測試案例的 .docx 成品樣本
"""
import os
import asyncio
import json
from pathlib import Path
import aiohttp
from loguru import logger

from create_test_samples import TEST_CASES


async def generate_all_samples():
    """生成所有測試案例的 Word 樣本"""
    
    logger.info("開始生成 12 組測試案例的 .docx 樣本")
    
    # 確保樣本目錄存在
    samples_dir = "../samples"
    os.makedirs(samples_dir, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        
        for i, test_case in enumerate(TEST_CASES, 1):
            try:
                logger.info(f"生成樣本 {i}/12: {test_case['name']}")
                
                # 1. 上傳測試檔案
                task_id = await upload_test_file(session, test_case)
                
                # 2. 等待處理完成
                await wait_for_completion(session, task_id)
                
                # 3. 匯出 Word 文檔
                output_file = await export_word_sample(session, task_id, test_case, i)
                
                # 4. 移動到樣本目錄
                sample_filename = f"sample_{i:02d}_{test_case['id']}.docx"
                sample_path = os.path.join(samples_dir, sample_filename)
                
                if os.path.exists(output_file):
                    os.rename(output_file, sample_path)
                    logger.info(f"樣本已生成: {sample_path}")
                else:
                    logger.warning(f"樣本檔案不存在: {output_file}")
                
            except Exception as e:
                logger.error(f"生成樣本 {test_case['name']} 失敗: {e}")
    
    # 生成樣本清單
    await generate_sample_index()
    
    logger.info("所有樣本生成完成")


async def upload_test_file(session, test_case):
    """上傳測試檔案"""
    file_path = f"test_cases/{test_case['file']}"
    
    with open(file_path, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename=test_case['file'])
        data.add_field('auto_process', 'true')
        
        async with session.post("http://localhost:8000/api/upload", data=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["task_id"]
            else:
                raise RuntimeError(f"上傳失敗: {response.status}")


async def wait_for_completion(session, task_id, timeout=60):
    """等待處理完成"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        async with session.get(f"http://localhost:8000/api/upload/status/{task_id}") as response:
            if response.status == 200:
                status = await response.json()
                if status["stage"] == "completed":
                    return True
                elif status["stage"] == "failed":
                    raise RuntimeError(f"處理失敗: {status.get('error', '未知錯誤')}")
        
        await asyncio.sleep(2)
    
    raise RuntimeError("處理超時")


async def export_word_sample(session, task_id, test_case, case_number):
    """匯出 Word 樣本"""
    
    # 根據測試案例調整匯出設定
    export_settings = {
        "problem_font_size": 11,
        "solution_font_size": 9,
        "include_figure_captions": True,
        "image_max_width_cm": 14.0,
        "maintain_aspect_ratio": True,
        "anchor_images_inline": True
    }
    
    # 特殊案例的設定調整
    if case_number == 12:  # 字級切換測試
        export_settings.update({
            "problem_font_size": 12,
            "solution_font_size": 10
        })
    
    export_data = {
        "task_id": task_id,
        "export_settings": export_settings
    }
    
    async with session.post("http://localhost:8000/api/export/word", json=export_data) as response:
        if response.status == 200:
            result = await response.json()
            return result["output_file"]
        else:
            raise RuntimeError(f"匯出失敗: {response.status}")


async def generate_sample_index():
    """生成樣本清單檔案"""
    
    samples_dir = "../samples"
    index_data = {
        "description": "OCR 系統測試案例 Word 樣本",
        "total_samples": 12,
        "generation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "samples": []
    }
    
    # 掃描樣本檔案
    for i, test_case in enumerate(TEST_CASES, 1):
        sample_filename = f"sample_{i:02d}_{test_case['id']}.docx"
        sample_path = os.path.join(samples_dir, sample_filename)
        
        sample_info = {
            "id": test_case["id"],
            "name": test_case["name"],
            "filename": sample_filename,
            "description": test_case["description"],
            "exists": os.path.exists(sample_path),
            "file_size": os.path.getsize(sample_path) if os.path.exists(sample_path) else 0
        }
        
        index_data["samples"].append(sample_info)
    
    # 儲存清單
    index_path = os.path.join(samples_dir, "sample_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"樣本清單已生成: {index_path}")


if __name__ == "__main__":
    import time
    
    # 設定日誌
    logger.add("sample_generation.log")
    
    # 執行樣本生成
    asyncio.run(generate_all_samples())