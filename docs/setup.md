# 系統安裝與運行指引

## 環境需求

### 系統需求
- **作業系統**: Linux (推薦 Ubuntu 20.04+) 或 macOS
- **記憶體**: 至少 4GB RAM (推薦 8GB+)
- **磁碟空間**: 至少 10GB 可用空間
- **網路**: 穩定的網際網路連線（Mathpix API）

### 軟體需求
- Docker 20.10+
- Docker Compose 2.0+
- Git

## 快速啟動

### 1. 下載專案
```bash
git clone <repository-url>
cd ocr-math-system
```

### 2. 環境配置
複製環境變數範本：
```bash
cp .env.example .env
```

編輯 `.env` 檔案，設定必要參數：
```env
# Mathpix API 設定（兜底引擎）
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key
MATHPIX_DAILY_LIMIT=100

# 系統設定
DEBUG=false
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# OCR 引擎開關
PADDLEOCR_ENABLED=true
TESSERACT_ENABLED=true
PIX2TEX_ENABLED=true
TROCR_ENABLED=true
MATHPIX_ENABLED=true
```

### 3. 啟動服務
```bash
# 建置並啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 4. 驗證安裝
開啟瀏覽器訪問：
- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **Celery 監控**: http://localhost:5555

## 手動安裝（開發環境）

### 後端安裝
```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 安裝系統依賴
sudo apt-get install tesseract-ocr tesseract-ocr-chi-tra pandoc

# 啟動服務
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端安裝
```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發服務器
npm run dev
```

### Redis 安裝
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

## 配置說明

### OCR 引擎配置

#### PaddleOCR（主要文字引擎）
- **用途**: 中文文字識別
- **配置**: 自動下載模型，首次啟動較慢
- **記憶體**: ~1GB

#### pix2tex（主要公式引擎）
- **用途**: LaTeX 公式識別
- **配置**: 自動下載模型
- **記憶體**: ~2GB

#### Tesseract（備援文字引擎）
- **用途**: 備援文字識別
- **配置**: 需要安裝中文語言包
- **安裝**: `sudo apt-get install tesseract-ocr-chi-tra`

#### Mathpix（兜底公式引擎）
- **用途**: 高精度公式識別
- **配置**: 需要 API 金鑰
- **限制**: 每日配額限制
- **註冊**: https://mathpix.com/

### 效能調校

#### 記憶體優化
```env
# 限制並發任務數
MAX_CONCURRENT_TASKS=5
MAX_UPLOAD_CONCURRENT=3

# OCR 模型記憶體設定
PADDLEOCR_USE_GPU=false
TORCH_NUM_THREADS=2
```

#### 處理速度優化
```env
# 影像處理參數
MIN_WIDTH_TEXT=1200
MIN_WIDTH_FORMULA=800
DEFAULT_QUALITY_LEVEL=B

# 重試策略
MAX_RETRY_ATTEMPTS=3
TASK_TIMEOUT_SECONDS=300
```

## 故障排除

### 常見問題

#### 1. OCR 引擎初始化失敗
```bash
# 檢查依賴安裝
pip list | grep paddle
pip list | grep torch

# 重新安裝
pip install paddlepaddle paddleocr --force-reinstall
```

#### 2. Pandoc 轉換失敗
```bash
# 檢查 Pandoc 版本
pandoc --version

# 重新安裝
sudo apt-get remove pandoc
sudo apt-get install pandoc
```

#### 3. 前端無法連接後端
```bash
# 檢查後端服務
curl http://localhost:8000/health

# 檢查 CORS 設定
grep CORS_ORIGINS .env
```

#### 4. 記憶體不足
```bash
# 監控記憶體使用
docker stats

# 調整並發設定
# 在 .env 中降低 MAX_CONCURRENT_TASKS
```

### 日誌檢查
```bash
# Docker 環境
docker-compose logs backend
docker-compose logs frontend
docker-compose logs celery_worker

# 檔案日誌
tail -f logs/app.log
```

### 效能監控
```bash
# 系統資源
htop
df -h

# 服務狀態
docker-compose ps
curl http://localhost:8000/management/health
```

## 生產環境部署

### 安全設定
1. 更改預設密鑰
2. 設定防火牆規則
3. 啟用 HTTPS
4. 限制 API 存取

### 效能優化
1. 使用 GPU 加速（如果可用）
2. 配置負載平衡
3. 設定 CDN
4. 資料庫優化

### 監控設定
1. 設定日誌輪替
2. 配置告警通知
3. 效能指標收集
4. 錯誤追蹤

## 備份與維護

### 定期備份
```bash
# 備份上傳檔案
tar -czf backup_uploads_$(date +%Y%m%d).tar.gz uploads/

# 備份輸出檔案
tar -czf backup_outputs_$(date +%Y%m%d).tar.gz outputs/
```

### 定期維護
```bash
# 清理舊檔案（7天前）
curl -X POST http://localhost:8000/api/management/cleanup

# 重置每日配額
curl -X POST http://localhost:8000/api/management/quota/reset
```

## 支援與除錯

如遇問題，請按以下順序檢查：
1. 查看系統健康狀態：http://localhost:8000/health
2. 檢查服務日誌：`docker-compose logs`
3. 驗證環境配置：檢查 `.env` 檔案
4. 測試 OCR 引擎：使用管理介面測試
5. 聯繫技術支援並提供錯誤日誌