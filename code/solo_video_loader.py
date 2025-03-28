from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError
from pytubefix.innertube import _default_clients
import os

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def solo_video_loader():
    path = str(input("Path :"))
    if os.path.exists(path):
        try:
            url = str(input("Youtube video url :"))
            video = YouTube(url)
            print(video.title)
            print(" ")

            video_stream = video.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            audio_stream = video.streams.get_audio_only()

            video_file = video_stream.download(output_path="../video")
            audio_file = audio_stream.download(output_path="../sound")

            video_path = os.path.splitext(os.path.basename(video_file))[0]
            audio_path = os.path.splitext(os.path.basename(audio_file))[0]

            # mp3
            command = f"ffmpeg -i '../sound/{audio_path}.mp4' '../sound/{audio_path}.mp3'"
            os.system(command)
            os.remove(f"../sound/{audio_path}.mp4")

            # result
            command = (f"ffmpeg -i '../video/{video_path}.mp4' -i '../sound/{audio_path}.mp3' "
                       f"-c:v  copy -c:a aac -map 0:v -map 1:a '{path}/{video_path}.mp4'")
            os.system(command)
            os.remove(f"../video/{video_path}.mp4")
            os.remove(f"../sound/{video_path}.mp3")

            print(" ")
            print("The video is downloaded in MP4")
        except RegexMatchError:
            print("Unable to fetch video information. Please check the video URL, provide the correct URL or your "
                  "network connection.")
    else:
        print("The path is wrong or doesn't exist. Please enter the correct path.")
