import os
import getpass
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import RegexMatchError
from rich.progress import Progress
from core import process_single_item


def _get_valid_path():
    path = input("Output Path: ").strip()
    if os.path.exists(path):
        return path
    else:
        return None


def _wait_input():
    getpass.getpass("\n\033[5mPress Enter to continue \033[0m")


def handle_solo(is_audio_only):
    path = _get_valid_path()
    if path:
        url = input("Youtube video url: ").strip()

        try:
            print("Fetching info...")
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            print(f"Title: {yt.title}")

            status = process_single_item(yt, path, is_audio_only)
            if status == "Success": print(f"Downloaded successfully in {'MP3' if is_audio_only else 'MP4'}")
            elif status == "Pass": print("File already exists.")
            else: print("Error occurred during processing.")
        except RegexMatchError:
            print("Invalid URL.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Path does not exist.")
    _wait_input()

def handle_playlist(is_audio_only):
    path = _get_valid_path()
    if path:
        url = input("Youtube playlist url: ").strip()

        try:
            pl = Playlist(url, use_oauth=True, allow_oauth_cache=True)
            count = 0
            with Progress() as progress:
                task = progress.add_task("[cyan]Processing Playlist...", total=len(pl.videos))
                for video in pl.videos:
                    progress.update(task, description=f"Processing: {video.title[:30]}...")
                    status = process_single_item(video, path, is_audio_only)
                    if status == "Success": count += 1
                    progress.update(task, advance=1)
            print(f"\nFinished! +{count} new files.")

        except Exception as e:
            print(f"Error processing playlist: {e}")
    else:
        print("Path does not exist.")
    _wait_input()


def solo_video_loader(): handle_solo(is_audio_only=False)
def solo_sound_loader(): handle_solo(is_audio_only=True)
def playlist_video_loader(): handle_playlist(is_audio_only=False)
def playlist_sound_loader(): handle_playlist(is_audio_only=True)