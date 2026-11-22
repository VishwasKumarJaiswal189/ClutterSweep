import os
from collections import OrderedDict
import pymupdf  # PyMuPDF
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QImage

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
TEXT_EXTS = {".txt", ".md", ".py", ".js", ".json", ".csv", ".log", ".xml", ".html", ".css"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg"}

FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000

class PreloadSignals(QObject):
    ready = Signal(str, object)  # path, decoded_payload

class DecodeWorker(QRunnable):
    def __init__(self, path: str, signals: PreloadSignals):
        super().__init__()
        self.path = path
        self.signals = signals

    def run(self):
        if not os.path.exists(self.path):
            return
        ext = os.path.splitext(self.path)[1].lower()
        payload = ("META", self._build_metadata())

        try:
            # Skip decoding cloud-only OneDrive files so Windows doesn't force-download them
            st = os.stat(self.path)
            if getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS:
                payload = ("META", f"☁️ Cloud-Only OneDrive File (Not Downloaded)\n\n{self._build_metadata()}")
                self.signals.ready.emit(self.path, payload)
                return

            if ext in IMAGE_EXTS:
                img = QImage(self.path)
                if not img.isNull():
                    if img.width() > 1600 or img.height() > 1200:
                        img = img.scaled(1600, 1200)
                    payload = ("IMAGE", img)

            elif ext == ".pdf":
                doc = pymupdf.open(self.path)
                if len(doc) > 0:
                    page = doc.load_page(0)
                    pix = page.get_pixmap(dpi=120)
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888).copy()
                    payload = ("IMAGE", img)
                doc.close()

            elif ext in TEXT_EXTS:
                with open(self.path, "r", encoding="utf-8", errors="replace") as f:
                    snippet = f.read(50_000)  # Cap at 50 KB
                payload = ("TEXT", snippet)

            elif ext in VIDEO_EXTS or ext in AUDIO_EXTS:
                payload = ("MEDIA", self.path)

        except Exception as e:
            payload = ("META", f"Preview unavailable: {e}\n\n{self._build_metadata()}")

        self.signals.ready.emit(self.path, payload)

    def _build_metadata(self) -> str:
        stat = os.stat(self.path)
        size_mb = stat.st_size / (1024 * 1024)
        return f"File: {os.path.basename(self.path)}\nPath: {self.path}\nSize: {size_mb:.2f} MB"

class LookAheadCache(QObject):
    payload_loaded = Signal(str, object)

    def __init__(self, max_items: int = 15):
        super().__init__()
        self.cache: OrderedDict[str, object] = OrderedDict()
        self.in_flight: set[str] = set()
        self.max_items = max_items
        self.pool = QThreadPool.globalInstance()
        self.signals = PreloadSignals()
        self.signals.ready.connect(self._on_ready)

    def get_or_fetch(self, path: str, lookahead_paths: list[str] = None):
        if lookahead_paths:
            for upcoming in lookahead_paths:
                if upcoming not in self.cache and upcoming not in self.in_flight:
                    self._enqueue(upcoming)

        if path in self.cache:
            self.cache.move_to_end(path)
            self.payload_loaded.emit(path, self.cache[path])
        elif path not in self.in_flight:
            self._enqueue(path)

    def _enqueue(self, path: str):
        self.in_flight.add(path)
        worker = DecodeWorker(path, self.signals)
        self.pool.start(worker)

    def _on_ready(self, path: str, payload: object):
        self.in_flight.discard(path)
        self.cache[path] = payload
        if len(self.cache) > self.max_items:
            self.cache.popitem(last=False)
        self.payload_loaded.emit(path, payload)