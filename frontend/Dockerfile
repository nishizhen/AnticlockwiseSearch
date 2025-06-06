# frontend/Dockerfile
# 使用 Node.js 作为构建阶段的基础镜像
FROM node:18-alpine as builder

WORKDIR /app

# 复制 package.json 和 lock 文件，并安装依赖
COPY package.json yarn.lock* package-lock.json* ./
RUN npm install --frozen-lockfile

# 复制其余的应用代码
COPY . .

# 构建 Vue 应用
RUN npm run build

# 使用轻量级的 Nginx 镜像来服务静态文件
FROM nginx:alpine

# 复制构建阶段的输出到 Nginx 的默认网页目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置文件 (可选，但推荐用于生产环境)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制启动脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 80

# 使用自定义启动脚本
ENTRYPOINT ["/docker-entrypoint.sh"]