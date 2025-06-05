from typing import List, Optional
from models.search_result import SearchResult

class DataSourceAdapter:
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.api_base_url = config.get("api_base_url")
        self.web_base_url = config.get("web_base_url")

    async def search(self, query: str) -> List[SearchResult]:
        raise NotImplementedError

    def _build_detail_url(self, item_id: str, item_type: Optional[str] = None, original_query: Optional[str] = None) -> str:
        raise NotImplementedError