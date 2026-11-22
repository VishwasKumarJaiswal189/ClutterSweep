# ClutterSweep

A native Windows desktop utility built with **PySide6** for fast visual file triage and disk cleanup.

## Features
- **3-Pane Triage Layout:** Size-sorted directory tree, instant inline previewer (images, videos, audio, PDFs, text), and one-key triage controls.
- **Persistent Review State:** Tracks `Unvisited`, `Visited`, and `Deleted` files in a local SQLite database inside `%LOCALAPPDATA%\ClutterSweep`.
- **Look-Ahead Preloading:** Pre-decodes upcoming unvisited files in a background thread pool for zero-latency switching.
- **Safe Deletion:** Moves deleted files to the Windows Recycle Bin via `Send2Trash`.

## Run From Source
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py