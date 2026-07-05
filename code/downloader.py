import os
import getpass
import re
import json
import time
from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from rich import print
from rich.progress import Progress, BarColumn, TextColumn, ProgressColumn
from rich.text import Text
from rich.spinner import Spinner
from rich.cells import cell_len

import config
from core import process_single_item, QuietLogger


def _clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def _wait_input():
    getpass.getpass("\n\033[5mPress Enter to continue \033[0m")
    _clear_screen()


def _get_history_filepath() -> str:
    if os.name == 'nt': base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:               base = os.path.join(os.path.expanduser('~'), '.config')

    folder = os.path.join(base, 'loader_app')
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = os.path.expanduser('~')
    return os.path.join(folder, 'history.json')


def _load_history() -> list:
    filepath = _get_history_filepath()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list): return [str(p).strip() for p in data if p][:3]
        except Exception:
            pass
    return []


def _save_history(new_path: str):
    if not new_path: return
    new_path = os.path.abspath(new_path)
    filepath = _get_history_filepath()
    history = _load_history()

    if new_path in history: history.remove(new_path)

    history.insert(0, new_path)
    history = history[:3]

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def _parse_error(error_msg: str) -> str:
    err_lower = error_msg.lower()

    if "ffmpeg" in err_lower or "ffprobe" in err_lower:
        return "Engine error | FFmpeg is missing"
    elif "sign in" in err_lower or "confirm your age" in err_lower or "age-gated" in err_lower:
        return "Age restricted | Video requires login"
    elif "private" in err_lower:
        return "Private video | This video is private"
    elif "unavailable" in err_lower or "not exist" in err_lower or "404" in err_lower:
        return "Unavailable | Video does not exist"
    elif "country" in err_lower or "geo restriction" in err_lower or "region" in err_lower:
        return "Region locked | Blocked in your country (try VPN)"
    elif "connection" in err_lower or "network" in err_lower or "urlopen" in err_lower or "timeout" in err_lower:
        return "Network error | Check connection or try VPN"
    elif "403" in err_lower:
        return "Access blocked | YouTube restricted this request (try VPN)"
    elif "permission" in err_lower or "denied" in err_lower:
        return "Folder restricted | Choose another save path"
    elif "space" in err_lower or "full" in err_lower:
        return "Disk full | Free up space and try again"

    clean_err = error_msg.replace("Error:", "").strip().split("\n")[0]
    if len(clean_err) > 45:
        clean_err = clean_err[:42] + "..."
    return f"{clean_err} | Try another video"


def _draw_box(text: str, border_color: str = "white", title: str = "") -> str:
    clean_text = re.sub(r'\[/?.*?\]', '', text)
    clean_title = re.sub(r'\[/?.*?\]', '', title) if title else ""

    text_len = len(clean_text)
    title_len = len(clean_title)

    if title:
        min_width = max(text_len, title_len + 4)
    else:
        min_width = text_len

    padded_text = text + " " * (min_width - text_len)

    if title:
        dashes = min_width - title_len - 1
        top = f"[{border_color}]╭─[/{border_color}] {title} [{border_color}]{'─' * dashes}╮[/{border_color}]"
    else:
        top = f"[{border_color}]╭{'─' * (min_width + 2)}╮[/{border_color}]"

    middle = f"[{border_color}]│[/{border_color}] {padded_text} [{border_color}]│[/{border_color}]"
    bottom = f"[{border_color}]╰{'─' * (min_width + 2)}╯[/{border_color}]"

    return f"{top}\n{middle}\n{bottom}"


def _format_info_line(url: str, path: str, max_part_len: int = 25) -> str:
    safe_url = url if url else "..."
    safe_path = path if path else "..."

    if len(safe_url) > max_part_len:
        safe_url = safe_url[:max_part_len - 3] + "..."
    if len(safe_path) > max_part_len:
        safe_path = safe_path[:max_part_len - 3] + "..."

    return f"Path: {safe_path} | Link: {safe_url}"


def _format_row(prefix: str, text: str, width: int = 40) -> str:
    text = str(text).replace('\n', ' ').strip()

    # Считаем реальную визуальную ширину префикса
    prefix_width = cell_len(prefix)
    max_cell_width = width - prefix_width

    if cell_len(text) > max_cell_width:
        # Если текст слишком длинный, аккуратно обрезаем его посимвольно
        target_width = max_cell_width - 3
        current_text = ""
        current_width = 0
        for char in text:
            char_width = cell_len(char)
            if current_width + char_width > target_width: break
            current_text += char
            current_width += char_width

        text = current_text + "..."

    # Дозаполняем оставшееся пространство пробелами до точной ширины
    padding = max_cell_width - cell_len(text)
    text = text + " " * padding

    return f"{prefix}{text}"


def _check_file_exists(output_dir: str, raw_title: str, is_audio_only: bool) -> bool:
    if not os.path.exists(output_dir): return False
    clean_title = sanitize_filename(raw_title)
    final_ext = ".mp3" if is_audio_only else ".mp4"

    for file in os.listdir(output_dir):
        if file == f"{clean_title}{final_ext}": return True
        if file.startswith(f"{clean_title}.") and file.endswith(final_ext): return True
    return False


def _validate_url(url):
    if url.strip().lower() == "/test":
        return {
            'title': 'System Visualization Test',
            'entries': config.MOCK_TEST_CASES
        }

    opts = {
        'quiet': True, 'no_warnings': True, 'extract_flat': True,
        'noprogress': True, 'ignoreerrors': True, 'logger': QuietLogger()
    }
    try:
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        return None


class DynamicIconColumn(ProgressColumn):
    def __init__(self, table_column=None):
        super().__init__(table_column)
        self.spinner = Spinner("dots", style="bold cyan")

    def render(self, task):
        if task.finished: return Text("✔ ", style="green")
        return Text.assemble(self.spinner.render(task.elapsed or 0), " ")


def create_solid_bar():
    return Progress(
        DynamicIconColumn(),
        TextColumn("{task.description}"),
        BarColumn(
            bar_width=30,
            style="#2c2a3e",
            complete_style="bold #00f0ff",
            finished_style="bold #a6e3a1"
        ),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=False,
        refresh_per_second=10
    )


def handle_download(is_audio_only):
    title_text = f"« {'Sound' if is_audio_only else 'Video'} Loader »"

    _clear_screen()
    print(_draw_box(title_text, border_color="blue"))
    print()

    history = _load_history()
    if history:
        print("[#6c7086]Recent paths (enter number to auto-select):[/#6c7086]")
        for idx, item in enumerate(history, 1):
            print(f" [#6c7086][{idx}] {item}[/#6c7086]")
        print()

    raw_path_input = input("Output Path: ").strip()

    if raw_path_input in ("1", "2", "3") and len(history) >= int(raw_path_input):
        path = history[int(raw_path_input) - 1]
    else:
        path = raw_path_input

    is_test_path = path.lower() in ("test", "virtual_test_directory")
    if is_test_path: path = "Virtual_Test_Directory"

    if not is_test_path and (not path or not os.path.exists(path)):
        _clear_screen()
        print(_draw_box(title_text, border_color="blue"))
        print()
        info_line = _format_info_line(url="", path=path)
        print(_draw_box(info_line, border_color="red", title="[bold red]Error: Invalid Path[/bold red]"))
        _wait_input()
        return

    url = input("Youtube URL: ").strip()

    is_test_mode = (url.strip().lower() == "/test") or is_test_path

    info = _validate_url(url)

    is_valid = True
    err_msg = ""

    if not info:
        is_valid, err_msg = False, "Error: Invalid Link"
    else:
        entries = info.get('entries')
        is_playlist = entries is not None
        if not is_playlist: entries = [info]
        if not entries: is_valid, err_msg = False, "Error: No valid videos found"

    if not is_valid:
        _clear_screen()
        print(_draw_box(title_text, border_color="blue"))
        print()
        info_line = _format_info_line(url=url, path=path)
        print(_draw_box(info_line, border_color="red", title=f"[bold red]{err_msg}[/bold red]"))
        _wait_input()
        return

    if not is_test_mode: _save_history(path)

    _clear_screen()
    print(_draw_box(title_text, border_color="blue"))
    print()
    info_line = _format_info_line(url=url, path=path)
    print(_draw_box(info_line, border_color="#a9b2d3"))
    print()

    if is_playlist:
        playlist_title = info.get('title') or "Unknown Playlist"
        print(f"[Playlist] {playlist_title}")

    s_success = 0
    s_pass = 0
    s_err = 0
    total_files = len(entries)

    icon_pass = "»  "
    icon_error = "✖  "

    for idx, entry in enumerate(entries, start=1):
        video_url = entry.get('url') or entry.get('id')
        raw_title = entry.get('title') or entry.get('id') or "Unknown Video"

        prefix = f"[{idx}/{total_files}] " if is_playlist else ""
        safe_title = _format_row(prefix, raw_title)

        v_id = entry.get('id')
        display_url = f"https://youtu.be/{v_id}" if v_id else (entry.get('url') or url)

        if not video_url and not is_test_mode:
            print(f"[red]{icon_error}{safe_title} [Error][/red]")
            print(f"   [#6c7086]├─ Link: {display_url}[/#6c7086]")
            print(f"   [#6c7086]└─ Info: Missing URL | Try another video[/#6c7086]")
            s_err += 1
            continue

        if not is_test_mode and _check_file_exists(path, raw_title, is_audio_only):
            s_pass += 1
            print(f"[yellow]{icon_pass}{safe_title} [File Exist][/yellow]")
            continue

        progress = None
        task_id = None
        download_started = False

        def update_progress(status, pct):
            nonlocal progress, task_id, download_started
            if status == 'downloading':
                if not download_started:
                    download_started = True
                    progress = create_solid_bar()
                    progress.start()
                    task_id = progress.add_task(safe_title, total=100)

                if progress: progress.update(task_id, completed=pct)
            elif status == 'finished':
                if progress: progress.update(task_id, completed=100)

        if is_test_mode:
            mock_res = entry.get("mock_res")
            if mock_res == "Success":
                for pct in range(0, 101, 25):
                    update_progress('downloading', pct)
                    time.sleep(0.12)
                update_progress('finished', 100)
                result = "Success"
            elif mock_res == "Pass":
                time.sleep(0.15)
                result = "Pass"
            else:
                time.sleep(0.15)
                result = mock_res
        else:
            result = process_single_item(video_url, path, is_audio_only, progress_callback=update_progress)

        if result == "Success":
            s_success += 1
            if progress:
                progress.update(task_id, completed=100, description=f"[green]{safe_title}[/green]")
                progress.stop()
            else:
                print(f"[green]✔  {safe_title}[/green]")
        elif result == "Pass":
            s_pass += 1
            if progress: progress.stop()
            print(f"[yellow]{icon_pass}{safe_title} [File Exist][/yellow]")
        else:
            s_err += 1
            if progress: progress.stop()

            short_reason = _parse_error(result)
            print(f"[red]{icon_error}{safe_title} [Error][/red]")
            print(f"   [#6c7086]├─ Link: {display_url}[/#6c7086]")
            print(f"   [#6c7086]└─ Info: {short_reason}[/#6c7086]")

    stats_text = f"[green]✔ {s_success}[/green] | [yellow]» {s_pass}[/yellow] | [red]✖ {s_err}[/red]"
    print()
    print(_draw_box(stats_text, border_color="blue"))

    _wait_input()