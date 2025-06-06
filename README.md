# AnticlockwiseSearch

## Welcome to AnticlockwiseSearch\!

AnticlockwiseSearch is a unified search platform designed for home NAS users. Are you tired of switching between PhotoPrism to find photos, Jellyfin for movies, Audiobookshelf for audiobooks, Calibre Web for e-books, just to search for a specific item? AnticlockwiseSearch aims to solve this by providing a **single, unified search entry point** for all your scattered digital resources on your NAS.

## Project Philosophy

We believe your personal digital resources should work for you, not the other way around. AnticlockwiseSearch aims to:

  * **Unify Search Experience:** Provide a clean, intuitive interface where you can enter keywords to search across all integrated services.
  * **Direct Navigation:** Search results link directly to the resource's detail page in the original application, allowing for seamless transitions.
  * **Plugin-Based Extensibility:** Designed to be highly modular and configurable, making it easy to add, remove, or customize data sources based on your needs.
  * **Minimize Redundant Indexing:** Prioritize real-time searching by directly calling existing service APIs, reducing data redundancy and maintenance overhead.

## Currently Supported MVP Data Sources (More Coming Soon\!)

In its MVP (Minimum Viable Product) stage, AnticlockwiseSearch initially supports the following popular open-source resource management services:

  * **Jellyfin:** Movies, TV shows, music, and other media content
  * **Audiobookshelf:** Audiobook library
  * **PhotoPrism:** Photo and video management
  * **Calibre Web:** E-book management

## How to Get Started (For Developers)

AnticlockwiseSearch is built with **FastAPI** for the backend, **Vue 3** for the frontend, and uses **Docker Compose** for containerized deployment.

### 1\. Clone the Repository

```bash
git clone https://github.com/nishizhen/AnticlockwiseSearch.git
cd AnticlockwiseSearch
```

### 2\. Configure the `.env` file

Create a `.env` file in the project root directory to store API addresses and keys for each service. **Be sure to replace these with the actual IP addresses, ports, and API keys/tokens of your services running on your NAS.**

```env
# Jellyfin 配置
JELLYFIN_API_BASE_URL="http://192.168.1.100:8096" # 替换为你的 Jellyfin API 地址
JELLYFIN_WEB_BASE_URL="http://192.168.1.100"     # 替换为你的 Jellyfin Web UI 地址 (通常是域名或IP，不带8096端口)
JELLYFIN_API_KEY="你的JellyfinAPIKey"            # 在 Jellyfin 仪表板 -> API 密钥中创建
JELLYFIN_USER_ID="你的Jellyfin用户ID"            # 在 Jellyfin 用户设置中查找

# PhotoPrism 配置
PHOTOPRISM_API_BASE_URL="http://192.168.1.101:2342/api/v1" # 替换为你的 PhotoPrism API 地址
PHOTOPRISM_WEB_BASE_URL="http://192.168.1.101:2342"      # 替换为你的 PhotoPrism Web UI 地址
PHOTOPRISM_API_KEY="你的PhotoPrismAPIKey"        # 在 PhotoPrism 设置 -> 高级 -> API 中查找, 如果是无用户和密码的，可以忽略这个配置

# Audiobookshelf 配置
AUDIOBOOKSHELF_API_BASE_URL="http://192.168.1.102:1337/api" # 替换为你的 Audiobookshelf API 地址
AUDIOBOOKSHELF_WEB_BASE_URL="http://192.168.1.102:1337"   # 替换为你的 Audiobookshelf Web UI 地址
AUDIOBOOKSHELF_USERNAME="你的Audiobookshelf用户名" # 替换为你的ABS登录用户名
AUDIOBOOKSHELF_PASSWORD="你的Audiobookshelf密码"   # 替换为你的ABS登录密码

# Calibre-Web 配置
CALIBREWEB_API_BASE_URL="http://192.168.1.103:8083/api" # 替换为你的 Calibre-Web API 地址 (如果存在)
CALIBREWEB_WEB_BASE_URL="http://192.168.1.103:8083"   # 替换为你的 Calibre-Web Web UI 地址
CALIBREWEB_USERNAME="your_calibreweb_username" # 替换为你的登录用户名
CALIBREWEB_PASSWORD="your_calibreweb_password" # 替换为你的登录密码

```

### 3\. Deploy with Docker Compose (Recommended)

Ensure Docker and Docker Compose are installed on your system.

```bash
docker compose -f docker-compose.build.yml up --build -d # self build
```
or
```bash
docker compose up -d # use dockerhub images
```

  * `--build` will build images for the first time or after changes to Dockerfiles/code.
  * `-d` runs services in the background.

Once deployed successfully, visit `http://localhost` (if port 80 is available; otherwise, check your `docker-compose.build.yml` for port mappings) to use AnticlockwiseSearch.

### 4\. Local Development Run (Without Docker)

If you prefer to run and debug the project in your local development environment without Docker:

#### Backend (FastAPI)

1.  **Install Poetry and Python 3.9+:**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    # Configure PATH, e.g.: export PATH="$HOME/.poetry/bin:$PATH"
    # Install Python 3.9+ (e.g., using pyenv)
    ```
2.  **Install Dependencies:**
    ```bash
    cd backend
    poetry install --no-root
    ```
3.  **Run Backend:**
    ```bash
    poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will run on `http://localhost:8000`.

#### Frontend (Vue 3)

1.  **Install Node.js (Recommended 18+ LTS) and npm:**
    ```bash
    # For example, using nvm:
    # curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    # nvm install 18 && nvm use 18
    ```
2.  **Install Dependencies:**
    ```bash
    cd frontend
    npm install
    ```
3.  **Run Frontend:**
    ```bash
    npm run dev
    ```
    The frontend will run on `http://localhost:5173`.


## Contribution Guide

AnticlockwiseSearch welcomes contributions in all forms\! We hope this project becomes a community-driven, ever-growing tool.

### We particularly welcome the following types of contributions:

  * **New Data Source Adapters:** Do you have other commonly used open-source services on your NAS (e.g., Grocy, Home Assistant, Gitea, Nextcloud, etc.) that you'd like to integrate? We highly encourage you to contribute new adapter code.
      * Please refer to the existing adapters in `backend/main.py` (e.g., `JellyfinAdapter`) to understand how to encapsulate API calls, parse results, and standardize them for the new service.
      * Ensure your adapter maps search results to the `SearchResult` Pydantic model.
      * Add your new adapter's configuration and instance to the `DATA_SOURCE_CONFIGS` and `ADAPTERS` lists.
  * **Improvements to Existing Adapters:** Optimize performance, enhance error handling, or add more metadata support to existing adapters.
  * **Frontend Feature Enhancements:** Improve the user interface, add result sorting/filtering capabilities, responsive design, etc.
  * **Bug Reports and Fixes:** Discover and report bugs, or submit Pull Requests to fix them.

### How to Contribute Code?

1.  **Fork** this repository.
2.  **Create a feature branch** (`git checkout -b feature/your-feature-name`).
3.  **Write your code** and thoroughly test it.
4.  **Commit your changes** (`git commit -m 'feat: Add new data source X'`).
5.  **Push your branch** (`git push origin feature/your-feature-name`).
6.  **Submit a Pull Request** to the `main` branch of this repository.

When submitting a Pull Request, please provide a clear description explaining your changes and new features. We look forward to your contributions\!

## License

This project is released under the [MIT License](https://www.google.com/search?q=LICENSE).

**Thank you for your interest and support in AnticlockwiseSearch\!**