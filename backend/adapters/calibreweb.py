import httpx
from typing import List, Optional
from models.search_result import SearchResult
from .base import DataSourceAdapter

class CalibreWebAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            if not self.api_base_url:
                print("CalibreWebAdapter: api_base_url is not set for the adapter.")
                return results

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/books",
                    params={"query": query},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                for book in data.get("books", []):
                    thumbnail_url = f"{self.web_base_url}/get_cover/{book['id']}" if book.get("id") else None
                    results.append(SearchResult(
                        id=str(book["id"]),
                        source="CalibreWeb",
                        title=book.get("title", "Untitled Book"),
                        description=book.get("description"),
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(str(book["id"])),
                        type="Book"
                    ))
        except Exception as e:
            print(f"CalibreWebAdapter error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None, original_query: Optional[str] = None) -> str:
        return f"{self.web_base_url}/book/{item_id}"