#! /usr/bin/env python3
import curses
import os
import subprocess
from curses import wrapper

from handlers import solo_video_loader, solo_sound_loader, playlist_video_loader, playlist_sound_loader


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


MENU_ACTIONS = [
    {"label": "Solo Video Loader", "callback": solo_video_loader},
    {"label": "Solo Sound Loader", "callback": solo_sound_loader},
    {"label": "Playlist Video Loader", "callback": playlist_video_loader},
    {"label": "Playlist Sound Loader", "callback": playlist_sound_loader},
    {"label": "Quit", "callback": None}  # None сигнализирует о выходе
]


class AppManager:
    def __init__(self, console):
        self.console = console
        self.selected_idx = 0
        self.resize_path = os.path.abspath("resize")
        self.setup_curses()

    def setup_curses(self):
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, 255, -1)  # Обычный текст
        curses.init_pair(2, 0, 255)  # Выделенный текст
        self.apply_resize()

    def apply_resize(self):
        """Применяет системное изменение размера окна."""
        if os.path.exists(self.resize_path):
            subprocess.call([self.resize_path, '-s', '40', '100'])
        self.console.resize(40, 100)
        self.h, self.w = self.console.getmaxyx()

    def draw_logo(self):
        art_lines = ASCII_LOGO.splitlines()
        start_y = 2
        for i, line in enumerate(art_lines):
            x = max(0, self.w // 2 - len(line) // 2)
            self.console.addstr(start_y + i, x, line, curses.color_pair(2) | curses.A_BOLD)
        return start_y + len(art_lines)

    def draw_menu(self, start_y):
        for index, item in enumerate(MENU_ACTIONS):
            label = item["label"]
            x = self.w // 2 - len(label) // 2
            y = start_y + 2 + (index * 2)

            style = curses.color_pair(2) if index == self.selected_idx else curses.color_pair(1)
            self.console.addstr(y, x, label, style)

    def execute_action(self):
        action = MENU_ACTIONS[self.selected_idx]["callback"]
        if action is None: return False  # Выход

        curses.endwin()
        os.system('clear')

        try:
            action()
        except Exception as e:
            print(f"Error executing action: {e}")

        # Возврат в curses mode
        self.console.clear()
        return True

    def run(self):
        while True:
            self.console.clear()
            next_y = self.draw_logo()
            self.draw_menu(next_y)
            self.console.refresh()

            key = self.console.getch()

            if key == curses.KEY_UP and self.selected_idx > 0:
                self.selected_idx -= 1
            elif key == curses.KEY_DOWN and self.selected_idx < len(MENU_ACTIONS) - 1:
                self.selected_idx += 1
            elif key in [10, curses.KEY_ENTER]:
                should_continue = self.execute_action()
                if not should_continue:
                    break
            elif key == curses.KEY_RESIZE:
                self.apply_resize()


def main(console):
    app = AppManager(console)
    app.run()


if __name__ == "__main__":
    wrapper(main)
    os.system('clear')