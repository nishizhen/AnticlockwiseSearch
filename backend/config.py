import os
from dotenv import load_dotenv

load_dotenv()

DATA_SOURCE_CONFIGS = {
    "jellyfin": {
        "enabled": True,
        "api_base_url": os.getenv("JELLYFIN_API_BASE_URL", "http://your-jellyfin-ip:8096"),
        "web_base_url": os.getenv("JELLYFIN_WEB_BASE_URL", "http://your-jellyfin-ip"),
        "api_key": os.getenv("JELLYFIN_API_KEY", ""),
        "user_id": os.getenv("JELLYFIN_USER_ID", "")
    },
    "photoprism": {
        "enabled": True,
        "api_base_url": os.getenv("PHOTOPRISM_API_BASE_URL", "http://your-photoprism-ip:2342/api/v1"),
        "web_base_url": os.getenv("PHOTOPRISM_WEB_BASE_URL", "http://your-photoprism-ip:2342"),
        "api_key": os.getenv("PHOTOPRISM_API_KEY", "")
    },
    "audiobookshelf": {
        "enabled": True,
        "api_base_url": os.getenv("AUDIOBOOKSHELF_API_BASE_URL", "http://your-audiobookshelf-ip:80/api"),
        "web_base_url": os.getenv("AUDIOBOOKSHELF_WEB_BASE_URL", "http://your-audiobookshelf-ip"),
        "username": os.getenv("AUDIOBOOKSHELF_USERNAME", ""),
        "password": os.getenv("AUDIOBOOKSHELF_PASSWORD", "")
    },
    "calibreweb": {
        "enabled": True,
        "api_base_url": os.getenv("CALIBREWEB_API_BASE_URL", "http://your-calibreweb-ip:8083/api"),
        "web_base_url": os.getenv("CALIBREWEB_WEB_BASE_URL", "http://your-calibreweb-ip:8083"),
        "username": os.getenv("CALIBREWEB_USERNAME", ""),
        "password": os.getenv("CALIBREWEB_PASSWORD", "")
    },
    "filesystem": {
        "enabled": True,
        "search_path": os.getenv("FILESYSTEM_SEARCH_PATH", "/data/search_root")
    }
}