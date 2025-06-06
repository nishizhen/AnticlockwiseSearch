#!/bin/sh

# 设置默认值
API_BASE_URL=${VITE_API_BASE_URL:-"http://localhost:8000"}

echo "Configuring frontend with API_BASE_URL: $API_BASE_URL"

# 在所有 JS 文件中替换占位符
find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|__API_BASE_URL__|$API_BASE_URL|g" {} \;

echo "Configuration completed"

# 启动 nginx
exec nginx -g "daemon off;"