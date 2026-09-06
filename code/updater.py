"""
Обеспечивает наличие рабочего бинарника yt-dlp.

Логика (в порядке приоритета):
1. Пробуем узнать последнюю версию через GitHub API (короткий таймаут).
2. Если версия новая (или бинарника ещё нет вообще) - скачиваем ассет,
   подходящий под текущую ОС, атомарно (tmp-файл + os.replace) заменяем
   старый бинарник.
3. Если скачать не удалось (нет сети, GitHub недоступен, антивирус
   заблокировал) - используем уже закэшированный бинарник, если он есть.
4. Если ни кэша, ни сети нет (самый первый запуск офлайн) - копируем
   бинарник, зашитый рядом с самим приложением при сборке (см. build.yml,
   папка ytdlp_bundled/).
5. Если и этого нет - возвращаем None и понятное сообщение об ошибке.
   Программа НЕ падает с трейсбеком, а показывает юзеру, что делать.
"""

import os
import re
import time
import shutil
import stat
import platform
import urllib.request
import urllib.error

REPO = "yt-dlp/yt-dlp"
CHECK_TIMEOUT = 5.0
DOWNLOAD_TIMEOUT = 60.0
# Обычный браузерный User-Agent - без него некоторые прокси/WAF отдают 403.
USER_AGENT = "Mozilla/5.0 (compatible; loader-app-updater/1.0)"
# Сколько последних строк лога обновлений хранить (чтобы файл не рос вечно)
LOG_MAX_LINES = 200


def get_app_dir() -> str:
    if os.name == "nt": base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:               base = os.path.join(os.path.expanduser("~"), ".config")
    d = os.path.join(base, "YTD", "bin")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        d = os.path.expanduser("~")
    return d


def _asset_and_local_names():
    """Имя ассета в релизе GitHub -> имя файла у нас на диске."""
    system = platform.system()
    if system == "Windows":  return "yt-dlp.exe", "yt-dlp.exe"
    elif system == "Darwin": return "yt-dlp_macos", "yt-dlp"
    else:                    return "yt-dlp", "yt-dlp"


def get_ytdlp_binary_path() -> str:
    """Путь, по которому бинарник должен лежать (не гарантирует, что он там есть)."""
    _, local_name = _asset_and_local_names()
    return os.path.join(get_app_dir(), local_name)


def _version_file_path() -> str:
    return os.path.join(get_app_dir(), "version.txt")


def _read_current_version() -> str:
    vf = _version_file_path()
    if os.path.exists(vf):
        try:
            with open(vf, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return ""


def _write_current_version(ver: str):
    try:
        with open(_version_file_path(), "w", encoding="utf-8") as f:
            f.write(ver)
    except Exception:
        pass


def get_current_version() -> str:
    """
    Публичный геттер версии yt-dlp, которая реально стоит прямо сейчас
    (то, что записано в version.txt после последнего успешного скачивания).
    Пустая строка, если версия ещё неизвестна (самый первый запуск).
    """
    return _read_current_version()


def _log_file_path() -> str:
    return os.path.join(get_app_dir(), "update_log.txt")


def _log_event(message: str):
    """
    Пишет событие с таймстемпом в персистентный лог обновлений - чтобы
    и юзер, и разработчик могли посмотреть историю попыток (успешных и
    неуспешных) не в моменте, а спустя недели, без необходимости
    воспроизводить живую сессию. Автоматически подрезает файл до
    LOG_MAX_LINES последних строк. Никогда не бросает исключение.
    """
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        log_path = _log_file_path()

        lines = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                lines = []

        lines.append(line)
        lines = lines[-LOG_MAX_LINES:]

        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception:
        pass


def get_log_file_path() -> str:
    """Публичный геттер пути к логу обновлений - для показа юзеру, где искать."""
    return _log_file_path()


def _make_executable(path: str):
    if os.name == "nt": return
    try:
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass


class _StopAtFirstRedirect(urllib.request.HTTPRedirectHandler):
    """Не идёт дальше первого 30x - иначе urlopen сам утащит нас через все
    хопы вплоть до подписанной CDN-ссылки release-assets.githubusercontent.com,
    в которой версии релиза уже нет."""
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None


def _fetch_latest_release_info():
    """
    Возвращает (tag_name, download_url) либо (None, None) при любой проблеме.

    Намеренно НЕ используется api.github.com/repos/.../releases/latest:
    у него общий лимит 60 запросов/час на IP, и если много юзеров сидят
    за одним NAT/офисным IP, они быстро упрутся в 403 "rate limit exceeded"
    (см. историю разработки - это не гипотетическая, а воспроизведённая
    на практике проблема).

    Вместо этого используется постоянная ссылка
    github.com/OWNER/REPO/releases/latest/download/<asset>, которая всегда
    редиректит на актуальный релиз и НЕ считается в лимит API. Редирект
    перехватывается на первом хопе (там ещё виден тег версии в пути), а не
    после docs.geturl() - до финальной CDN-ссылки, где тега уже нет.
    """
    asset_name, _ = _asset_and_local_names()
    convenience_url = f"https://github.com/{REPO}/releases/latest/download/{asset_name}"
    opener = urllib.request.build_opener(_StopAtFirstRedirect)
    req = urllib.request.Request(convenience_url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        opener.open(req, timeout=CHECK_TIMEOUT)
        # если сюда дошли без исключения - редиректа не было (странно, но не наш случай)
        return None, None
    except urllib.error.HTTPError as e:
        if e.code not in (301, 302, 303, 307, 308): return None, None
        location = e.headers.get("Location")
        if not location: return None, None
        match = re.search(r"/releases/download/([^/]+)/", location)
        tag = match.group(1) if match else None
        return tag, convenience_url
    except Exception:
        return None, None


def _download_binary(url: str, target_path: str) -> bool:
    tmp_path = target_path + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp, open(tmp_path, "wb") as out:
            shutil.copyfileobj(resp, out)
        if os.path.getsize(tmp_path) < 1_000_000:
            # GitHub мог отдать HTML-страницу ошибки вместо бинарника - отбраковываем
            raise ValueError("downloaded file suspiciously small, likely not a real binary")
        _make_executable(tmp_path)
        os.replace(tmp_path, target_path)  # атомарная замена на всех ОС
        return True
    except Exception:
        try:
            if os.path.exists(tmp_path): os.remove(tmp_path)
        except Exception:
            pass
        return False


def ensure_ytdlp(status_callback=None) -> tuple:
    """
    Гарантирует наличие рабочего бинарника yt-dlp.
    Возвращает (path_or_None, message). Никогда не бросает исключение.

    Каждое решение (обновил / использовал кэш / не смог) логируется в
    персистентный файл (см. get_log_file_path()) - чтобы можно было
    проверить историю обновлений спустя недели, а не только в моменте.
    """
    def notify(msg):
        if status_callback:
            try:
                status_callback(msg)
            except Exception:
                pass

    target_path = get_ytdlp_binary_path()
    already_have = os.path.exists(target_path)
    current_ver = _read_current_version()

    notify("Checking for yt-dlp updates...")
    latest_ver, download_url = _fetch_latest_release_info()

    if latest_ver is None: _log_event(f"Could not reach GitHub to check latest version (cached: {current_ver or 'none'})")

    needs_download = download_url and (not already_have or latest_ver != current_ver)

    if needs_download:
        notify(f"Downloading yt-dlp {latest_ver}...")
        if _download_binary(download_url, target_path):
            if latest_ver: _write_current_version(latest_ver)
            _log_event(f"Updated: {current_ver or 'none'} -> {latest_ver}")
            return target_path, f"yt-dlp updated to {latest_ver}"
        # скачивание не удалось - тихо падаем обратно на то, что уже есть
        _log_event(f"Download of {latest_ver} failed, falling back to cached {current_ver or 'none'}")

    if os.path.exists(target_path):
        if latest_ver and latest_ver == current_ver:  _log_event(f"Already up to date: {current_ver}")
        else:                                         _log_event(f"Using cached version: {current_ver or '(unknown)'}")
        return target_path, f"using yt-dlp {current_ver or '(unknown version)'}"

    _log_event("FATAL: no cached binary and no network on very first run")
    return None, (
        "yt-dlp is not available: no internet connection on first run and "
        "no cached copy found. Connect to the internet once and restart the app."
    )