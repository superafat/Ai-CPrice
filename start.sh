#!/bin/bash

# OCR 數學題目解析系統啟動腳本

echo "🚀 正在啟動 OCR 數學題目解析系統..."

# 檢查 Docker 是否已安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 檢查環境配置檔案
if [ ! -f .env ]; then
    echo "📝 建立環境配置檔案..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 檔案，設定 Mathpix API 金鑰"
    echo "   MATHPIX_APP_ID=your_app_id"
    echo "   MATHPIX_APP_KEY=your_app_key"
fi

# 建立必要目錄
echo "📁 建立必要目錄..."
mkdir -p uploads processed outputs logs temp_export samples reports

# 建立測試樣本
echo "🖼️  建立測試樣本..."
cd tests
python3 create_test_samples.py
cd ..

# 啟動服務
echo "🐳 啟動 Docker 服務..."
docker-compose up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose ps

# 健康檢查
echo "🏥 執行健康檢查..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 後端服務正常"
else
    echo "❌ 後端服務異常"
fi

curl -s http://localhost:3000 > /dev/null  
if [ $? -eq 0 ]; then
    echo "✅ 前端服務正常"
else
    echo "❌ 前端服務異常"
fi

echo ""
echo "🎉 系統啟動完成！"
echo ""
echo "📱 前端界面: http://localhost:3000"
echo "🔧 後端 API: http://localhost:8000"
echo "📚 API 文檔: http://localhost:8000/docs"
echo "🌸 Celery 監控: http://localhost:5555"
echo ""
echo "💡 使用說明:"
echo "   1. 開啟瀏覽器訪問 http://localhost:3000"
echo "   2. 上傳數學題目圖片或 PDF"
echo "   3. 等待 OCR 處理完成"
echo "   4. 預覽並校對識別結果"
echo "   5. 匯出 Word 文檔（包含 OMML 公式）"
echo ""
echo "🧪 執行測試: cd tests && python3 test_runner.py"
echo "🛑 停止服務: docker-compose down"