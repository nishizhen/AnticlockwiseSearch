# AnticlockwiseSearch

## Welcome to AnticlockwiseSearch\!

AnticlockwiseSearch is a unified search platform designed for home NAS users. Are you tired of switching between PhotoPrism to find photos, Jellyfin for movies, Audiobookshelf for audiobooks, Calibre Web for e-books, or even searching your file system, just to find a specific item? AnticlockwiseSearch aims to solve this by providing a **single, unified search entry point** for all your scattered digital resources on your NAS.

## Some screenshots

![Screenshot 1](https://github.com/nishizhen/AnticlockwiseSearch/blob/main/screenshots/1.png)
![Screenshot 2](https://github.com/nishizhen/AnticlockwiseSearch/blob/main/screenshots/2.png)
![Screenshot 3](https://github.com/nishizhen/AnticlockwiseSearch/blob/main/screenshots/3.png)

## Project Philosophy

We believe your personal digital resources should work for you, not the other way around. AnticlockwiseSearch aims to:

  * **Unify Search Experience:** Provide a clean, intuitive interface where you can enter keywords to search across all integrated services.
  * **Direct Navigation:** Search results link directly to the resource's detail page in the original application, allowing for seamless transitions.
  * **Plugin-Based Extensibility:** Designed to be highly modular and configurable, making it easy to add, remove, or customize data sources based on your needs.
  * **Minimize Redundant Indexing:** Prioritize real-time searching by directly calling existing service APIs, reducing data redundancy and maintenance overhead.

## Supported Data Sources

AnticlockwiseSearch currently supports the following open-source resource management services and file system search:

  * **Jellyfin:** Movies, TV shows, music, and other media content
  * **Audiobookshelf:** Audiobook library
  * **PhotoPrism:** Photo and video management
  * **Calibre Web:** E-book management
  * **File System Search:** Search files and folders in a specified directory(My usage scenario is that there is already an automatic sync folder for OneDrive on the NAS, so this search is for searching files in OneDrive.)

## How to Get Started (For Developers & Users)

AnticlockwiseSearch is built with **FastAPI** for the backend, **Vue 3** for the frontend, and uses **Docker Compose** for containerized deployment.

### 1\. Clone the Repository

```bash
git clone https://github.com/nishizhen/AnticlockwiseSearch.git
cd AnticlockwiseSearch
```

### 2\. Configure the `.env` file

Create a `.env` file in the project root directory to store API addresses and keys for each service. You can copy and modify the provided `.env.example`:

```bash
cp .env.example .env
```

**Be sure to replace these with the actual IP addresses, ports, and API keys/tokens of your services running on your NAS.**

### 3\. Deploy with Docker Compose

Make sure Docker and Docker Compose are installed, then run:

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

MIT License

## Acknowledgements

- [Jellyfin](https://jellyfin.org/)
- [PhotoPrism](https://photoprism.app/)
- [Audiobookshelf](https://www.audiobookshelf.org/)
- [Calibre Web](https://github.com/janeczku/calibre-web)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)