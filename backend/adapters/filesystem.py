from adapters.base import DataSourceAdapter
from models.search_result import SearchResult
import os
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

class _IndexUpdateHandler(FileSystemEventHandler):
    def __init__(self, adapter):
        self.adapter = adapter

    def on_any_event(self, event):
        # 简单策略：任何变更都重建索引（可优化为增量）
        self.adapter.build_index()

class FileSystemAdapter(DataSourceAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.root_path = config.get("search_path", "/data/search_root")
        self.index = []
        self.build_index()
        self._start_watchdog()

    def _start_watchdog(self):
        event_handler = _IndexUpdateHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.root_path, recursive=True)
        t = threading.Thread(target=observer.start, daemon=True)
        t.start()

    def build_index(self):
        self.index = []
        for dirpath, _, filenames in os.walk(self.root_path):
            for fname in filenames:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), self.root_path)
                self.index.append((rel_path, os.path.join(dirpath, fname)))

    async def search(self, query: str) -> List[SearchResult]:
        results = []
        for rel_path, abs_path in self.index:
            if query.lower() in os.path.basename(rel_path).lower():
                results.append(SearchResult(
                    id=rel_path,
                    source="filesystem",
                    title=os.path.basename(rel_path),
                    description=rel_path,
                    thumbnail_url=None,
                    detail_url=f"/download/filesystem/{rel_path}",
                    type="file"
                ))
        return results

    def _build_detail_url(self, item_id: str, item_type: str = None, original_query: str = None) -> str:
        return f"/download/filesystem/{item_id}"

    # TODO: add download support
