import os
import re
import sys
import time
import json
import shutil
import subprocess

from updater import get_ytdlp_binary_path

AUDIO_QUALITY = "192"                        # битрейт mp3, кбит/с
OUTPUT_FILENAME_TEMPLATE = "%(title)s.%(ext)s"  # шаблон имени файла для yt-dlp -o
EXTRACT_INFO_TIMEOUT = 25                    # сек, таймаут на получение инфы о видео
EXTRACT_INFO_RETRIES = 3                     # повторов при сетевых сбоях (инфо о видео)
DOWNLOAD_RETRIES = 3                         # повторов при сетевых сбоях (само скачивание)


def _find_ffmpeg() -> "str | None":
    """
    Ищет рабочий ffmpeg в таком порядке:
    1. os.path.dirname(sys.executable) - куда Nuitka кладёт файлы,
       встроенные через --include-data-files, ПРЯМО ВНУТРЬ собранного
       exe/AppImage (проверено вживую: работает и для --standalone,
       и для --onefile - в onefile-режиме именно туда распаковывается
       payload при каждом запуске).
    2. os.path.dirname(sys.argv[0]) - запасной вариант на случай, если
       файл лежит рядом с самим бинарником, а не встроен внутрь.
    3. portable_ffmpeg.get_ffmpeg() - для dev-режима (`python code/main.py`,
       не собранный exe). ВАЖНО: используется именно portable_ffmpeg, а не
       imageio_ffmpeg - тот отдаёт только ffmpeg без ffprobe, а ffprobe
       обязателен для вшивания обложки в mp4 (см. _cleanup_leftovers и
       комментарий в process_single_item - проверено вживую на реальной
       ошибке "ffprobe not found").
    4. Системный ffmpeg из PATH - последний шанс.

    В обоих случаях (1)/(2) предполагается, что ffprobe лежит В ТОЙ ЖЕ
    папке, что и ffmpeg - yt-dlp сам ищет ffprobe рядом с переданным
    --ffmpeg-location (проверено вживую через FFmpegPostProcessor).
    Собственно копирование обоих файлов рядом - забота build-скриптов
    (compile.sh/build.yml), не этой функции.
    """
    for base_getter in (lambda: os.path.dirname(sys.executable),
                        lambda: os.path.dirname(os.path.abspath(sys.argv[0]))):
        try:
            base_dir = base_getter()
            candidate = os.path.join(base_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if os.path.isfile(candidate):
                return candidate
        except Exception:
            continue

    try:
        from portable_ffmpeg import get_ffmpeg
        ffmpeg_path, _ffprobe_path = get_ffmpeg()
        if ffmpeg_path and os.path.isfile(ffmpeg_path):
            return ffmpeg_path
    except Exception:
        pass

    return shutil.which("ffmpeg")


FFMPEG_PATH = _find_ffmpeg()

# Признаки сетевых/временных ошибок, при которых имеет смысл повторить попытку
RETRYABLE_MARKERS = (
    "urlopen error", "timed out", "timeout", "connection reset",
    "connection aborted", "connection refused", "temporary failure",
    "network is unreachable", "remote end closed", "reset by peer",
    "http error 500", "http error 502", "http error 503", "http error 429",
    "econnreset", "ebusy",
)

_POPEN_FLAGS = 0
if os.name == "nt": _POPEN_FLAGS = subprocess.CREATE_NO_WINDOW


def _is_retryable(text: str) -> bool:
    low = (text or "").lower()
    return any(marker in low for marker in RETRYABLE_MARKERS)


def _last_meaningful_line(text: str) -> str:
    if not text: return "Error: unknown yt-dlp failure"
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines: return "Error: unknown yt-dlp failure"
    # yt-dlp обычно кладёт саму ошибку в последнюю строку stderr
    line = lines[-1]
    return line if line.lower().startswith("error") else f"Error: {line}"


def _run_capture(args, timeout=None):
    ytdlp_path = get_ytdlp_binary_path()
    if not ytdlp_path or not os.path.exists(ytdlp_path): return 127, "", "Error: yt-dlp is not installed or unavailable"
    try:
        proc = subprocess.run(
            [ytdlp_path] + args,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout, creationflags=_POPEN_FLAGS,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Error: operation timed out"
    except Exception as e:
        return 1, "", f"Error: {e}"


def _run_streaming(args, on_line, timeout=None):
    """
    Запускает yt-dlp и построчно отдаёт вывод в on_line(line).

    ВАЖНО: stderr смерджен в тот же поток, что и stdout (stderr=STDOUT).
    Проверено вживую: когда среди args присутствует --print, yt-dlp
    переносит ВЕСЬ обычный вывод (статусы, --progress-template) в stderr,
    оставляя stdout исключительно под сам --print - иначе progress-callback
    никогда бы не вызывался. Раз содержимое обоих потоков всё равно нужно
    для парсинга прогресса/ошибок, различать их не требуется.
    """
    ytdlp_path = get_ytdlp_binary_path()
    if not ytdlp_path or not os.path.exists(ytdlp_path): return 127, "Error: yt-dlp is not installed or unavailable"

    output_lines = []
    try:
        env = os.environ.copy()
        # КРИТИЧНО для живого прогресс-бара: yt-dlp - Python-программа и сама
        # буферизует свой вывод блоками, когда пишет не в терминал, а в pipe
        # (стандартное поведение CPython для non-tty stdout/stderr). Без этой
        # переменной все строки прогресса прилетают одним куском в самом
        # конце вместо реального времени - проверено вживую на локальном
        # тестовом сервере: без PYTHONUNBUFFERED все строки имеют идентичный
        # таймстемп независимо от реальной длительности скачивания.
        env["PYTHONUNBUFFERED"] = "1"
        proc = subprocess.Popen(
            [ytdlp_path] + args,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            bufsize=1, creationflags=_POPEN_FLAGS, env=env,
        )
    except Exception as e:
        return 1, f"Error: {e}"

    start = time.time()
    try:
        while True:
            line = proc.stdout.readline()
            if line:
                clean = line.rstrip("\n")
                output_lines.append(clean)
                on_line(clean)
                continue
            if proc.poll() is not None:
                break
            if timeout and (time.time() - start) > timeout:
                proc.kill()
                return 1, "Error: operation timed out (stalled download)"
    except Exception as e:
        try:
            proc.kill()
        except Exception:
            pass
        return 1, f"Error: {e}"

    return proc.returncode, "\n".join(output_lines)


def extract_info(url: str, timeout: int = EXTRACT_INFO_TIMEOUT, retries: int = EXTRACT_INFO_RETRIES):
    """
    Возвращает (entries, error).
    entries - список dict (id/title/url и т.п.), один элемент для одиночного
    видео, несколько - для плейлиста. Работает единообразно благодаря
    --flat-playlist (для одиночного видео он не влияет на результат).
    """
    args = ["--flat-playlist", "--dump-json", "--no-warnings",
            "--ignore-no-formats-error", "--no-check-certificates", url]

    last_err = "Error: unknown failure"
    for attempt in range(retries):
        rc, out, err = _run_capture(args, timeout=timeout)

        if rc == 0 and out.strip():
            entries = []
            for line in out.strip().splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            if entries:return entries, None
            return None, "Error: no valid videos found"

        last_err = _last_meaningful_line(err or out)
        if not _is_retryable(last_err) or attempt == retries - 1: break
        time.sleep(1.5 * (attempt + 1))

    return None, last_err


def process_single_item(url: str, output_dir: str, is_audio_only: bool, progress_callback=None, retries: int = DOWNLOAD_RETRIES):
    outtmpl = os.path.join(output_dir, OUTPUT_FILENAME_TEMPLATE)

    args = [
        "--newline", "--no-warnings", "--no-check-certificates",
        "-o", outtmpl,
        # Только --embed-thumbnail (без --write-thumbnail) значит "встроить
        # обложку И удалить отдельный файл после" - по документации yt-dlp
        # это тот же принцип, что --embed-subs без --write-subs для субтитров.
        "--embed-thumbnail", "--add-metadata",
        "--progress-template",
        "download:__PROG__ %(progress.downloaded_bytes)s %(progress.total_bytes)s",
        # ВАЖНО: --print сюда НЕ добавлять. Проверено вживую: при наличии
        # --print yt-dlp подавляет ВЕСЬ обычный вывод (статусы, прогресс) -
        # остаётся только сам --print. Раньше здесь был --print для
        # получения финального пути файла, но это значение нигде не
        # использовалось, а прогресс-бар из-за этого никогда не показывался.
    ]
    if FFMPEG_PATH: args += ["--ffmpeg-location", FFMPEG_PATH]

    if is_audio_only: args += ["-f", "bestaudio/best", "-x", "--audio-format", "mp3", "--audio-quality", AUDIO_QUALITY]
    else:             args += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]

    args.append(url)

    def parse_progress_line(line: str):
        if line.startswith("[download] Destination:"):
            destination_holder[0] = line.split("Destination:", 1)[1].strip()
            return
        if not line.startswith("__PROG__"): return
        parts = line.split()
        try:
            downloaded = float(parts[1]) if len(parts) > 1 and parts[1] != "NA" else 0.0
            total = float(parts[2]) if len(parts) > 2 and parts[2] != "NA" else 0.0
        except (ValueError, IndexError):
            downloaded, total = 0.0, 0.0
        if progress_callback:
            pct = min(100.0, (downloaded / total) * 100) if total > 0 else 0.0
            progress_callback("downloading", pct)

    destination_holder = [None]
    last_err = "Error: unknown failure"
    for attempt in range(retries):
        rc, err_tail = _run_streaming(args, on_line=parse_progress_line, timeout=None)

        if rc == 0:
            if progress_callback: progress_callback("finished", 100)
            return "Success"

        last_err = _last_meaningful_line(err_tail)

        # yt-dlp резюмирует докачку сам (.part-файлы), поэтому повтор всей
        # команды безопасен - не начинает скачивание с нуля без необходимости
        if not _is_retryable(last_err) or attempt == retries - 1: break
        time.sleep(2.0 * (attempt + 1))

    _cleanup_leftovers(output_dir, destination_holder[0], is_audio_only)
    return last_err


def _cleanup_leftovers(output_dir: str, destination_path: "str | None", is_audio_only: bool):
    """
    Если скачивание в итоге провалилось - подчищает недокачанные обрывки
    (.part, промежуточные .webp/.jpg до конвертации/эмбеда, и т.п.), чтобы
    в папке не копился мусор от неудачных попыток. Аналог cleanup-логики
    из старой версии на чистом Python API (там был доступен ydl.prepare_filename,
    здесь используем строку "[download] Destination: ..." из вывода yt-dlp).
    Никогда не бросает исключение - максимум, ничего не почистит.
    """
    if not destination_path:
        return
    try:
        base_name, _ = os.path.splitext(os.path.basename(destination_path))
        final_ext = ".mp3" if is_audio_only else ".mp4"
        if not os.path.isdir(output_dir): return
        for file in os.listdir(output_dir):
            if file.startswith(base_name) and not file.endswith(final_ext):
                try:
                    os.remove(os.path.join(output_dir, file))
                except Exception:
                    pass
    except Exception:
        pass


def sanitize_filename_basic(name: str) -> str:
    """
    Упрощённая замена yt_dlp.utils.sanitize_filename (та была доступна только
    при импорте yt-dlp как Python-библиотеки, теперь yt-dlp - внешний бинарник).
    Не претендует на 100%-ное совпадение с внутренней санитацией yt-dlp,
    но достаточно для эвристической проверки "файл уже скачан".
    """
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = name.strip(" .")
    return name or "video"