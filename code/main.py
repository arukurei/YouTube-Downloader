#! /usr/bin/env python3
import curses
import getpass
import os
import subprocess
from curses import wrapper
from solo_video_loader import solo_video_loader
from solo_sound_loader import solo_sound_loader
from playlist_video_loader import playlist_video_loader
from playlist_sound_loader import playlist_sound_loader


path = os.path.abspath("resize")
subprocess.call([path, '-s', '40', '100'])
pointo = ['Solo Video Loader', 'Solo Sound Loader', 'Playlist Video Loader', 'Playlist Sound Loader', 'Quite']

def menu(console, w, indento, selected_row_index):
    for index, row in enumerate(pointo):
        x = w // 2 - len(row) // 2
        y = indento + 3 + index * 2
        if index == selected_row_index:
            # console.addstr(y, x - 2, "> ", curses.color_pair(1))
            console.addstr(y, x, row, curses.color_pair(2))
            # console.addstr(y, x + len(row), " <", curses.color_pair(1))
        else:
            console.addstr(y, x, row, curses.color_pair(1))


def logo(console, h, w):
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
    x = w // 2 - len(art_lines[0]) // 2
    y = h // 2

    for y, line in enumerate(art_lines, 2):
        console.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)
    return y


def main(console):
    # disable cursor blinking, set and get screen size
    curses.curs_set(0)
    curses.def_prog_mode()
    console.resize(40, 100)
    h, w = console.getmaxyx()

    # color
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # draw
    selected_row_index = 0
    indento = logo(console, h, w)
    menu(console, w, indento, selected_row_index)

    while True:
        key = console.getch()

        # clear the screen
        console.clear()

        if key == curses.KEY_UP and selected_row_index > 0:
            selected_row_index -= 1
        elif key == curses.KEY_DOWN and selected_row_index < len(pointo) - 1:
            selected_row_index += 1
        elif key == 10 or key == curses.KEY_ENTER:
            if selected_row_index == 4:
                break
            elif selected_row_index == 0:
                curses.endwin()
                os.system('clear')
                solo_video_loader()
                getpass.getpass("\033[5mPress Enter to continue \033[0m")
            elif selected_row_index == 1:
                curses.endwin()
                os.system('clear')
                solo_sound_loader()
                getpass.getpass("\033[5mPress Enter to continue \033[0m")
            elif selected_row_index == 2:
                curses.endwin()
                os.system('clear')
                playlist_video_loader()
                getpass.getpass("\033[5mPress Enter to continue \033[0m")
            elif selected_row_index == 3:
                curses.endwin()
                os.system('clear')
                playlist_sound_loader()
                getpass.getpass("\033[5mPress Enter to continue \033[0m")
        if key == curses.KEY_RESIZE:
            subprocess.call([path, '-s', '40', '100'])
            console.resize(40, 100)

        # draw
        indento = logo(console, h, w)
        menu(console, w, indento, selected_row_index)

        # update the screen
        console.refresh()

wrapper(main)
os.system('clear')
