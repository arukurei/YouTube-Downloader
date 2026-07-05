VERSION = "v2.0.1"

ASCII_LOGO = r"""⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⣷⡿⠟⠛⠉⠉⠙⠻⢿⣿⣿⠷⠟⠋⠉⠉⠉⠻⢾⣗⠐⣾⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢿⣿⣿⣹⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣼⣿⣿⣯⢛⣿⣿⣿⣿⣿⣿⣿
⣿⡿⠟⠻⠿⠿⠿⠫⠽⡄⣴⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⢷⡾⠿⠟⠛⢻⠿
⢻⠃⠐⠁⠀⠀⠠⠄⡀⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⡿⣧⡀⠀⠀⠀⠀⠀
⠁⠀⠈⠀⠀⢠⣤⣾⣿⡿⣿⠃⠀⠀⣠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠻⣆⠉⢻⣦⡇⠀⠀⠀
⣶⣄⠀⢠⠀⣸⣿⣷⠟⣠⠃⠀⣠⠞⠁⣀⣀⣠⡀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠤⣀⣀⠀⠀⠀⠀⠳⣝⣦⡄⠹⢷⣤⠀⠀
⢹⣿⠀⢀⣼⡟⣲⣏⡞⠃⣴⣟⡥⠖⡹⠁⢀⡴⠃⢠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢄⠀⠨⣏⠒⠦⣀⠀⠈⢿⣿⡀⠾⣿⠀⠀
⣠⣿⠀⢸⣿⣿⣿⡟⠀⢠⠟⠁⣠⠞⢁⡴⠋⠀⠀⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄⠈⢳⡀⠈⠱⡄⠀⠻⣧⣰⣿⠀⠀
⣴⡇⠀⢸⡿⢿⣿⠁⣰⣿⠀⠀⣏⡴⠋⢀⠀⡄⢰⡇⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢤⡇⠀⠀⡇⠀⠀⢹⡿⠻⡇⠲
⣿⢷⣤⡟⠁⢰⡇⣰⣿⢻⠀⣰⣿⠁⢠⠃⠀⡇⢸⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⡆⠀⡀⠀⡄⢠⠀⠀⡄⠀⢹⣦⣠⠃⠀⠀⢸⠀⠀⣿⣀
⠟⢳⢠⠇⠀⢸⣇⣿⡏⠈⠋⢹⠇⢠⠇⠀⢀⡇⢸⡇⠀⣿⠀⠀⡀⢀⠀⠀⠀⡇⠀⡇⠀⡇⢸⡆⠀⠹⡀⠀⣇⠀⠀⠀⢣⢸⠀⠀⠘⣮
⠀⠀⢹⠀⠀⠀⢿⣿⠁⠀⠀⡏⢠⡟⠀⡴⢸⢹⢸⣇⠀⣿⡆⠀⡇⠘⣇⠀⠀⡇⢰⡇⢀⣿⡀⣿⣄⠀⢳⡀⢸⠀⠀⠀⢸⣸⠀⠀⠀⣿
⠀⠀⣼⠀⠀⠀⣼⣿⠀⠀⢸⢣⣿⠁⣰⣧⡇⠘⣜⣿⠀⠟⣿⠀⢱⠀⣿⠀⢠⣿⣼⡇⡸⠀⢳⣿⣿⣆⠘⣧⠈⡆⠀⠀⢸⣿⠀⠀⠀⣿
⠀⠀⣿⠀⠀⠀⣿⣿⠀⣇⠘⣿⡏⣰⣷⡿⣤⢄⣻⡝⣿⡆⢹⡄⠘⡄⣿⡄⢸⣿⢋⣷⣁⣀⣠⣿⡼⢿⣦⣿⣴⠁⠀⠀⣼⡏⠀⠀⠀⣿
⠀⠀⣿⠀⠀⠀⢿⠸⣄⢻⠸⠙⠿⢻⡟⠳⣾⠿⠟⣻⣿⣷⣶⣿⣆⢣⡏⣧⣿⡿⡾⢿⣿⣿⡟⢿⠗⠉⣿⣿⡇⠀⢀⢠⠋⡇⠀⠀⠀⣿
⠀⢠⣿⠀⠀⠀⢸⠀⠙⢿⠀⠀⠀⠀⢣⡀⠈⠀⠘⠿⠿⠀⠀⠈⢿⣾⣇⠸⠉⠁⠀⠘⠿⠿⠃⠀⠀⣰⠟⣿⠇⡄⢰⡟⠀⡇⠀⠀⢀⣿
⣷⡝⠼⣧⡀⠀⢸⡄⠀⠈⣇⢠⠀⠀⠘⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠇⡀⠀⣸⢷⣸⠀⣰⠃⠀⢀⣾⠙
⣿⣿⣦⣙⣻⣶⣶⣷⣤⣤⣿⣼⣷⡀⠀⠸⣿⣷⡦⡀⠀⠀⠀⠀⠀⣠⡄⠀⠀⠀⠀⠀⢀⡤⢾⣿⠇⣰⡇⢰⣿⣿⣿⣶⣿⣶⣿⣯⣽⣿
⣿⣿⣿⣿⣿⣿⡿⠿⠛⠛⠋⠙⣇⠙⣦⡀⠛⢿⣟⡦⠄⠀⠀⠀⠀⠛⠃⠀⠀⠀⠀⠀⠠⠖⣻⣧⡞⣹⣧⡏⠈⠉⠙⠛⠛⠻⠿⣿⣿⣿
⣍⡩⠿⠛⠋⠁⠀⠀⠀⠀⠀⢀⣬⡾⠛⣿⣿⢿⣟⢯⣄⠀⠀⠀⠀⠈⠉⠁⠀⠀⠀⣀⣴⣞⡿⠻⣿⡻⠟⢷⣄⡀⠀⠀⠀⠀⠀⠀⠈⠙
⠁⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡿⣍⣀⣾⠟⠙⠀⣹⠿⣿⣷⣦⡀⠀⠀⠀⠀⠀⡠⠞⣵⡿⠿⣅⠀⠙⢿⣄⠀⠉⠻⣦⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⡶⠟⠁⠀⣸⡿⠃⠀⠀⠀⠳⣄⠀⠁⠀⠈⠱⣦⣤⡴⠋⠀⠀⠀⠀⡠⠜⠀⠀⠀⠙⢷⣄⠀⠀⠙⢿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣸⡏⠀⠀⢀⣾⠋⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⢀⡠⠒⠉⠀⠀⠀⠀⠀⠀⠀⠙⣷⠀⠀⠀⢿⡆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢢⠀⠀⠀⠀⡰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡆⠀⠀⠘⣷⠀⠀⠀
⠀⠀⠀⠀⢀⣴⣧⣤⣄⣤⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠤⠤⠜⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣤⣤⣶⠟⠃⠀⡀"""

# Цветовая палитра интерфейса
THEME = {
    "background": "#1c1b29",
    "text": "#a9b2d3",
    "active": "#a6e3a1",
    "muted": "#6c7086"
}

# Список пунктов меню: ярлык кнопки и внутренний идентификатор действия
MENU_OPTIONS = [
    {"label": "Video Loader", "action": "video_download"},
    {"label": "Sound Loader", "action": "audio_download"},
    {"label": "Quit", "action": "quit"}
]

# Тестовые сценарии
MOCK_TEST_CASES = [
    {"title": "Successfully Downloaded Audio", "id": "dQw4w9WgXcQ", "mock_res": "Success"},
    {"title": "Already Existing Local File", "id": "oYv54tN2EEY", "mock_res": "Pass"},
    {"title": "Age Gated Content", "id": "g4mHPeMdgHQ", "mock_res": "Error: sign in to confirm your age"},
    {"title": "Private Music Playlist Video", "id": "76n27YFm5iA", "mock_res": "Error: This video is private"},
    {"title": "Deleted/Missing Video Source", "id": "deleted_vid", "mock_res": "Error: This video is unavailable"},
    {"title": "Country Blocked Stream", "id": "geoblocked1", "mock_res": "Error: geo restriction country"},
    {"title": "Unstable Connection Stream", "id": "neterror123", "mock_res": "Error: urlopen error timed out"},
    {"title": "Rate Limit Blocked Video", "id": "ratelimit99", "mock_res": "Error: HTTP Error 403: Forbidden"},
    {"title": "No Write Permission Folder", "id": "perm_denied", "mock_res": "Error: Permission denied"},
    {"title": "Drive Out of Space Error", "id": "nospace1234", "mock_res": "Error: No space left on device"},
    {"title": "Missing FFmpeg Postprocessor", "id": "no_ffmpeg_id", "mock_res": "Error: ffmpeg not found"},
    {"title": "Unidentified System Exception", "id": "unknown_err", "mock_res": "Error: Extractor exception traceback line"}
]