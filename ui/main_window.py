import os
import time
from send2trash import send2trash
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPlainTextEdit, QPushButton, QSlider, QSplitter, QStackedWidget,
    QTreeView, QVBoxLayout, QWidget
)
from core.database import StateDB
from core.preloader import LookAheadCache
from core.scanner import DiskScannerThread
from ui.styles import MODERN_DARK_QSS
from ui.tree_model import FileTreeModel, format_size

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClutterSweep — Visual File Triage")
        self.resize(1320, 820)
        self.setStyleSheet(MODERN_DARK_QSS)

        self.db = StateDB()
        self.cache = LookAheadCache(max_items=15)
        self.cache.payload_loaded.connect(self._on_preview_ready)

        self.current_path: str | None = None
        self.current_item = None
        self.scanner: DiskScannerThread | None = None

        self._setup_ui()
        self._setup_shortcuts()
        self._update_freed_label()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # 1. Top Card Bar
        top_card = QFrame()
        top_card.setObjectName("TopBar")
        top_bar = QHBoxLayout(top_card)
        top_bar.setContentsMargins(12, 10, 12, 10)

        self.btn_folder = QPushButton("📂  Select Folder")
        self.btn_folder.setObjectName("FolderBtn")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self._choose_folder)

        self.lbl_status = QLabel("Choose a folder to scan and start cleaning.")
        self.lbl_status.setObjectName("StatusLabel")

        top_bar.addWidget(self.btn_folder)
        top_bar.addWidget(self.lbl_status, stretch=1)
        main_layout.addWidget(top_card)

        # 2. Center 2-Pane Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left Pane: Directory Tree
        self.tree_model = FileTreeModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setColumnWidth(0, 270)
        self.tree_view.setColumnWidth(1, 85)
        self.tree_view.setAnimated(True)
        self.tree_view.selectionModel().currentChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.tree_view)

        # Right Pane: Preview Card
        preview_card = QFrame()
        preview_card.setObjectName("PreviewCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(12, 10, 12, 12)
        preview_layout.setSpacing(8)

        self.lbl_preview_header = QLabel("No file selected")
        self.lbl_preview_header.setObjectName("PreviewHeader")
        preview_layout.addWidget(self.lbl_preview_header)

        self.preview_stack = QStackedWidget()

        # Page 0: Image / PDF Viewer
        self.image_label = QLabel("Select a folder on the top-left to begin previewing files.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #14171f; border-radius: 8px; color: #64748b;")
        self.preview_stack.addWidget(self.image_label)

        # Page 1: Video / Audio Player + Scrub Bar
        media_container = QWidget()
        media_layout = QVBoxLayout(media_container)
        media_layout.setContentsMargins(0, 0, 0, 0)
        media_layout.setSpacing(8)

        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        media_layout.addWidget(self.video_widget, stretch=1)

        controls_row = QHBoxLayout()
        self.btn_play_pause = QPushButton("⏸ Pause")
        self.btn_play_pause.setCursor(Qt.PointingHandCursor)
        self.btn_play_pause.clicked.connect(self._toggle_playback)

        self.slider_seek = QSlider(Qt.Horizontal)
        self.slider_seek.sliderMoved.connect(self.media_player.setPosition)
        self.media_player.durationChanged.connect(self.slider_seek.setMaximum)
        self.media_player.positionChanged.connect(self.slider_seek.setValue)

        controls_row.addWidget(self.btn_play_pause)
        controls_row.addWidget(self.slider_seek, stretch=1)
        media_layout.addLayout(controls_row)
        self.preview_stack.addWidget(media_container)

        # Page 2: Text / Metadata Viewer
        self.text_viewer = QPlainTextEdit()
        self.text_viewer.setReadOnly(True)
        self.preview_stack.addWidget(self.text_viewer)

        preview_layout.addWidget(self.preview_stack, stretch=1)
        splitter.addWidget(preview_card)
        splitter.setSizes([450, 870])
        main_layout.addWidget(splitter, stretch=1)

        # 3. Bottom Action Card
        bottom_card = QFrame()
        bottom_card.setObjectName("BottomBar")
        bottom_bar = QHBoxLayout(bottom_card)
        bottom_bar.setContentsMargins(12, 10, 12, 10)
        bottom_bar.setSpacing(10)

        self.btn_keep = QPushButton("✓  Keep & Next  [K]")
        self.btn_keep.setObjectName("KeepBtn")
        self.btn_keep.setCursor(Qt.PointingHandCursor)
        self.btn_keep.clicked.connect(self.keep_and_next)

        self.btn_delete = QPushButton("🗑  Move to Recycle Bin  [Del]")
        self.btn_delete.setObjectName("DeleteBtn")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_and_next)

        self.lbl_freed = QLabel("Space Freed: 0.0 B")
        self.lbl_freed.setObjectName("FreedBadge")

        bottom_bar.addWidget(self.btn_keep)
        bottom_bar.addWidget(self.btn_delete)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.lbl_freed)
        main_layout.addWidget(bottom_card)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("K"), self, self.keep_and_next)
        QShortcut(QKeySequence(Qt.Key_Delete), self, self.delete_and_next)
        QShortcut(QKeySequence(Qt.Key_Space), self, self._toggle_playback)

    def _toggle_playback(self):
        if self.preview_stack.currentIndex() != 1:
            return
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.btn_play_pause.setText("▶ Play")
        else:
            self.media_player.play()
            self.btn_play_pause.setText("⏸ Pause")

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Cluttered Folder")
        if not folder:
            return
        self.lbl_status.setText(f"Scanning {folder}...")
        self.scanner = DiskScannerThread(folder)
        self.scanner.scan_finished.connect(self._on_scan_complete)
        self.scanner.start()

    def _on_scan_complete(self, root_node):
        states = self.db.get_all_states()
        self.tree_model.populate(root_node, states)
        self.tree_view.expandToDepth(1)
        self.lbl_status.setText(f"{root_node.path}  •  Total Size: {format_size(root_node.size)}")
        self._jump_to_next_unvisited(start_index=-1)

    def _on_selection_changed(self, current, _previous):
        if not current.isValid():
            return
        item = self.tree_model.itemFromIndex(current.siblingAtColumn(0))
        path = item.data(FileTreeModel.PATH_ROLE)
        size = item.data(FileTreeModel.SIZE_ROLE)
        is_dir = item.data(FileTreeModel.IS_DIR_ROLE)

        self.media_player.stop()
        self.current_item = item
        self.current_path = path
        self.lbl_preview_header.setText(f"{os.path.basename(path)}   ({format_size(size)})")

        if is_dir:
            self.text_viewer.setPlainText(f"Folder: {path}\nTotal Size: {format_size(size)}\n\nExpand in the left tree to inspect files inside.")
            self.preview_stack.setCurrentWidget(self.text_viewer)
            return

        lookahead = self._get_upcoming_unvisited_paths(item, count=3)
        self.cache.get_or_fetch(path, lookahead_paths=lookahead)

    def _on_preview_ready(self, path: str, payload: object):
        if path != self.current_path:
            return
        kind, data = payload

        if kind == "IMAGE":
            pix = QPixmap.fromImage(data)
            scaled = pix.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            self.preview_stack.setCurrentWidget(self.image_label)

        elif kind == "MEDIA":
            self.preview_stack.setCurrentIndex(1)
            self.btn_play_pause.setText("⏸ Pause")
            self.media_player.setSource(QUrl.fromLocalFile(data))
            self.media_player.play()

        else:
            self.text_viewer.setPlainText(data)
            self.preview_stack.setCurrentWidget(self.text_viewer)

    def keep_and_next(self):
        if not self.current_item or self.current_item.data(FileTreeModel.IS_DIR_ROLE):
            self._jump_to_next_unvisited()
            return
        path = self.current_item.data(FileTreeModel.PATH_ROLE)
        size = self.current_item.data(FileTreeModel.SIZE_ROLE)
        self.db.set_status(path, size, "VISITED")
        self.tree_model.mark_item_status(self.current_item, "VISITED")
        self._jump_to_next_unvisited()

    def delete_and_next(self):
        if not self.current_item or self.current_item.data(FileTreeModel.IS_DIR_ROLE):
            return
        path = self.current_item.data(FileTreeModel.PATH_ROLE)
        size = self.current_item.data(FileTreeModel.SIZE_ROLE)

        self.media_player.stop()
        self.media_player.setSource(QUrl())
        QApplication.processEvents()

        if os.path.exists(path):
            norm_path = os.path.abspath(os.path.normpath(path))
            for attempt in range(3):
                try:
                    send2trash(norm_path)
                    break
                except Exception as e:
                    if attempt == 2:
                        self.lbl_status.setText(f"Could not recycle file: {e}")
                        return
                    time.sleep(0.05)

        self.db.set_status(path, size, "DELETED")
        self.tree_model.mark_item_status(self.current_item, "DELETED")
        self._update_freed_label()
        self._jump_to_next_unvisited()

    def _get_upcoming_unvisited_paths(self, from_item, count: int = 3) -> list[str]:
        items = self.tree_model.ordered_file_items
        try:
            idx = items.index(from_item)
        except ValueError:
            return []
        upcoming = []
        for candidate in items[idx + 1:]:
            if candidate.data(FileTreeModel.STATUS_ROLE) == "UNVISITED":
                upcoming.append(candidate.data(FileTreeModel.PATH_ROLE))
                if len(upcoming) >= count:
                    break
        return upcoming

    def _jump_to_next_unvisited(self, start_index: int | None = None):
        items = self.tree_model.ordered_file_items
        if not items:
            return
        if start_index is None:
            try:
                start_index = items.index(self.current_item)
            except ValueError:
                start_index = -1

        for idx in range(start_index + 1, len(items)):
            if items[idx].data(FileTreeModel.STATUS_ROLE) == "UNVISITED":
                index = self.tree_model.indexFromItem(items[idx])
                self.tree_view.setCurrentIndex(index)
                self.tree_view.scrollTo(index)
                return

        self.lbl_status.setText("All files in this directory have been reviewed!")

    def _update_freed_label(self):
        freed = self.db.get_bytes_freed()
        self.lbl_freed.setText(f"Space Freed: {format_size(freed)}")