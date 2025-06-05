import httpx
from typing import List, Optional
from models.search_result import SearchResult
from .base import DataSourceAdapter

class JellyfinAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
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
                params = {
                    "searchTerm": query,
                    "Recursive": "true",
                    "IncludeItemTypes": "Movie,Series,Episode,Audio,Photo,Book"
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
        except Exception as e:
            print(f"JellyfinAdapter error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None, original_query: Optional[str] = None) -> str:
        return f"{self.web_base_url}/web/index.html#!/details?id={item_id}"