import httpx
import asyncio
from typing import List, Optional
from models.search_result import SearchResult
from .base import DataSourceAdapter

class AudiobookshelfAdapter(DataSourceAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.username = config.get("username")
        self.password = config.get("password")
        self.session_token: Optional[str] = None
        self.token_lock = asyncio.Lock()

    async def _login(self) -> bool:
        if not self.username or not self.password or not self.web_base_url:
            print("AudiobookshelfAdapter: Username, password, or Web base URL is not set for login.")
            return False

        login_url = f"{self.web_base_url}/login"
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    login_url,
                    json=payload,
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
                if "user" in data and "token" in data["user"]:
                    self.session_token = data["user"]["token"]
                    self.default_library_id = data.get("userDefaultLibraryId")
                    return True
                else:
                    self.session_token = None
                    return False
        except Exception as e:
            print(f"AudiobookshelfAdapter login error: {e}")
            self.session_token = None
            return False

    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []

        async with self.token_lock:
            if not self.session_token:
                if not await self._login():
                    print("AudiobookshelfAdapter: Failed to obtain session token. Cannot perform search.")
                    return results

        if not self.session_token:
            return results

        if not hasattr(self, 'default_library_id') or not self.default_library_id:
            print("AudiobookshelfAdapter: Default library ID not found after login. Cannot perform search.")
            return results

        try:
            search_url = f"{self.api_base_url}/libraries/{self.default_library_id}/search"
            headers = {
                "Authorization": f"Bearer {self.session_token}"
            }
            params = {
                "q": query,
                "limit": 50
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    search_url,
                    headers=headers,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                items = []
                if "books" in data and isinstance(data["books"], list):
                    items.extend(data["books"])
                if "podcast" in data and isinstance(data["podcast"], list):
                    items.extend(data["podcast"])

                if not items:
                    print(f"AudiobookshelfAdapter: No recognized items (books/podcast) in search response: {data}")
                    return results

                for item in items:
                    if "libraryItem" in item:
                        book_data = item["libraryItem"].get("media", {}).get("metadata", {})
                        book_id = item["libraryItem"].get("id")
                    else:
                        book_data = item
                        book_id = item.get("_id")

                    if not book_id:
                        print(f"AudiobookshelfAdapter: Skipping item due to missing ID: {item}")
                        continue

                    title = book_data.get("title")
                    description_parts = []
                    if book_data.get("series"):
                        description_parts.append(f"Series: {book_data.get('series')}")
                    if book_data.get("author"):
                        description_parts.append(f"Author: {book_data.get('author')}")
                    if book_data.get("description"):
                        description_parts.append(book_data.get("description"))
                    description = "\n".join(description_parts).strip() or ""
                    thumbnail_url = f"{self.api_base_url}/items/{book_id}/cover"

                    results.append(SearchResult(
                        id=book_id,
                        source="Audiobookshelf",
                        title=title or "Untitled Audiobook",
                        description=description,
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(book_id, item_type="book"),
                        type="Audiobook"
                    ))
        except Exception as e:
            print(f"AudiobookshelfAdapter error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None, original_query: Optional[str] = None) -> str:
        if item_type == "book":
            return f"{self.web_base_url}/item/{item_id}"
        return f"{self.web_base_url}/"