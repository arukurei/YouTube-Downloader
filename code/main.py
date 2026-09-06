import sys

from updater import ensure_ytdlp, get_current_version


def _startup_check():
    """
    Проверяет/качает yt-dlp ДО запуска TUI. Никогда не бросает исключение -
    если что-то пошло не так, просто печатает причину и программа продолжает
    (ошибка потом покажется юзеру уже внутри UI при попытке скачать видео).

    Возвращаемое сообщение ("yt-dlp updated to ..." / "using yt-dlp ..." /
    ошибка) видно ТОЛЬКО в консоли до запуска Textual - сам Textual сразу
    переключается в альтернативный экран и эта строка исчезает из виду.
    Поэтому версия yt-dlp дополнительно передаётся в UI (см. ниже) - так
    и юзер, и разработчик при саппорте всегда видят её прямо на экране,
    без необходимости смотреть консоль или лог.
    """
    try:
        path, message = ensure_ytdlp()
        print(f"[YTD] {message}")
        return path
    except Exception as e:
        print(f"[YTD] startup check failed unexpectedly: {e}")
        return None


_startup_check()

import config
from menu import UniversalApp
from downloader import handle_download


def action_router(app, selected_option):
    action = selected_option.get("action")

    if action == "quit":
        app.exit()
    elif action == "video_download":
        with app.suspend():
            handle_download(is_audio_only=False)
    elif action == "audio_download":
        with app.suspend():
            handle_download(is_audio_only=True)


if __name__ == "__main__":
    ytdlp_version = get_current_version()
    version_label = f"{config.VERSION} | yt-dlp {ytdlp_version}" if ytdlp_version else f"{config.VERSION} | yt-dlp unavailable"

    app = UniversalApp(
        logo=config.ASCII_LOGO,
        options=config.MENU_OPTIONS,
        version=version_label,
        theme=config.THEME,
        on_select=action_router
    )
    app.run()