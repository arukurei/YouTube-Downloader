import os
from yt_dlp import YoutubeDL


def process_single_item(url: str, output_dir: str, is_audio_only: bool):
    """
    Скачивает видео или аудио через yt-dlp.
    url: ссылка на видео
    output_dir: папка для сохранения
    is_audio_only: если True - скачает только MP3
    """

    # Настройки yt-dlp
    ydl_opts = {
        # Шаблон имени файла: Название.расширение
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': True,  # Не забивать консоль лишним текстом
        'no_warnings': True,
        'nocheckcertificate': True,
        'writethumbnail': True,  # Скачать обложку
        'addmetadata': True,  # Добавить метаданные
    }

    if is_audio_only:
        # Настройки для аудио
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    # Конвертация в MP3
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    # Вшивание обложки в файл
                    'key': 'EmbedThumbnail',
                },
                {
                    # Вшивание метаданных
                    'key': 'FFmpegMetadata',
                }
            ],
        })
    else:
        # Настройки для видео (лучшее видео + лучшее аудио)
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',  # Итог в MP4
            'postprocessors': [
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'},
            ],
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Проверяем, не скачан ли файл уже (yt-dlp делает это сам, но для статуса)
            info = ydl.extract_info(url, download=True)
            return "Success"
    except Exception as e:
        if "already been downloaded" in str(e):
            return "Pass"
        print(f"Error: {e}")
        return "Error"