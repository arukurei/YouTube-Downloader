#! /usr/bin/env python3
import curses
import os
import subprocess
from curses import wrapper
from handlers import (
    solo_video_loader,
    solo_sound_loader,
    playlist_video_loader,
    playlist_sound_loader
)

MENU_ITEMS = [
    'Solo Video Loader',
    'Solo Sound Loader',
    'Playlist Video Loader',
    'Playlist Sound Loader',
    'Quit'
]


def draw_menu(console, h, w, selected_row_index, logo_height):
    for index, row in enumerate(MENU_ITEMS):
        x = w // 2 - len(row) // 2
        y = logo_height + 3 + index * 2

        style = curses.color_pair(2) if index == selected_row_index else curses.color_pair(1)
        console.addstr(y, x, row, style)


def draw_logo(console, h, w):
    art = ("⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⣷⡿⠟⠛⠉⠉⠙⠻⢿⣿⣿⠷⠟⠋⠉⠉⠉⠻⢾⣗⠐⣾⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"
           "\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢿⣿⣿⣹⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣼⣿⣿⣯⢛⣿⣿⣿⣿⣿⣿⣿"
           "\n⣿⡿⠟⠻⠿⠿⠿⠫⠽⡄⣴⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⢷⡾⠿⠟⠛⢻⠿"
           "\n⢻⠃⠐⠁⠀⠀⠠⠄⡀⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⡿⣧⡀⠀⠀⠀⠀⠀"
           "\n⠁⠀⠈⠀⠀⢠⣤⣾⣿⡿⣿⠃⠀⠀⣠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠻⣆⠉⢻⣦⡇⠀⠀⠀"
           "\n⣶⣄⠀⢠⠀⣸⣿⣷⠟⣠⠃⠀⣠⠞⠁⣀⣀⣠⡀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠤⣀⣀⠀⠀⠀⠀⠳⣝⣦⡄⠹⢷⣤⠀⠀"
           "\n⢹⣿⠀⢀⣼⡟⣲⣏⡞⠃⣴⣟⡥⠖⡹⠁⢀⡴⠃⢠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢄⠀⠨⣏⠒⠦⣀⠀⠈⢿⣿⡀⠾⣿⠀⠀"
           "\n⣠⣿⠀⢸⣿⣿⣿⡟⠀⢠⠟⠁⣠⠞⢁⡴⠋⠀⠀⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄⠈⢳⡀⠈⠱⡄⠀⠻⣧⣰⣿⠀⠀"
           "\n⣴⡇⠀⢸⡿⢿⣿⠁⣰⣿⠀⠀⣏⡴⠋⢀⠀⡄⢰⡇⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢤⡇⠀⠀⡇⠀⠀⢹⡿⠻⡇⠲"
           "\n⣿⢷⣤⡟⠁⢰⡇⣰⣿⢻⠀⣰⣿⠁⢠⠃⠀⡇⢸⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⡆⠀⡀⠀⡄⢠⠀⠀⡄⠀⢹⣦⣠⠃⠀⠀⢸⠀⠀⣿⣀"
           "\n⠟⢳⢠⠇⠀⢸⣇⣿⡏⠈⠋⢹⠇⢠⠇⠀⢀⡇⢸⡇⠀⣿⠀⠀⡀⢀⠀⠀⠀⡇⠀⡇⠀⡇⢸⡆⠀⠹⡀⠀⣇⠀⠀⠀⢣⢸⠀⠀⠘⣮"
           "\n⠀⠀⢹⠀⠀⠀⢿⣿⠁⠀⠀⡏⢠⡟⠀⡴⢸⢹⢸⣇⠀⣿⡆⠀⡇⠘⣇⠀⠀⡇⢰⡇⢀⣿⡀⣿⣄⠀⢳⡀⢸⠀⠀⠀⢸⣸⠀⠀⠀⣿"
           "\n⠀⠀⣼⠀⠀⠀⣼⣿⠀⠀⢸⢣⣿⠁⣰⣧⡇⠘⣜⣿⠀⠟⣿⠀⢱⠀⣿⠀⢠⣿⣼⡇⡸⠀⢳⣿⣿⣆⠘⣧⠈⡆⠀⠀⢸⣿⠀⠀⠀⣿"
           "\n⠀⠀⣿⠀⠀⠀⣿⣿⠀⣇⠘⣿⡏⣰⣷⡿⣤⢄⣻⡝⣿⡆⢹⡄⠘⡄⣿⡄⢸⣿⢋⣷⣁⣀⣠⣿⡼⢿⣦⣿⣴⠁⠀⠀⣼⡏⠀⠀⠀⣿"
           "\n⠀⠀⣿⠀⠀⠀⢿⠸⣄⢻⠸⠙⠿⢻⡟⠳⣾⠿⠟⣻⣿⣷⣶⣿⣆⢣⡏⣧⣿⡿⡾⢿⣿⣿⡟⢿⠗⠉⣿⣿⡇⠀⢀⢠⠋⡇⠀⠀⠀⣿"
           "\n⠀⢠⣿⠀⠀⠀⢸⠀⠙⢿⠀⠀⠀⠀⢣⡀⠈⠀⠘⠿⠿⠀⠀⠈⢿⣾⣇⠸⠉⠁⠀⠘⠿⠿⠃⠀⠀⣰⠟⣿⠇⡄⢰⡟⠀⡇⠀⠀⢀⣿"
           "\n⣷⡝⠼⣧⡀⠀⢸⡄⠀⠈⣇⢠⠀⠀⠘⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠇⡀⠀⣸⢷⣸⠀⣰⠃⠀⢀⣾⠙"
           "\n⣿⣿⣦⣙⣻⣶⣶⣷⣤⣤⣿⣼⣷⡀⠀⠸⣿⣷⡦⡀⠀⠀⠀⠀⠀⣠⡄⠀⠀⠀⠀⠀⢀⡤⢾⣿⠇⣰⡇⢰⣿⣿⣿⣶⣿⣶⣿⣯⣽⣿"
           "\n⣿⣿⣿⣿⣿⣿⡿⠿⠛⠛⠋⠙⣇⠙⣦⡀⠛⢿⣟⡦⠄⠀⠀⠀⠀⠛⠃⠀⠀⠀⠀⠀⠠⠖⣻⣧⡞⣹⣧⡏⠈⠉⠙⠛⠛⠻⠿⣿⣿⣿"
           "\n⣍⡩⠿⠛⠋⠁⠀⠀⠀⠀⠀⢀⣬⡾⠛⣿⣿⢿⣟⢯⣄⠀⠀⠀⠀⠈⠉⠁⠀⠀⠀⣀⣴⣞⡿⠻⣿⡻⠟⢷⣄⡀⠀⠀⠀⠀⠀⠀⠈⠙"
           "\n⠁⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡿⣍⣀⣾⠟⠙⠀⣹⠿⣿⣷⣦⡀⠀⠀⠀⠀⠀⡠⠞⣵⡿⠿⣅⠀⠙⢿⣄⠀⠉⠻⣦⣄⠀⠀⠀⠀⠀⠀"
           "\n⠀⠀⠀⠀⠀⠀⠀⣠⡶⠟⠁⠀⣸⡿⠃⠀⠀⠀⠳⣄⠀⠁⠀⠈⠱⣦⣤⡴⠋⠀⠀⠀⠀⡠⠜⠀⠀⠀⠙⢷⣄⠀⠀⠙⢿⣦⠀⠀⠀⠀"
           "\n⠀⠀⠀⠀⠀⠀⣸⡏⠀⠀⢀⣾⠋⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⢀⡠⠒⠉⠀⠀⠀⠀⠀⠀⠀⠙⣷⠀⠀⠀⢿⡆⠀⠀⠀"
           "\n⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢢⠀⠀⠀⠀⡰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡆⠀⠀⠘⣷⠀⠀⠀"
           "\n⠀⠀⠀⠀⢀⣴⣧⣤⣄⣤⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠤⠤⠜⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣤⣤⣶⠟⠃⠀⡀")

    art_lines = art.splitlines()
    x = max(0, w // 2 - len(art_lines[0]) // 2)

    for y, line in enumerate(art_lines, 2):
        if y < h: console.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)
    return y


def main(console):
    curses.curs_set(0)
    curses.def_prog_mode()

    try:
        console.resize(40, 100)
    except:
        pass  # Игнорируем ошибку, если терминал не дает менять размер

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    selected_index = 0
    h, w = console.getmaxyx()
    logo_h = draw_logo(console, h, w)
    draw_menu(console, h, w, selected_index, logo_h)

    while True:
        key = console.getch()
        console.clear()

        if key == curses.KEY_RESIZE: h, w = console.getmaxyx()

        if key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(MENU_ITEMS) - 1:
            selected_index += 1

        ## Выбор
        elif key == 10 or key == curses.KEY_ENTER:
            if selected_index == 4:  break

            # Временный выход из Curses для работы с input()
            curses.endwin()
            os.system('clear')

            if selected_index == 0: solo_video_loader()
            elif selected_index == 1: solo_sound_loader()
            elif selected_index == 2: playlist_video_loader()
            elif selected_index == 3: playlist_sound_loader()

            # Возвращаемся в Curses
            console.refresh()
        logo_h = draw_logo(console, h, w)
        draw_menu(console, h, w, selected_index, logo_h)
        console.refresh()


if __name__ == "__main__":
    temp_path = os.path.abspath(__file__)
    temp_dir = os.path.dirname(temp_path)
    path = os.path.join(temp_dir, 'resize')
    if os.path.exists(path): subprocess.call([path, '-s', '40', '100'])

    try:
        wrapper(main)
    except KeyboardInterrupt:
        pass # Корректный выход при Ctrl+C
    finally:
        os.system('clear')