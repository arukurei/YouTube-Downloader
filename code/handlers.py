import os
import getpass
from yt_dlp import YoutubeDL
from rich.progress import Progress
from core import process_single_item


def _get_valid_path():
    path = input("Output Path: ").strip()
    if os.path.exists(path): return path
    else: return None


def _wait_input():
    getpass.getpass("\n\033[5mPress Enter to continue \033[0m")


def handle_solo(is_audio_only):
    path = _get_valid_path()
    if not path: return
    url = input("Youtube video url: ").strip()

    print("Processing...")
    status = process_single_item(url, path, is_audio_only)

    if status == "Success":
        print("Done!")
    elif status == "Pass":
        print("Already exists.")
    else:
        print("Failed.")
    _wait_input()


def handle_playlist(is_audio_only):
    path = _get_valid_path()
    if not path: return
    url = input("Youtube playlist url: ").strip()

    try:
        # Сначала получаем список видео в плейлисте без скачивания
        with YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            entries = playlist_info.get('entries', [])

        print(f"Found: {len(entries)} videos")
        count = 0

        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading...", total=len(entries))

            for entry in entries:
                video_url = entry.get('url') or entry.get('id')
                if not video_url: continue

                # Обновляем текст в статус-баре
                progress.update(task, description=f"Loading: {entry.get('title', '')[:20]}...")

                status = process_single_item(video_url, path, is_audio_only)
                if status == "Success": count += 1
                progress.update(task, advance=1)

        print(f"\nFinished! +{count} new files.")
    except Exception as e:
        print(f"Playlist error: {e}")
    _wait_input()

def solo_video_loader(): handle_solo(is_audio_only=False)
def solo_sound_loader(): handle_solo(is_audio_only=True)
def playlist_video_loader(): handle_playlist(is_audio_only=False)
def playlist_sound_loader(): handle_playlist(is_audio_only=True)