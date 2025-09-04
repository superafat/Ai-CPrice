FROM node:18-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package files
COPY package*.json ./

# 安裝依賴
RUN npm ci --only=production

# 複製原始碼
COPY . .

# 建置應用
RUN npm run build

# 使用 nginx 提供靜態檔案
FROM nginx:alpine

# 複製建置結果
COPY --from=0 /app/dist /usr/share/nginx/html

# 複製 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 3000

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]