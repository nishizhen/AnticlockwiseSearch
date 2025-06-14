from adapters.base import DataSourceAdapter
from models.search_result import SearchResult
import os
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent, FileMovedEvent
import threading
import time

class _IndexUpdateHandler(FileSystemEventHandler):
    def __init__(self, adapter):
        self.adapter = adapter

    def on_created(self, event):
        if not event.is_directory:
            rel_path = os.path.relpath(event.src_path, self.adapter.root_path)
            self.adapter.index[rel_path] = event.src_path

    def on_deleted(self, event):
        if not event.is_directory:
            rel_path = os.path.relpath(event.src_path, self.adapter.root_path)
            self.adapter.index.pop(rel_path, None)

    def on_moved(self, event):
        if not event.is_directory:
            old_rel = os.path.relpath(event.src_path, self.adapter.root_path)
            new_rel = os.path.relpath(event.dest_path, self.adapter.root_path)
            self.adapter.index.pop(old_rel, None)
            self.adapter.index[new_rel] = event.dest_path

class FileSystemAdapter(DataSourceAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.root_path = config.get("search_path", "/data/search_root")
        self.backend_base_url = config.get("backend_base_url", "http://localhost:8000")
        self.index = {}  # key: rel_path, value: abs_path
        self.build_index()
        self._start_watchdog()

    def _start_watchdog(self):
        event_handler = _IndexUpdateHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.root_path, recursive=True)
        t = threading.Thread(target=observer.start, daemon=True)
        t.start()

    def build_index(self):
        self.index = {}
        for dirpath, _, filenames in os.walk(self.root_path):
            for fname in filenames:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), self.root_path)
                self.index[rel_path] = os.path.join(dirpath, fname)

    async def search(self, query: str) -> List[SearchResult]:
        results = []
        for rel_path, abs_path in self.index.items():
            if query.lower() in os.path.basename(rel_path).lower():
                results.append(SearchResult(
                    id=rel_path,
                    source="filesystem",
                    title=os.path.basename(rel_path),
                    description=rel_path,
                    thumbnail_url=None,
                    detail_url=f"{self.backend_base_url}/download/filesystem/{rel_path}",
                    type="file"
                ))
        return results

    def _build_detail_url(self, item_id: str, item_type: str = None, original_query: str = None) -> str:
        return f"{self.backend_base_url}/download/filesystem/{item_id}"
