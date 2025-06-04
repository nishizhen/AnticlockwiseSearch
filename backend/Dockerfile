# backend/Dockerfile
# 使用官方的 Python 运行时作为父镜像
FROM python:3.9-slim-buster

# 设置容器内的工作目录
WORKDIR /app

# 安装 poetry
RUN pip install poetry

# 复制 pyproject.toml 和 poetry.lock，并安装项目依赖
# 使用 --no-root 避免安装当前项目本身 (因为它还没完全复制)
# 使用 --no-dev 避免安装开发依赖，减小最终镜像大小
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# 复制其余的应用代码
COPY . .

# 暴露 FastAPI 运行的端口
EXPOSE 8000

# 运行 FastAPI 应用
# `poetry run` 确保命令在 Poetry 管理的虚拟环境中执行
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]