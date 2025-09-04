# API 規格文件

## 概述

OCR 數學題目解析系統 API 提供完整的檔案上傳、OCR 處理、內容預覽與 Word 匯出功能。

## 基本資訊

- **Base URL**: `http://localhost:8000/api`
- **認證方式**: Bearer Token（可選）
- **請求格式**: JSON / multipart/form-data
- **回應格式**: JSON

## API 端點

### 1. 檔案上傳

#### POST /upload
上傳圖片或 PDF 檔案進行處理

**請求**:
```http
POST /api/upload
Content-Type: multipart/form-data

file: [檔案]
auto_process: true
```

**回應**:
```json
{
  "task_id": "uuid-string",
  "filename": "problem.jpg",
  "file_size": 1024000,
  "stage": "uploaded",
  "message": "檔案上傳成功，正在處理中..."
}
```

#### GET /upload/status/{task_id}
獲取上傳任務處理狀態

**回應**:
```json
{
  "task_id": "uuid-string",
  "stage": "ocr_processing",
  "progress": 75,
  "total_blocks": 4,
  "successful_blocks": 3,
  "failed_blocks": 0,
  "message": "OCR 識別中"
}
```

### 2. OCR 處理

#### POST /ocr/text
處理文字區塊 OCR

**請求**:
```json
{
  "image_path": "path/to/image.png",
  "block_type": "text",
  "quality_level": "B"
}
```

**回應**:
```json
{
  "success": true,
  "text": "識別的文字內容",
  "confidence": 0.89,
  "confidence_level": "medium",
  "engine_used": "paddleocr",
  "processing_time_ms": 1200,
  "attempts": 2
}
```

#### POST /ocr/formula
處理公式區塊 OCR

**請求**:
```json
{
  "image_path": "path/to/formula.png", 
  "block_type": "formula",
  "quality_level": "B"
}
```

**回應**:
```json
{
  "success": true,
  "latex": "\\frac{x^2 + 1}{2x}",
  "confidence": 0.92,
  "confidence_level": "high",
  "engine_used": "pix2tex",
  "is_compilable": true,
  "processing_time_ms": 2100,
  "attempts": 1
}
```

#### POST /ocr/retry
重試失敗的區塊處理

**請求**:
```json
{
  "task_id": "uuid-string",
  "block_id": "block_123",
  "use_high_quality": true,
  "force_emergency_engine": false
}
```

#### POST /validate/latex
驗證 LaTeX 語法

**請求**:
```json
{
  "latex_text": "\\frac{x^2}{y}"
}
```

**回應**:
```json
{
  "latex": "\\frac{x^2}{y}",
  "is_valid": true,
  "message": "LaTeX 語法正確"
}
```

### 3. 內容匯出

#### POST /export/word
匯出單一任務為 Word 文檔

**請求**:
```json
{
  "task_id": "uuid-string",
  "export_settings": {
    "problem_font_size": 11,
    "solution_font_size": 9,
    "include_figure_captions": true,
    "image_max_width_cm": 14.0,
    "maintain_aspect_ratio": true,
    "anchor_images_inline": true
  }
}
```

**回應**:
```json
{
  "task_id": "uuid-string",
  "output_file": "outputs/uuid-string.docx",
  "file_size": 2048000,
  "export_settings": { ... },
  "omml_validation": {
    "total_formulas": 5,
    "omml_formulas": 5,
    "omml_ratio": 1.0,
    "all_formulas_omml": true
  },
  "message": "Word 文檔匯出成功"
}
```

#### POST /export/batch
批次匯出多個任務

**請求**:
```json
{
  "task_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "export_settings": { ... }
}
```

#### GET /export/download/{task_id}
下載生成的 Word 檔案

**回應**: 檔案下載 (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

#### GET /export/preview/{task_id}
預覽標準化內容

**回應**:
```json
{
  "task_id": "uuid-string",
  "markdown_content": "## 題目\n...",
  "preview_url": "/api/export/preview/render/uuid-string",
  "message": "預覽內容已生成"
}
```

### 4. 系統管理

#### GET /management/stats
獲取系統統計資料

**回應**:
```json
{
  "total_requests": 1250,
  "success_rate": 95.2,
  "fallback_usage_rate": 12.3,
  "emergency_usage_rate": 3.1,
  "mathpix_daily_usage": 45,
  "mathpix_remaining": 55,
  "average_processing_time": 4.2
}
```

#### GET /management/dashboard
獲取儀表板資料

**回應**:
```json
{
  "overview": {
    "total_requests_today": 156,
    "success_rate": 95.2,
    "average_processing_time": 4.2,
    "active_tasks": 3
  },
  "ocr_performance": {
    "text_ocr_success": 96.5,
    "formula_ocr_success": 89.2,
    "fallback_usage": 12.3,
    "emergency_usage": 3.1
  },
  "resource_usage": {
    "mathpix_quota_used": 45,
    "mathpix_quota_limit": 100,
    "disk_usage_mb": 1250.5,
    "memory_usage_mb": 890.2
  }
}
```

#### POST /management/error-report
提交錯誤回報

**請求**:
```json
{
  "task_id": "uuid-string",
  "error_type": "ocr_failure",
  "error_message": "公式識別失敗",
  "user_feedback": "圖片很清晰但識別錯誤",
  "timestamp": "2024-01-01T10:30:00Z"
}
```

#### GET /management/quota/status
獲取配額使用狀態

#### POST /management/quota/reset
重置每日配額

#### POST /management/cleanup
清理舊檔案

## 錯誤處理

### HTTP 狀態碼
- `200`: 成功
- `400`: 請求錯誤（檔案格式不支援、參數錯誤等）
- `404`: 資源不存在（任務不存在等）
- `413`: 檔案過大
- `429`: 請求過於頻繁
- `500`: 伺服器內部錯誤

### 錯誤回應格式
```json
{
  "detail": "錯誤描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T10:30:00Z"
}
```

### 常見錯誤碼
- `FILE_TOO_LARGE`: 檔案超過大小限制
- `UNSUPPORTED_FORMAT`: 不支援的檔案格式
- `OCR_ENGINE_FAILURE`: OCR 引擎處理失敗
- `QUOTA_EXCEEDED`: 配額已用完
- `TASK_NOT_FOUND`: 任務不存在
- `EXPORT_FAILED`: Word 匯出失敗

## 速率限制

- **上傳**: 每分鐘 10 次
- **OCR 處理**: 每分鐘 30 次
- **匯出**: 每分鐘 5 次
- **管理操作**: 每分鐘 20 次

## 檔案大小限制

- **單一檔案**: 最大 50MB
- **支援格式**: JPG, PNG, WebP, PDF
- **建議解析度**: 1200×800 像素以上

## 配額管理

### Mathpix 配額
- **每日限制**: 100 次（可調整）
- **每帳號限制**: 1000 次/月
- **重置時間**: 每日 00:00 UTC

### 兜底策略
1. 主引擎失敗 → 備援引擎
2. 備援引擎失敗 → 高品質重試
3. 仍失敗 → Mathpix 兜底（受配額限制）

## WebSocket 事件（即時更新）

### 連接端點
```
ws://localhost:8000/ws/task/{task_id}
```

### 事件類型
```json
{
  "type": "stage_update",
  "data": {
    "task_id": "uuid-string",
    "stage": "ocr_processing",
    "progress": 60,
    "message": "正在識別第 3 個區塊..."
  }
}
```

```json
{
  "type": "block_completed",
  "data": {
    "block_id": "block_123",
    "success": true,
    "confidence": 0.89,
    "text": "識別結果..."
  }
}
```

## 測試端點

### GET /health
系統健康檢查

### GET /
系統資訊

### POST /test/ocr
測試 OCR 功能（開發環境）