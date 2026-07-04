import os
from yt_dlp import YoutubeDL


class QuietLogger:
    def debug(self, msg): pass

    def warning(self, msg): pass

    def error(self, msg): pass

    def info(self, msg): pass


def process_single_item(url: str, output_dir: str, is_audio_only: bool, progress_callback=None):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'writethumbnail': True,
        'addmetadata': True,
        'noprogress': True,
        'logger': QuietLogger(),
    }

    if is_audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [
                {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'}
            ],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessors': [
                {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'},
            ],
        })

    def ydl_hook(d):
        if progress_callback:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                pct = (downloaded / total) * 100 if total > 0 else 0
                progress_callback('downloading', pct)
            elif d['status'] == 'finished':
                progress_callback('finished', 100)

    ydl_opts['progress_hooks'] = [ydl_hook]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            temp_filename = ydl.prepare_filename(info_dict)

            base, _ = os.path.splitext(temp_filename)
            final_ext = ".mp3" if is_audio_only else ".mp4"
            final_filepath = base + final_ext

            if os.path.exists(final_filepath): return "Pass"

            ydl.process_info(info_dict)
            return "Success"

    except Exception as e:
        try:
            if 'base' in locals() and os.path.exists(output_dir):
                base_name = os.path.basename(base)
                for file in os.listdir(output_dir):
                    if file.startswith(base_name) and not file.endswith((".mp3", ".mp4")):
                        try:    os.remove(os.path.join(output_dir, file))
                        except: pass
        except: pass
        return f"Error: {e}"