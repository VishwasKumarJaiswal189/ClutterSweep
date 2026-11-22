import os
import sys

os.environ["QT_MEDIA_BACKEND"] = "ffmpeg"
os.environ["QT_LOGGING_RULES"] = "qt.multimedia.*=false;*.debug=false;*.warning=false"

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def resource_path(relative_path: str) -> str:
    """Resolve asset paths both in dev mode and inside PyInstaller builds."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def silence_ffmpeg_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)


def main():
    silence_ffmpeg_stderr()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()