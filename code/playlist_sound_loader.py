from pytubefix import Playlist
from pytubefix.innertube import _default_clients
from rich.progress import Progress
import os

"""def playlist_sound_converter():
    playlist = Path("playlist/").glob('*.mp4')
    for video in playlist:
        file_name = os.path.splitext(os.path.basename(video))[0]
        if not os.path.exists(f"sound_playlist/{file_name}.mp3"):
            command = f"ffmpeg -i 'playlist/{file_name}.mp4' 'sound_playlist/{file_name}.mp3'"
            os.system(command)
        else:
            print("pass")
            print(" ")
    print("The playlist is converted in MP3")"""

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def load(video, num, path):
    try:
        stream = video.streams.filter(progressive=True).get_highest_resolution()
        if not os.path.exists(f"{path}/{os.path.splitext(stream.default_filename)[0]}.mp3"):
            file = stream.download(output_path="../sound")
            print(video.title)
            num += 1

            file_name = os.path.splitext(os.path.basename(file))[0]
            command = f"ffmpeg -hide_banner -loglevel error -i '../sound/{file_name}.mp4' '{path}/{file_name}.mp3'"
            os.system(command)
            os.remove(f"../sound/{file_name}.mp4")
            print("Successfully")
            print(" ")
        elif os.path.exists(f"{path}/{os.path.splitext(stream.default_filename)[0]}.mp3"):
            print("Pass")
            print(video.title)
            print(" ")
    except Exception:
        print("Error")
        print(video.title)
        print(" ")
    return num


def playlist_sound_loader():
    path = str(input("Path :"))
    if os.path.exists(path):
        url = str(input("Youtube playlist url :"))
        with Progress() as progress:
            pl = Playlist(url)
            num = 0
            try:
                task = progress.add_task("[cyan]Downloading...", total=len(pl))
            except KeyError:
                print("Unable to fetch playlist information. Please check the playlist URL, provide the correct URL or "
                      "your network connection.")

            while not progress.finished:
                for video in pl.videos:
                    num = load(video, num, path)
                    progress.update(task, advance=1)
                print(f"+{num} sounds!")
                print("The sound playlist is downloaded in MP3")
    else:
        print("The path is wrong or doesn't exist. Please enter the correct path.")
