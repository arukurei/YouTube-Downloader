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
    app = UniversalApp(
        logo=config.ASCII_LOGO,
        options=config.MENU_OPTIONS,
        version=config.VERSION,
        theme=config.THEME,
        on_select=action_router
    )
    app.run()