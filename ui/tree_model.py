from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QStandardItem, QStandardItemModel
from core.scanner import FileNode

def format_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

class FileTreeModel(QStandardItemModel):
    PATH_ROLE = Qt.UserRole + 1
    SIZE_ROLE = Qt.UserRole + 2
    IS_DIR_ROLE = Qt.UserRole + 3
    STATUS_ROLE = Qt.UserRole + 4

    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Name", "Size", "Status"])
        self.ordered_file_items: list[QStandardItem] = []

    def populate(self, root_node: FileNode, saved_states: dict[str, str]):
        self.clear()
        self.setHorizontalHeaderLabels(["Name", "Size", "Status"])
        self.ordered_file_items.clear()
        self._add_node(self.invisibleRootItem(), root_node, saved_states)

    def _add_node(self, parent_item: QStandardItem, node: FileNode, saved_states: dict[str, str]):
        status = saved_states.get(node.path, "UNVISITED")
        if status == "DELETED":
            return  # Skip already deleted files

        name_item = QStandardItem(node.name)
        size_item = QStandardItem(format_size(node.size))
        status_item = QStandardItem("✓ Visited" if status == "VISITED" else "• Unvisited")

        for item in (name_item, size_item, status_item):
            item.setEditable(False)
            item.setData(node.path, self.PATH_ROLE)
            item.setData(node.size, self.SIZE_ROLE)
            item.setData(node.is_dir, self.IS_DIR_ROLE)
            item.setData(status, self.STATUS_ROLE)

        self._apply_row_style(name_item, size_item, status_item, status, node.is_dir)
        parent_item.appendRow([name_item, size_item, status_item])

        if not node.is_dir:
            self.ordered_file_items.append(name_item)

        for child in node.children:
            self._add_node(name_item, child, saved_states)

    def mark_item_status(self, name_item: QStandardItem, new_status: str):
        parent = name_item.parent() or self.invisibleRootItem()
        row = name_item.row()
        size_item = parent.child(row, 1)
        status_item = parent.child(row, 2)

        status_text = "✓ Visited" if new_status == "VISITED" else "🗑 Deleted"
        status_item.setText(status_text)

        for item in (name_item, size_item, status_item):
            item.setData(new_status, self.STATUS_ROLE)

        self._apply_row_style(name_item, size_item, status_item, new_status, is_dir=False)

    def _apply_row_style(self, name_item, size_item, status_item, status: str, is_dir: bool):
        font = QFont()
        if status == "VISITED":
            brush = QBrush(QColor("#7f8c8d"))  # Muted gray for visited
            font.setBold(False)
        elif status == "DELETED":
            brush = QBrush(QColor("#e74c3c"))
            font.setStrikeOut(True)
        else:
            brush = QBrush(QColor("#ecf0f1"))  # Bright white for unvisited
            font.setBold(is_dir)

        for item in (name_item, size_item, status_item):
            item.setForeground(brush)
            item.setFont(font)