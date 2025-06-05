import httpx
from typing import List, Optional
from models.search_result import SearchResult
from .base import DataSourceAdapter

class PhotoPrismAdapter(DataSourceAdapter):
    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
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
                    photo_hash = photo.get("Hash")
                    if photo_hash:
                        thumbnail_url = f"{self.web_base_url}/api/v1/t/{photo_hash}/public/tile_500"
                    else:
                        thumbnail_url = ""
                        print(f"Warning: Photo {photo.get('UID')} has no 'Hash' for thumbnail generation.")

                    results.append(SearchResult(
                        id=photo["UID"],
                        source="PhotoPrism",
                        title=photo.get("Title") or photo.get("FileName", "Untitled Photo"),
                        description=photo.get("Description"),
                        thumbnail_url=thumbnail_url,
                        detail_url=self._build_detail_url(photo["Hash"]),
                        type="Photo"
                    ))
        except Exception as e:
            print(f"PhotoPrismAdapter error: {e}")
        return results

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None, original_query: Optional[str] = None) -> str:
        return f"{self.web_base_url}/api/v1/dl/{item_id}"