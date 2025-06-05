from fastapi import APIRouter, Query
from typing import List
import asyncio
from models.search_result import SearchResult
from adapters.jellyfin import JellyfinAdapter
from adapters.audiobookshelf import AudiobookshelfAdapter
from adapters.photoprism import PhotoPrismAdapter
from adapters.calibreweb import CalibreWebAdapter
from config import DATA_SOURCE_CONFIGS

router = APIRouter()

ADAPTERS = [
    JellyfinAdapter(DATA_SOURCE_CONFIGS["jellyfin"]),
    AudiobookshelfAdapter(DATA_SOURCE_CONFIGS["audiobookshelf"]),
    PhotoPrismAdapter(DATA_SOURCE_CONFIGS["photoprism"]),
    CalibreWebAdapter(DATA_SOURCE_CONFIGS["calibreweb"]),
]

@router.get("/search", response_model=List[SearchResult])
async def unified_search(query: str = Query(..., min_length=1, max_length=100)):
    if not query.strip():
        return []

    tasks = [adapter.search(query) for adapter in ADAPTERS if adapter.enabled]
    results_lists = await asyncio.gather(*tasks, return_exceptions=True)

    all_results: List[SearchResult] = []
    for res_list in results_lists:
        if isinstance(res_list, Exception):
            print(f"Error during search for one adapter: {type(res_list).__name__} - {res_list}")
            continue
        all_results.extend(res_list)
    return all_results

@router.get("/config")
async def get_config():
    display_config = {k: {key: v for key, v in val.items() if key not in ["api_key", "token", "user_id"]}
                      for k, val in DATA_SOURCE_CONFIGS.items()}
    return display_config