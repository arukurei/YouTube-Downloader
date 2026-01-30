import os
import subprocess
from pathlib import Path
from pytubefix import YouTube
from pytubefix.innertube import _default_clients


_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
TEMP_VIDEO_DIR = Path("../temp_video")
TEMP_AUDIO_DIR = Path("../temp_sound")


def ensure_temp_dirs():
    TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def run_ffmpeg(inputs, output_path, video_mode=False):
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for i in inputs: command.extend(['-i', str(i)])
    if video_mode: command.extend(['-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a', '-strict', 'experimental'])

    command.append(str(output_path))
    subprocess.run(command, check=True)


def get_best_video_stream(yt_obj):
    streams = yt_obj.streams.filter(adaptive=True, only_video=True)
    if not streams: return None

    def sort_key(s):
        res = int(s.resolution.replace('p', '')) if s.resolution else 0
        return (res, s.fps)
    best_stream = max(streams, key=sort_key)
    return best_stream


def process_single_item(yt_obj: YouTube, output_dir: str, is_audio_only: bool):
    try:
        ensure_temp_dirs()
        safe_title = "".join([c for c in yt_obj.title if c.isalpha() or c.isdigit() or c in " .-_"]).rstrip()
        output_path = Path(output_dir)

        if is_audio_only:
            final_file = output_path / f"{safe_title}.mp3"
            if final_file.exists(): return "Pass"

            ## Скачиваем только аудио (progressive или highest audio)
            stream = yt_obj.streams.get_audio_only()
            if not stream: stream = yt_obj.streams.filter(only_audio=True).first() # Фоллбэк, если get_audio_only не сработал
            temp_file = Path(stream.download(output_path=TEMP_AUDIO_DIR))

            # Конвертация
            run_ffmpeg([temp_file], final_file, video_mode=False)

            ## Чистка
            os.remove(temp_file)
        else:
            final_file = output_path / f"{safe_title}.mp4"
            if final_file.exists(): return "Pass"

            ## Скачивание
            video_stream = get_best_video_stream(yt_obj)
            audio_stream = yt_obj.streams.get_audio_only()

            if not video_stream or not audio_stream:
                print(f"Skipping {yt_obj.title}: stream not found")
                return "Error"
            print(f"DEBUG: Loading {video_stream.resolution} {video_stream.fps}fps")

            v_file = Path(video_stream.download(output_path=TEMP_VIDEO_DIR, filename_prefix="v_"))
            a_file = Path(audio_stream.download(output_path=TEMP_AUDIO_DIR, filename_prefix="a_"))

            ## Слияние
            run_ffmpeg([v_file, a_file], final_file, video_mode=True)

            ## Чистка
            os.remove(v_file)
            os.remove(a_file)
        return "Success"
    except Exception as e:
        print(f"Error detail: {e}")
        return "Error"
