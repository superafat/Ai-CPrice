# OCR 數學題目解析系統 Makefile

.PHONY: help install start stop test clean logs status

help: ## 顯示說明
	@echo "OCR 數學題目解析系統"
	@echo "可用命令:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安裝依賴與初始化
	@echo "📦 安裝系統依賴..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠️  請編輯 .env 設定 Mathpix API"; fi
	@mkdir -p uploads processed outputs logs temp_export samples reports
	@echo "✅ 安裝完成"

start: ## 啟動所有服務
	@echo "🚀 啟動 OCR 系統..."
	@./start.sh

stop: ## 停止所有服務  
	@echo "🛑 停止 OCR 系統..."
	@docker-compose down

restart: stop start ## 重啟服務

test: ## 執行完整測試
	@echo "🧪 執行系統測試..."
	@cd tests && ./run_tests.sh

test-api: ## 僅執行 API 測試
	@echo "🔧 執行 API 測試..."
	@cd tests && python3 test_runner.py

samples: ## 生成測試樣本
	@echo "📄 生成 Word 樣本..."
	@cd tests && python3 generate_samples.py

clean: ## 清理臨時檔案
	@echo "🧹 清理臨時檔案..."
	@rm -rf uploads/* processed/* outputs/* logs/* temp_export/*
	@docker-compose down -v
	@docker system prune -f

logs: ## 查看服務日誌
	@docker-compose logs -f

logs-backend: ## 查看後端日誌
	@docker-compose logs -f backend

logs-frontend: ## 查看前端日誌
	@docker-compose logs -f frontend

status: ## 檢查服務狀態
	@echo "📊 服務狀態:"
	@docker-compose ps
	@echo ""
	@echo "🏥 健康檢查:"
	@curl -s http://localhost:8000/health | jq . || echo "後端服務未響應"
	@curl -s http://localhost:3000 > /dev/null && echo "前端服務正常" || echo "前端服務未響應"

dev-backend: ## 開發模式啟動後端
	@echo "🔧 啟動後端開發服務..."
	@cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## 開發模式啟動前端  
	@echo "🎨 啟動前端開發服務..."
	@cd frontend && npm run dev

build: ## 建置 Docker 映像
	@echo "🏗️  建置 Docker 映像..."
	@docker-compose build

push: ## 推送到容器倉庫
	@echo "📤 推送 Docker 映像..."
	@docker-compose push

deploy: build push ## 建置並推送

backup: ## 備份重要資料
	@echo "💾 備份系統資料..."
	@tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz uploads/ outputs/ logs/ .env

restore: ## 恢復備份（需指定 BACKUP_FILE）
	@echo "🔄 恢復備份..."
	@if [ -z "$(BACKUP_FILE)" ]; then echo "請指定備份檔案: make restore BACKUP_FILE=backup.tar.gz"; exit 1; fi
	@tar -xzf $(BACKUP_FILE)

monitor: ## 開啟監控面板
	@echo "📈 開啟監控面板..."
	@open http://localhost:3000/management || xdg-open http://localhost:3000/management

docs: ## 開啟文檔
	@echo "📚 開啟 API 文檔..."
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs