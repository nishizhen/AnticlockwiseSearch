from pydantic import BaseModel
from typing import Optional

class SearchResult(BaseModel):
    id: str
    source: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    detail_url: str
    type: Optional[str] = None