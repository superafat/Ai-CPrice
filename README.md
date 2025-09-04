# 題解上傳 OCR 標準化系統

完整的Web服務，支援上傳物理/數學題目圖檔或PDF，自動進行OCR識別並產出包含OMML公式的Word文檔。

## 功能特色
- 影像前處理與單題切塊
- 雙引擎OCR（文字+公式）
- 標準化為Markdown+LaTeX  
- 匯出Word文檔（OMML公式）
- 行動優先設計
- 字體大小與版面設定

## 技術架構
- 後端: Python + FastAPI + Celery
- 前端: React + Vite + Tailwind CSS
- OCR引擎: PaddleOCR, pix2tex, Tesseract, TrOCR, Mathpix
- 文檔轉換: Pandoc (LaTeX → OMML)

## 專案結構
```
/
├── backend/          # FastAPI 後端服務
├── frontend/         # React 前端應用  
├── docs/            # 規格文件與指引
├── tests/           # 測試案例與腳本
├── samples/         # 輸出樣本
└── docker-compose.yml
```