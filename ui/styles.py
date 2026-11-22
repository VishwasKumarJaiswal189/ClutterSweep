MODERN_DARK_QSS = """
QMainWindow, QWidget {
    background-color: #12141a;
    color: #e4e7ec;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}

/* Top & Bottom Cards */
QFrame#TopBar, QFrame#BottomBar, QFrame#PreviewCard {
    background-color: #191c24;
    border: 1px solid #262b38;
    border-radius: 10px;
}

/* Buttons */
QPushButton {
    background-color: #232836;
    color: #e4e7ec;
    border: 1px solid #32394b;
    border-radius: 7px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #2c3344;
    border-color: #465069;
}
QPushButton:pressed {
    background-color: #1d222e;
}

/* Primary Keep Button */
QPushButton#KeepBtn {
    background-color: #16a34a;
    border: 1px solid #22c55e;
    color: #ffffff;
}
QPushButton#KeepBtn:hover {
    background-color: #15803d;
}

/* Danger Delete Button */
QPushButton#DeleteBtn {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
}
QPushButton#DeleteBtn:hover {
    background-color: #b91c1c;
}

/* Folder Select Button */
QPushButton#FolderBtn {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
}
QPushButton#FolderBtn:hover {
    background-color: #1d4ed8;
}

/* Directory TreeView */
QTreeView {
    background-color: #191c24;
    border: 1px solid #262b38;
    border-radius: 10px;
    padding: 6px;
    outline: none;
    show-decoration-selected: 1;
}
QTreeView::item {
    height: 28px;
    padding: 2px 6px;
    border-radius: 5px;
}
QTreeView::item:hover {
    background-color: #232836;
}
QTreeView::item:selected {
    background-color: #2b354b;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #191c24;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #262b38;
    padding: 6px 8px;
    font-weight: 600;
    font-size: 12px;
}

/* Text / Metadata Viewer */
QPlainTextEdit {
    background-color: #14171f;
    color: #cbd5e1;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12.5px;
}

/* Splitter Handle */
QSplitter::handle {
    background-color: transparent;
    width: 8px;
}

/* Badges & Labels */
QLabel#StatusLabel {
    color: #94a3b8;
    padding-left: 6px;
}
QLabel#PreviewHeader {
    color: #f8fafc;
    font-weight: 600;
    font-size: 13px;
    padding: 4px 6px;
}
QLabel#FreedBadge {
    background-color: #172554;
    color: #60a5fa;
    border: 1px solid #1e40af;
    border-radius: 7px;
    padding: 6px 12px;
    font-weight: 700;
    font-size: 13px;
}

/* Video Scrub Slider */
QSlider::groove:horizontal {
    height: 6px;
    background: #262b38;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #3b82f6;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 3px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 4px 0;
}
QScrollBar::handle:vertical {
    background: #32394b;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""