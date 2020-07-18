import traceback

import pygame as pg
from pygame.locals import *

from client import *
from network import Network
from player import *
from settings import *
from tile import *

# TODO: フリテン処理
# TODO: 役名を結果に表示する
# TODO: 上がり時の手牌表示
# TODO: オーラスの表示
# TODO: サーバー接続切れの時の処理調整
# TODO: 同時ロンが出来ないので考慮する
# TODO: 役判定が正しく行われてない可能性がある(コーツ・チャンタあたり)
# TODO: ルール説明のPDF

# FUTURE: 再戦処理
# FUTURE: 音楽の追加・随時

pg.init()
pg.font.init()
pg.mixer.init()
win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)

bg_img = pg.image.load(BG_SUZUME).convert_alpha()
bg_img_opa60 = pg.image.load(BG_IMG_OPA60).convert_alpha()
senpai_img = pg.image.load(SENPAI).convert_alpha()
kouhai_img = pg.image.load(KOUHAI).convert_alpha()
logo_img = pg.image.load(LOGO).convert_alpha()
battle_img = pg.image.load(BATTLE).convert_alpha()
suzume_img = pg.image.load(SUZUME).convert_alpha()


def main():
    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(60)
        game = n.send("get")
        if game.connected():
            start_screen_on_se()
            pg.time.delay(3000)
            Client(n, win)
            run = False
        else:
            waiting_screen()
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False


def start_screen_on_se():
    win.blit(bg_img_opa60, (0, 0))
    win.blit(battle_img, (400, 400))
    pg.display.update()

    pg.mixer.music.unload()
    se = pg.mixer.Sound(SE_START)
    se.play()


def waiting_screen():
    font = pg.font.Font(FONT_NAME, 42)
    text = font.render("対戦相手が揃うまでお待ちください...", True, WHITE)
    background()
    win.blit(bg_img_opa60, (0, 0))
    win.blit(text, (int(WIDTH/2 - text.get_width() /
                        2), int(HEIGHT/2 - text.get_height()/2)))


def background():
    font = pg.font.Font(FONT_NAME, 60)
    text = font.render("クリックで", True, WHITE)
    text_1 = font.render("スタート！", True, WHITE)
    win.blit(bg_img, (0, 0))
    win.blit(bg_img_opa60, (0, 0))
    win.blit(suzume_img, (650, 100))
    win.blit(logo_img, (100, 100))
    win.blit(kouhai_img, (-100, 450))
    win.blit(senpai_img, (600, 450))
    win.blit(text, (330, 600))
    win.blit(text_1, (360, 680))


def menu_screen():
    global n
    global player_no
    run = True
    clock = pg.time.Clock()
    offline = False

    pg.mixer.music.load(BGM_TITLE)
    pg.mixer.music.set_volume(0.5)
    pg.mixer.music.play(-1)

    while run:
        clock.tick(60)
        # メニュー画面描写
        background()
        small_font = pg.font.Font(FONT_NAME, 42)

        if offline:
            off = small_font.render(
                "サーバに接続が出来ません。", 1, WHITE)
            off_2 = small_font.render(
                "接続後、もう一度クリックしてください", True, WHITE)
            win.blit(bg_img_opa60, (0, 0))
            win.blit(off, (int(WIDTH / 2 - off.get_width() / 2), 300))
            win.blit(off_2, (int(WIDTH / 2 - off.get_width() / 2) - 50, 350))

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
                        raise "offline"
                    else:
                        run = False
                        main()
                except:
                    # debug用。完成時は取り除く
                    # print(traceback.format_exc(e))
                    print("Server offline")
                    offline = True
                    player_no = None


if __name__ == '__main__':
    menu_screen()
