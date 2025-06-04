-----

# AnticlockwiseSearch

-----

## 欢迎来到 AnticlockwiseSearch！

AnticlockwiseSearch 是一个为家庭 NAS 用户设计的统一搜索平台。你是否厌倦了在 PhotoPrism 里找照片、在 Jellyfin 里找电影、在 Audiobookshelf 里找有声书、在 Calibre Web 里找电子书，以及在 Joplin 里找笔记时，需要挨个打开应用进行搜索？AnticlockwiseSearch 的目标就是解决这个问题，它提供一个**统一的搜索入口**，让你能从一个地方搜索所有这些分散在 NAS 上的数字资源。

-----

## 项目理念

我们相信，你的个人数字资源应该为你服务，而不是让你花费大量时间去管理和寻找。AnticlockwiseSearch 旨在：

  * **统一搜索体验：** 提供一个简洁直观的界面，输入关键词即可搜索所有已集成的服务。
  * **直接跳转：** 搜索结果会直接链接到对应应用的资源详情页，让你能无缝切换到原始应用。
  * **插件化扩展：** 设计为高度模块化和可配置，方便你根据需求添加、移除或自定义数据源。
  * **避免冗余索引：** 优先通过调用现有服务的 API 进行实时搜索，最大程度减少数据冗余和维护成本。

-----

## 当前支持的 MVP 数据源 (更多即将到来！)

在 MVP (最小可行产品) 阶段，AnticlockwiseSearch 已初步支持以下流行开源资源管理服务：

  * **Jellyfin:** 电影、电视剧、音乐等媒体内容
  * **Audiobookshelf:** 有声书库
  * **PhotoPrism:** 照片和视频管理
  * **Calibre Web:** 电子书管理
  * **Joplin:** 笔记和知识库 (需配合 Joplin Server)

-----

## 如何开始？(为开发者准备)

AnticlockwiseSearch 项目采用 **FastAPI** 作为后端服务，**Vue 3** 作为前端界面，并使用 **Docker Compose** 进行容器化部署。

### **1. 克隆项目**

```bash
git clone https://github.com/nishizhen/AnticlockwiseSearch.git
cd AnticlockwiseSearch
```

### **2. 配置 `.env` 文件**

在项目根目录下创建一个 `.env` 文件，用于存放各个服务的 API 地址和密钥。**请务必替换为你的 NAS 上实际服务的 IP 地址、端口和对应的 API 密钥/Token。**

```env
# .env 文件示例 (请替换为你的实际值)

# Jellyfin 配置
JELLYFIN_API_BASE_URL="http://你的JellyfinIP:8096"
JELLYFIN_WEB_BASE_URL="http://你的JellyfinIP" # 通常是域名或IP，不带8096端口
JELLYFIN_API_KEY="你的JellyfinAPIKey"
JELLYFIN_USER_ID="你的Jellyfin用户ID"

# PhotoPrism 配置
PHOTOPRISM_API_BASE_URL="http://你的PhotoPrismIP:2342/api/v1"
PHOTOPRISM_WEB_BASE_URL="http://你的PhotoPrismIP:2342"
PHOTOPRISM_API_KEY="你的PhotoPrismAPIKey"

# Audiobookshelf 配置
AUDIOBOOKSHELF_API_BASE_URL="http://你的AudiobookshelfIP:1337/api"
AUDIOBOOKSHELF_WEB_BASE_URL="http://你的AudiobookshelfIP:1337"
AUDIOBOOKSHELF_API_KEY="你的AudiobookshelfAPIKey"

# Calibre-Web 配置
CALIBREWEB_API_BASE_URL="http://你的CalibreWebIP:8083/api"
CALIBREWEB_WEB_BASE_URL="http://你的CalibreWebIP:8083"

# Joplin 配置 (如果你使用 Joplin Server)
JOPLIN_API_BASE_URL="http://你的JoplinServerIP:27583"
JOPLIN_WEB_BASE_URL="http://你的JoplinServerIP:27583/shares" # 或其他可访问的笔记共享地址
JOPLIN_TOKEN="你的JoplinPersonalToken"
```

### **3. 使用 Docker Compose 部署 (推荐)**

确保你的系统已安装 Docker 和 Docker Compose。

```bash
docker compose -f docker-compose.build.yml up --build -d # 自己构建
```
或者
```bash
docker compose up -d # 使用dockerhub的镜像
```

  * `--build` 会首次构建镜像或在 Dockerfile/代码更改后重新构建。
  * `-d` 会在后台运行服务。

部署成功后，访问 `http://localhost` (如果 80 端口可用，否则请检查 `docker-compose.build.yml` 中的端口映射) 即可使用 AnticlockwiseSearch。

### **4. 本地开发运行 (无需 Docker)**

如果你想在本地开发环境中运行和调试项目：

#### **后端 (FastAPI)**

1.  **安装 Poetry 和 Python 3.9+：**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    # 配置 PATH，如：export PATH="$HOME/.poetry/bin:$PATH"
    # 安装 Python 3.9+ (例如使用 pyenv)
    ```
2.  **安装依赖：**
    ```bash
    cd backend
    poetry install --no-root
    ```
3.  **运行后端：**
    ```bash
    poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    后端将在 `http://localhost:8000` 运行。

#### **前端 (Vue 3)**

1.  **安装 Node.js (推荐 18+ LTS) 和 npm：**
    ```bash
    # 例如使用 nvm：
    # curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    # nvm install 18 && nvm use 18
    ```
2.  **安装依赖：**
    ```bash
    cd frontend
    npm install
    ```
3.  **运行前端：**
    ```bash
    npm run dev
    ```
    前端将在 `http://localhost:5173` 运行。

-----

## 贡献指南

AnticlockwiseSearch 欢迎所有形式的贡献！我们希望这个项目能成为一个由社区驱动的、不断成长的工具。

### **我们特别欢迎以下类型的贡献：**

  * **新的数据源适配器：** 你有其他 NAS 上常用的开源服务（例如 Grocy, Home Assistant, Gitea, Nextcloud 等）希望集成进来吗？我们非常欢迎你贡献新的适配器代码。
      * 请参考 `backend/main.py` 中现有适配器（如 `JellyfinAdapter`）的实现方式，封装该服务的 API 调用、结果解析和标准化。
      * 确保你的适配器能将搜索结果映射到 `SearchResult` Pydantic 模型。
      * 在 `DATA_SOURCE_CONFIGS` 和 `ADAPTERS` 列表中添加你的新适配器配置和实例。
  * **现有适配器改进：** 优化现有适配器的性能、错误处理或添加更多元数据支持。
  * **前端功能增强：** 改进用户界面、添加结果排序/筛选功能、响应式设计等。
  * **文档改进：** 完善 README、贡献指南或其他技术文档。
  * **Bug 报告与修复：** 发现并报告 Bug，或提交修复它们的 Pull Request。

### **如何贡献代码？**

1.  **Fork** 本仓库。
2.  **创建功能分支** (`git checkout -b feature/your-feature-name`)。
3.  **编写代码** 并进行充分测试。
4.  **提交更改** (`git commit -m 'feat: Add new data source X'`)。
5.  **推送分支** (`git push origin feature/your-feature-name`)。
6.  **提交 Pull Request** 到本仓库的 `main` 分支。

在提交 Pull Request 时，请提供清晰的描述，解释你的更改和新增的功能。我们期待你的加入！

-----

## 许可证

本项目采用 [MIT 许可证](https://www.google.com/search?q=LICENSE) 发布。

-----

**感谢你对 AnticlockwiseSearch 的关注和支持！**