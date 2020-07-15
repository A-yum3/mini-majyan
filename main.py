import traceback

import pygame as pg
from pygame import display, draw
from pygame.locals import *

from client import *
from network import Network
from player import *
from settings import *
from tile import *

pg.font.init()
pg.init()
pg.mixer.init()
win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)


def main():
    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(60)
        game = n.send("get")
        if game.connected():
            Client(n, win)
        else:
            waiting_screen()
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False


def waiting_screen():
    font = pg.font.SysFont("comicsans", 80)
    text = font.render("Waiting for Player...", 1, (255, 0, 0), True)
    win.blit(text, (int(WIDTH/2 - text.get_width() /
                        2), int(HEIGHT/2 - text.get_height()/2)))


def menu_screen():
    global n
    global player_no
    run = True
    clock = pg.time.Clock()
    offline = False

    while run:
        clock.tick(60)
        # メニュー画面描写
        win.fill((128, 128, 128))
        font = pg.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        small_font = pg.font.SysFont("comicsans", 50)
        win.blit(text, (100, 200))

        if offline:
            off = small_font.render(
                "Server Offline, Try Again Later...", 1, (255, 0, 0))
            win.blit(off, (int(WIDTH / 2 - off.get_width() / 2), 500))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                try:
                    n = Network()
                    player_no = n.getP()
                    # TODO: ここの調整
                    if player_no is None:
                        pass
                    else:
                        run = False
                        main()
                        break
                except Exception as e:
                    print(traceback.format_exc(e))
                    print("Server offline")
                    offline = True
                    player_no = None


if __name__ == '__main__':
    menu_screen()
