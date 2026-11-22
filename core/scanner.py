import os
from dataclasses import dataclass, field
from PySide6.QtCore import QThread, Signal

@dataclass
class FileNode:
    name: str
    path: str
    is_dir: bool
    size: int = 0
    children: list["FileNode"] = field(default_factory=list)

class DiskScannerThread(QThread):
    scan_finished = Signal(object)  # Emits root FileNode
    progress_update = Signal(str)

    def __init__(self, root_path: str):
        super().__init__()
        self.root_path = root_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        root_node = self._scan_dir(self.root_path)
        if not self._is_cancelled:
            self.scan_finished.emit(root_node)

    def _scan_dir(self, current_path: str) -> FileNode:
        name = os.path.basename(current_path) or current_path
        node = FileNode(name=name, path=current_path, is_dir=True)
        total_size = 0

        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if self._is_cancelled:
                        break
                    try:
                        # Avoid infinite recursion on Windows junctions/symlinks
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            child_dir = self._scan_dir(entry.path)
                            if child_dir.size > 0:
                                node.children.append(child_dir)
                                total_size += child_dir.size
                        elif entry.is_file(follow_symlinks=False):
                            f_size = entry.stat().st_size
                            node.children.append(
                                FileNode(name=entry.name, path=entry.path, is_dir=False, size=f_size)
                            )
                            total_size += f_size
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass

        # Sort children largest-first so biggest clutter appears at top
        node.children.sort(key=lambda x: x.size, reverse=True)
        node.size = total_size
        return node