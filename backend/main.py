# backend/main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware # 新增导入
from typing import List, Dict, Optional
import asyncio
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# --- 定义统一的搜索结果格式 ---
class SearchResult(BaseModel):
    id: str  # 原始资源在源应用中的唯一ID
    source: str  # 数据来源名称 (e.g., "Jellyfin", "PhotoPrism")
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None # 用于前端显示缩略图
    detail_url: str # 点击后跳转到源应用详情页的完整URL
    type: Optional[str] = None # 类型 (e.g., "movie", "album", "photo", "book", "note")
    # 更多可选字段，例如：tags, authors, duration 等

app = FastAPI(title="AnticlockwiseSearch Backend", version="0.1.0")

# --- CORS 配置开始 ---
# 定义允许跨域请求的源列表
# 在开发环境中，通常是你的前端开发服务器地址
# 在生产环境中，你需要替换为你的实际前端部署域名或 IP
origins = [
    "http://localhost:5173",  # 你的前端开发服务器地址 (Vite 默认)
    "http://127.0.0.1:5173",  # 另一个常见的本地开发地址
    # 以下是你可能在生产环境中需要添加的地址，请根据实际情况取消注释并修改
    # "http://你的NAS_IP",
    # "http://你的自定义域名.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 允许的源列表
    allow_credentials=True,      # 允许发送 cookies 和认证头（如果需要）
    allow_methods=["*"],         # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE等)
    allow_headers=["*"],         # 允许所有请求头
)
# --- CORS 配置结束 ---


# --- 数据源配置 (从环境变量读取) ---
DATA_SOURCE_CONFIGS: Dict[str, dict] = {
    "jellyfin": {
        "enabled": True,
        "api_base_url": os.getenv("JELLYFIN_API_BASE_URL", "http://your-jellyfin-ip:8096"),
        "web_base_url": os.getenv("JELLYFIN_WEB_BASE_URL", "http://your-jellyfin-ip"), # 用于构建跳转URL
        "api_key": os.getenv("JELLYFIN_API_KEY", ""),
        "user_id": os.getenv("JELLYFIN_USER_ID", "") # 替换为你的用户ID
    },
    "photoprism": {
        "enabled": True,
        "api_base_url": os.getenv("PHOTOPRISM_API_BASE_URL", "http://your-photoprism-ip:2342/api/v1"),
        "web_base_url": os.getenv("PHOTOPRISM_WEB_BASE_URL", "http://your-photoprism-ip:2342"),
        "api_key": os.getenv("PHOTOPRISM_API_KEY", "")
    },
    "audiobookshelf": {
        "enabled": False,
        "api_base_url": os.getenv("AUDIOBOOKSHELF_API_BASE_URL", "http://your-audiobookshelf-ip:80/api"),
        "web_base_url": os.getenv("AUDIOBOOKSHELF_WEB_BASE_URL", "http://your-audiobookshelf-ip"),
        "api_key": os.getenv("AUDIOBOOKSHELF_API_KEY", "") # 替换为实际的认证方式
    },
    "calibreweb": {
        "enabled": False,
        "api_base_url": os.getenv("CALIBREWEB_API_BASE_URL", "http://your-calibreweb-ip:8083/api"),
        "web_base_url": os.getenv("CALIBREWEB_WEB_BASE_URL", "http://your-calibreweb-ip:8083"),
        # TODO：// Calibre-Web可能没有简单的API Key，可能需要session管理
    },
    "joplin": {
        "enabled": False,
        "api_base_url": os.getenv("JOPLIN_API_BASE_URL", "http://your-joplin-server-ip:27583"), # 如果你使用Joplin Server
        "web_base_url": os.getenv("JOPLIN_WEB_BASE_URL", "http://your-joplin-server-ip:27583/shares"), # 示例，可能需要调整
        "token": os.getenv("JOPLIN_TOKEN", "")
        # 对于Joplin桌面版，直接从Web调用API会更复杂，可能需要一个代理
    }
}

# --- 数据源适配器接口 (抽象基类) ---
class DataSourceAdapter:
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.api_base_url = config.get("api_base_url")
        self.web_base_url = config.get("web_base_url") # 用于构建跳转URL

    async def search(self, query: str) -> List[SearchResult]:
        """执行搜索并返回标准化结果"""
        raise NotImplementedError

    def _build_detail_url(self, resource_id: str, item_type: Optional[str] = None) -> str:
        """根据资源ID和类型构建跳转到源应用的详情URL"""
        raise NotImplementedError

# --- 实现具体的数据源适配器 ---

class JellyfinAdapter(DataSourceAdapter):
    # 构造函数已经由 DataSourceAdapter 处理了 config, api_base_url, web_base_url
    # 所以这里不需要额外定义 __init__，除非你有 Jellyfin 特定的初始化逻辑

    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            # 确保 api_base_url, api_key, user_id 都已正确加载
            if not self.api_base_url:
                print("JellyfinAdapter: api_base_url is not set for the adapter.")
                return results
            if "api_key" not in self.config or not self.config["api_key"]:
                print("JellyfinAdapter: API key is not set in config.")
                return results
            if "user_id" not in self.config or not self.config["user_id"]:
                print("JellyfinAdapter: User ID is not set in config.")
                return results

            async with httpx.AsyncClient() as client:
                headers = {"X-MediaBrowser-Token": self.config["api_key"]}
                user_id = self.config["user_id"]

                # 定义请求参数
                params = {
                    "searchTerm": query,
                    "Recursive": "true",
                    "IncludeItemTypes": "Movie,Series,Episode,Audio,Photo,Book" # 包含常见类型
                }
                request_url = f"{self.api_base_url}/Users/{user_id}/Items"
                response = await client.get(
                    request_url,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                for item in data.get("Items", []):
                    # 简化映射，实际可能需要更复杂的逻辑来处理不同类型
                    thumbnail_url = None
                    if item.get("ImageTags", {}).get("Primary"):
                        thumbnail_url = f"{self.api_base_url}/Items/{item['Id']}/Images/Primary?quality=90"

                    results.append(SearchResult(
                        id=item["Id"],
                        source="Jellyfin",
                        title=item.get("Name", "Untitled"),
                        description=item.get("Overview"),
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(item["Id"]),
                        type=item.get("Type")
                    ))
        except httpx.HTTPStatusError as e:
            print(f"Jellyfin search failed ({e.request.url}): {e.response.status_code} - {e.response.text}")
            # 在这里也可以打印详细的错误响应体
            if e.response:
                print(f"Jellyfin error response body: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Jellyfin request error: {e}")
        except Exception as e: # 捕获其他所有异常
            print(f"An unexpected error occurred in JellyfinAdapter: {e}")
            
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None) -> str:
        # Jellyfin Web UI 通常在根路径，而非API路径
        return f"{self.web_base_url}/web/index.html#!/details?id={item_id}"

class AudiobookshelfAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            # 确保 api_base_url, api_key 都已正确加载
            if not self.api_base_url:
                print("AudiobookshelfAdapter: api_base_url is not set for the adapter.")
                return results
            if "api_key" not in self.config or not self.config["api_key"]:
                print("AudiobookshelfAdapter: API key is not set in config.")
                return results

            async with httpx.AsyncClient() as client:
                # Audiobookshelf API 认证可能需要 Bearer Token
                headers = {"Authorization": f"Bearer {self.config['api_key']}"}
                response = await client.get(
                    f"{self.api_base_url}/search",
                    params={"query": query},
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                # Audiobookshelf的搜索结果可能包含books, series, artists等
                for item in data.get("books", []):
                    thumbnail_url = f"{self.api_base_url}/items/{item['id']}/cover" if item.get("coverPath") else None
                    results.append(SearchResult(
                        id=item["id"],
                        source="Audiobookshelf",
                        title=item.get("title", "Untitled Audiobook"),
                        description=item.get("description"),
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(item["id"], "book"),
                        type="Audiobook"
                    ))
                # 也可以添加对 series, artists 等的搜索结果处理
        except httpx.HTTPStatusError as e:
            print(f"Audiobookshelf search failed ({e.request.url}): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Audiobookshelf request error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None) -> str:
        if item_type == "book":
            return f"{self.web_base_url}/book/{item_id}"
        # 其他类型如 series 等可在此扩展
        return f"{self.web_base_url}/" # 回退到主页

class PhotoPrismAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            # 确保 api_base_url, api_key 都已正确加载
            if not self.api_base_url:
                print("PhotoPrismAdapter: api_base_url is not set for the adapter.")
                return results

            async with httpx.AsyncClient() as client:
                params = {
                    "q": query,
                    "count": 100,
                    "offset": 0,
                    "merged": True,
                    "country": "",
                    "camera": 0,
                    "lens": 0,
                    "label": "",
                    "latlng": "",
                    "year": 0,
                    "month": 0,
                    "color": "",
                    "order": "newest",
                    "public": True,
                    "quality": 3
                }
                request_url = f"{self.api_base_url}/photos"
                response = await client.get(
                    request_url,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                for photo in data:
                    # --- CHANGE THIS LINE to use 'Hash' ---
                    # PhotoPrism's web UI uses /api/v1/t/<HASH>/public/tile_<SIZE>
                    # We need to get the 'Hash' from the photo object
                    photo_hash = photo.get("Hash")
                    if photo_hash:
                        # Construct the thumbnail URL using the Hash and desired size (e.g., 200 or 500)
                        # We use web_base_url because it already has the base host:port
                        thumbnail_url = f"{self.web_base_url}/api/v1/t/{photo_hash}/public/tile_500"
                    else:
                        # Fallback if Hash is not found (though it should be)
                        thumbnail_url = "" # Or a placeholder image URL
                        print(f"Warning: Photo {photo.get('UID')} has no 'Hash' for thumbnail generation.")

                    results.append(SearchResult(
                        id=photo["UID"],
                        source="PhotoPrism",
                        title=photo.get("Title") or photo.get("FileName", "Untitled Photo"),
                        description=photo.get("Description"),
                        thumbnail_url=thumbnail_url, # Use the newly constructed URL
                        detail_url=self._build_detail_url(photo["Hash"]),
                        type="Photo"
                    ))
        except httpx.HTTPStatusError as e:
            print(f"PhotoPrism search failed ({e.request.url}): {e.response.status_code} - {e.response.text}")
            if e.response:
                print(f"PhotoPrism error response body: {e.response.text}")
        except httpx.RequestError as e:
            print(f"PhotoPrism request error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in PhotoPrismAdapter: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None) -> str:
        return f"{self.web_base_url}/api/v1/dl/{item_id}"

class CalibreWebAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            # 确保 api_base_url 已正确加载
            if not self.api_base_url:
                print("CalibreWebAdapter: api_base_url is not set for the adapter.")
                return results

            async with httpx.AsyncClient() as client:
                # Calibre-Web 简单的搜索API，可能没有复杂的认证
                response = await client.get(
                    f"{self.api_base_url}/books",
                    params={"query": query},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                for book in data.get("books", []): # 返回的数据结构
                    thumbnail_url = f"{self.web_base_url}/get_cover/{book['id']}" if book.get("id") else None
                    results.append(SearchResult(
                        id=str(book["id"]), # Calibre IDs可能是整数
                        source="CalibreWeb",
                        title=book.get("title", "Untitled Book"),
                        description=book.get("description"), # 可能没有或需要从其他API获取
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(str(book["id"])),
                        type="Book"
                    ))
        except httpx.HTTPStatusError as e:
            print(f"CalibreWeb search failed ({e.request.url}): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"CalibreWeb request error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None) -> str:
        return f"{self.web_base_url}/book/{item_id}"


class JoplinAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            # 确保 api_base_url, token 都已正确加载
            if not self.api_base_url:
                print("JoplinAdapter: api_base_url is not set for the adapter.")
                return results
            if "token" not in self.config or not self.config["token"]:
                print("JoplinAdapter: Token is not set in config.")
                return results

            async with httpx.AsyncClient() as client:
                # Joplin Data API 搜索笔记，需要 token
                response = await client.get(
                    f"{self.api_base_url}/notes",
                    params={"token": self.config["token"], "query": query, "fields": "id,title,body"},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                for note in data: # TODO：// 需要验证返回的是笔记列表
                    # Joplin 通常没有直接的web UI详情页，如果使用Joplin Server的Web Clipper，可能需要自定义处理
                    # 这里的detail_url可能指向Joplin Web Clipper或自定义页面
                    results.append(SearchResult(
                        id=note["id"],
                        source="Joplin",
                        title=note.get("title", "Untitled Note"),
                        description=note.get("body", "")[:200] + "..." if note.get("body") else None, # 截断部分内容作为描述
                        # Joplin 通常没有缩略图，除非特殊处理笔记中的图片
                        thumbnail_url=None,
                        detail_url=self._build_detail_url(note["id"]),
                        type="Note"
                    ))
        except httpx.HTTPStatusError as e:
            print(f"Joplin search failed ({e.request.url}): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Joplin request error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None) -> str:
        # Joplin的Web UI跳转通常比较复杂，或者需要Joplin Server的特定共享链接
        # MVP阶段，这里可能只是一个占位符或指向Joplin Server主页
        # 例如，如果Joplin Server支持，可能是 f"{self.web_base_url}/notes/{item_id}"
        return f"{self.web_base_url}/" # 回退到主页，或自定义一个提示页


# 适配器实例列表
ADAPTERS: List[DataSourceAdapter] = [
    JellyfinAdapter(DATA_SOURCE_CONFIGS["jellyfin"]),
    AudiobookshelfAdapter(DATA_SOURCE_CONFIGS["audiobookshelf"]),
    PhotoPrismAdapter(DATA_SOURCE_CONFIGS["photoprism"]),
    CalibreWebAdapter(DATA_SOURCE_CONFIGS["calibreweb"]),
    JoplinAdapter(DATA_SOURCE_CONFIGS["joplin"]),
]

@app.get("/search", response_model=List[SearchResult])
async def unified_search(query: str = Query(..., min_length=1, max_length=100)):
    """
    执行统一搜索，从所有启用的数据源获取结果。
    """
    if not query.strip():
        return []

    tasks = [adapter.search(query) for adapter in ADAPTERS if adapter.enabled]

    # 并发执行所有搜索任务
    # return_exceptions=True 确保即使某个任务失败，其他任务也能继续执行
    results_lists = await asyncio.gather(*tasks, return_exceptions=True) 

    all_results: List[SearchResult] = []
    for res_list in results_lists:
        if isinstance(res_list, Exception):
            # 优雅地处理单个适配器的错误，不影响其他结果
            print(f"Error during search for one adapter: {type(res_list).__name__} - {res_list}")
            continue
        all_results.extend(res_list)

    # TODO: 可以加入简单的结果排序（例如按时间、相关性）或去重逻辑
    return all_results

@app.get("/config")
async def get_config():
    """返回当前数据源配置（用于前端展示，敏感信息请勿直接返回）"""
    # 在实际应用中，这里应该过滤掉敏感信息，只返回公共配置
    display_config = {k: {key: v for key, val in val.items() if key not in ["api_key", "token", "user_id"]} 
                      for k, val in DATA_SOURCE_CONFIGS.items()}
    return display_config

# 可选：如果想在开发阶段本地测试，可以添加一个主函数
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)