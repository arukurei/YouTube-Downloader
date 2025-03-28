from pytubefix import Playlist
from pytubefix.innertube import _default_clients
from rich.progress import Progress
import os

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def load(video, num, path):
    try:
        video_stream = video.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        audio_stream = video.streams.get_audio_only()
        if not os.path.exists(f"{path}/{video_stream.default_filename}"):
            video_file = video_stream.download(output_path="../video")
            audio_file = audio_stream.download(output_path="../sound")

            video_path = os.path.splitext(os.path.basename(video_file))[0]
            audio_path = os.path.splitext(os.path.basename(audio_file))[0]

            # result
            command = (f"ffmpeg -hide_banner -loglevel error -i '../video/{video_path}.mp4' -i '../sound/{audio_path}.m4a' "
                       f"-c:v  copy -c:a aac -map 0:v -map 1:a '{path}/{video_path}.mp4'")
            os.system(command)
            os.remove(f"../video/{video_path}.mp4")
            os.remove(f"../sound/{video_path}.m4a")

            print("Successfully")
            print(video.title)
            print(" ")
            num += 1
        elif os.path.exists(f"{path}{video_stream.default_filename}"):
            print("Pass")
            print(video.title)
            print(" ")
    except Exception:
        print("Error")
        print(video.title)
        print(" ")
    return num


def playlist_video_loader():
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
                print(f"+{num} videos!")
                print("The video playlist is downloaded in MP4")
    else:
        print("The path is wrong or doesn't exist. Please enter the correct path.")
