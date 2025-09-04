# OCR 處理流程規格

## 流程概述

OCR 處理採用九段式流程，確保高準確率與可追溯性：

1. **檔案上傳與驗證**
2. **影像前處理**
3. **單題切塊與版面分析**
4. **區塊分類與路由**
5. **雙引擎 OCR 處理**
6. **置信度檢查與重試**
7. **LaTeX 可編譯驗證**
8. **內容標準化**
9. **Word 匯出與 OMML 轉換**

## 詳細流程規格

### 第一段：檔案上傳與驗證

#### 輸入驗證
- **檔案格式**: JPG, PNG, WebP, PDF
- **檔案大小**: ≤ 50MB
- **解析度**: 建議 ≥ 1200×800 像素

#### 安全檢查
- 檔案類型驗證（Magic Number）
- 惡意內容掃描
- 檔案完整性檢查

#### 輸出
- 任務 ID
- 原始檔案路徑
- 檔案元資料

### 第二段：影像前處理

#### 處理步驟
1. **色彩轉換**: RGB → 灰階
2. **去噪處理**: 快速非局部平均去噪
3. **對比度增強**: CLAHE 自適應直方圖均衡
4. **二值化**: 自適應閾值二值化
5. **去陰影**: 形態學背景減除
6. **傾斜矯正**: 霍夫變換檢測與矯正
7. **尺寸調整**: 依品質等級調整

#### 品質等級定義
```python
QUALITY_LEVELS = {
    "A": {  # 高品質原圖
        "min_resolution": 2000,
        "min_contrast": 0.8,
        "noise_level": "low",
        "compression": None
    },
    "B": {  # 中等品質
        "min_resolution": 1200, 
        "min_contrast": 0.6,
        "noise_level": "medium",
        "compression": 0.8
    },
    "C": {  # 低品質壓縮圖
        "min_resolution": 800,
        "min_contrast": 0.4, 
        "noise_level": "high",
        "compression": 0.6
    }
}
```

#### 輸出
- 處理後影像路徑
- 品質評分 (0-1)
- 處理參數記錄

### 第三段：單題切塊與版面分析

#### 版面檢測
1. **題號偵測**: 輪廓分析 + 位置規律
2. **區域分割**: 基於題號位置分割題目區域
3. **結構分析**: 識別題幹、選項、公式、圖片區域
4. **邊界清理**: 移除頁眉、頁腳、冗餘留白

#### 切塊規則
- **最小區域**: 題幹 ≥ 1200px 寬，公式 ≥ 800px 寬
- **強制單題**: 一個輸出檔案對應一個題目
- **保留原圖**: 永遠保留原始影像供重試

#### 輸出
- 區塊清單（ID、類型、邊界框、影像路徑）
- 版面分析結果
- 區塊排序資訊

### 第四段：區塊分類與路由

#### 分類規則
```python
# 公式特徵關鍵字
FORMULA_KEYWORDS = [
    "\\frac", "\\sqrt", "\\int", "\\sum", "\\lim", 
    "^", "_", "\\alpha", "\\beta", "\\gamma"
]

# 選項模式
OPTION_PATTERNS = [r"\([A-D]\)", r"[A-D]\."]

# 題幹指示詞
PROBLEM_INDICATORS = ["題", "問", "求", "計算", "證明"]
```

#### 分類策略
1. **規則匹配**: 基於關鍵字和模式
2. **影像特徵**: 檢測數學符號、分數線、根號
3. **位置分析**: 基於在文檔中的位置
4. **輕量模型**: 機器學習輔助分類

#### 目標準確率
- 分類錯誤率 < 3%
- 低信心時雙引擎並行處理

### 第五段：雙引擎 OCR 處理

#### 引擎配置
```python
OCR_ENGINES = {
    "text": {
        "primary": "paddleocr",     # 中文文字主引擎
        "fallback": ["tesseract", "doctr"]  # 備援引擎
    },
    "formula": {
        "primary": "pix2tex",      # LaTeX 公式主引擎
        "fallback": ["trocr"],     # 備援引擎
        "emergency": "mathpix"     # 兜底引擎（配額保護）
    }
}
```

#### 處理策略
1. **主引擎處理**: 使用對應的主要引擎
2. **置信度檢查**: 文字 ≥ 0.8，公式 ≥ 0.7
3. **備援觸發**: 主引擎失敗或置信度不足
4. **並行處理**: 低信心時同時使用多引擎

### 第六段：置信度檢查與重試

#### 重試策略（3輪升級）
```
第 1 輪: 壓縮圖 + 主引擎
   ↓ 失敗
第 2 輪: 壓縮圖 + 備援引擎  
   ↓ 失敗
第 3 輪: 原圖 + 主引擎
   ↓ 失敗
第 4 輪: Mathpix 兜底（僅公式，受配額保護）
```

#### 升級條件
- 置信度低於閾值
- OCR 結果為空
- LaTeX 無法編譯（僅公式）

#### 保護機制
- 最大重試次數: 5 次
- 任務超時: 5 分鐘
- 兜底配額: 每日 100 次

### 第七段：LaTeX 可編譯驗證

#### 驗證規則
```python
def validate_latex(text):
    # 1. 基本語法檢查
    if text.count('{') != text.count('}'):
        return False
    
    # 2. 禁用字符檢查
    forbidden = ['<', '>', '&', '%', '#']
    if any(char in text for char in forbidden):
        return False
    
    # 3. 常見指令格式檢查
    # 4. MathJax/KaTeX 渲染測試
    
    return True
```

#### 重試機制
- 無法編譯 → 觸發備援引擎
- 備援仍失敗 → 啟用兜底引擎
- 記錄編譯失敗原因

### 第八段：內容標準化

#### 輸出格式
```markdown
## 題目
題幹內容...

$$公式內容$$

### 選項
(A) 選項 A
(B) 選項 B  
(C) 選項 C
(D) 選項 D

### 解析
詳解內容...

$行內公式$
```

#### 標準化規則
- 選項統一為 `(A)(B)(C)(D)` 格式
- 公式統一使用 LaTeX 語法
- 清理多餘換行與空白
- 語義標記（problem, options, solution）

### 第九段：Word 匯出與 OMML 轉換

#### 轉換流程
```
Markdown + LaTeX
    ↓ Pandoc --mathml
Word (.docx) + OMML 公式
    ↓ 後處理
最終 Word 文檔
```

#### OMML 轉換
- 使用 Pandoc `--mathml` 選項
- LaTeX → MathML → OMML
- 確保公式可在 Word 中編輯

#### 段落樣式
- `CCH-Problem`: 題幹樣式
- `CCH-Options`: 選項樣式  
- `CCH-Solution`: 詳解樣式

## 日誌與遙測

### 逐張記錄
每張影像處理記錄以下資訊：
```json
{
  "task_id": "uuid",
  "image_id": "block_123",
  "original_size": [1920, 1080],
  "processed_size": [1200, 675],
  "compression_ratio": 0.8,
  "quality_level": "B",
  "attempts": [
    {
      "attempt": 1,
      "engine": "paddleocr",
      "confidence": 0.85,
      "processing_time_ms": 1200,
      "is_compilable": true,
      "success": true
    }
  ],
  "final_result": {
    "text": "識別結果",
    "confidence": 0.85,
    "engine_used": "paddleocr",
    "total_time_ms": 1200
  },
  "failure_reason": null
}
```

### 彙總統計
```json
{
  "daily_stats": {
    "total_requests": 156,
    "successful_requests": 149,
    "success_rate": 95.5,
    "average_processing_time": 4.2,
    "retry_rate": 15.4,
    "fallback_usage_rate": 12.3,
    "emergency_usage_rate": 3.1
  },
  "engine_performance": {
    "paddleocr": {"requests": 120, "success_rate": 96.7},
    "pix2tex": {"requests": 89, "success_rate": 91.0},
    "tesseract": {"requests": 18, "success_rate": 83.3},
    "mathpix": {"requests": 5, "success_rate": 100.0}
  },
  "failure_analysis": [
    {"reason": "影像品質過低", "count": 4, "percentage": 57.1},
    {"reason": "公式過於複雜", "count": 2, "percentage": 28.6},
    {"reason": "文字模糊不清", "count": 1, "percentage": 14.3}
  ]
}
```

## 效能基準

### 處理時間目標
- **單題總處理時間**: ≤ 6 秒
- **影像前處理**: ≤ 1 秒
- **OCR 識別**: ≤ 3 秒
- **標準化**: ≤ 0.5 秒
- **Word 匯出**: ≤ 1.5 秒

### 準確率目標
- **整體成功率**: ≥ 95%
- **文字識別準確率**: ≥ 96%
- **公式識別準確率**: ≥ 89%
- **LaTeX 可編譯率**: ≥ 98%

### 資源使用目標
- **兜底引擎使用率**: ≤ 5%
- **重試率**: ≤ 20%
- **記憶體使用**: ≤ 2GB per worker
- **磁碟空間**: 定期清理，保持 ≥ 5GB 可用

## 故障處理

### 引擎故障
- 自動切換備援引擎
- 記錄故障時間與原因
- 管理員告警通知

### 配額耗盡
- 停用兜底引擎
- 降級處理策略
- 使用者友善提示

### 系統過載
- 任務佇列管理
- 自動限流
- 優雅降級服務