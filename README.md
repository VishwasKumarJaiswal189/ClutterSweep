# ClutterSweep


A native Windows desktop utility built with **PySide6** for fast visual file triage and disk cleanup.

## Features
- **3-Pane Triage Layout:** Size-sorted directory tree, instant inline previewer (images, videos, audio, PDFs, text), and one-key triage controls.
- **Persistent Review State:** Tracks `Unvisited`, `Visited`, and `Deleted` files in a local SQLite database inside `%LOCALAPPDATA%\ClutterSweep`.
- **Look-Ahead Preloading:** Pre-decodes upcoming unvisited files in a background thread pool for zero-latency switching.
- **Safe Deletion:** Moves deleted files to the Windows Recycle Bin via `Send2Trash`.
## Download & Install (Windows 10 / 11)

- **[Download ClutterSweep-Setup-v1.0.0.exe](https://github.com/VishwasKumarJaiswal189/ClutterSweep/releases/download/v1.0.0/ClutterSweep-Setup-v1.0.0.exe)** — Direct Windows installer
- **[View All Releases](https://github.com/VishwasKumarJaiswal189/ClutterSweep/releases)** — Release notes & installer versions




### Quick Setup
1. Download **`ClutterSweep-Setup-v1.0.0.exe`** using the link above.
2. Run the installer to install ClutterSweep and add Start Menu / Desktop shortcuts.
3. Launch **ClutterSweep** and pick any folder to start cleaning.
