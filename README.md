# YouTube-Downloader (YTD)

| <img src="assets/icon.png" width="320" /> | A Python-based terminal application for downloading videos and audio from YouTube. It combines a text user interface (TUI) for navigation with a command-line interface for the download process. |
|:------------------------------------------| :--- |

![img.png](assets/img_1.png)

![img.png](assets/img_2.png)

![img.png](assets/img_3.png)

![img.png](assets/img_4.png)

## Features
*   **Interactive TUI Menu:** Built with `Textual` for keyboard and mouse navigation.
*   **Video & Audio Extraction:** Supports downloading high-quality video (MP4) and audio-only extraction (MP3 with embedded thumbnails and metadata).
*   **Progress Tracking:** Visual progress bars using `Rich`.
*   **Playlist Support:** Sequential processing of playlists with index counters.
*   **Path History:** Remembers up to three recently used download directories.
*   **Error Classification:** Clear and concise explanations for common errors (network issues, age restrictions, geo-blocks, missing FFmpeg, etc.).

## Quick Start (Ready-to-use Release)
You don't need to install Python or any dependencies to use the app!
1. Go to the [Releases](https://github.com/arukurei/YouTube-Downloader/releases) page.
2. Download the latest executable file for your operating system.
3. Run the downloaded file—no installation required!

## Requirements
*   Python 3.8 or higher
*   Required libraries: `yt-dlp`, `rich`, `textual`, `imageio-ffmpeg`
*   **FFmpeg** (required for audio extraction and video merging)

## Installation
1. Clone the repository or copy the source files.
2. Install the dependencies:
   ```bash
   pip install yt-dlp rich textual imageio-ffmpeg
   ```
3. Ensure ffmpeg and ffprobe are installed on your system and added to your system path.

## Usage
If you downloaded the release version, simply double-click the executable.
If you are running from source, open your terminal and execute:

```bash
python main.py
```

*   Use **Up/Down arrow keys** or the **Mouse** to navigate the menu.
*   Press **Enter** or click to select an option.
*   Enter the output directory path (or select from history) and the URL when prompted.
*   Type `/test` in the URL prompt to run a simulated visualization test.
