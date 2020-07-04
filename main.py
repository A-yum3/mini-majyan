import pygame as pg
import random
from pygame.locals import *
from settings import *
from player import *
from pai import *

class Game:
    def __init__(self):
        self.running = True
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        # self.all_sprites = None
        self.playing = False
        self.player_list = [You(), Cpu(), Cpu(), Cpu()]
        self.font_name = pg.font.match_font(FONT_NAME)
        self.basic_pais = [
            Pai('1s', S_1), Pai('2s', S_2), Pai('3s', S_3), Pai('4s', S_4), Pai('5s', S_5), Pai('6s', S_6), Pai('7s', S_7), Pai('8s', S_8), Pai('9s', S_9),
            Pai('1s', S_1), Pai('2s', S_2), Pai('3s', S_3), Pai('4s', S_4), Pai('5s', S_5), Pai('6s', S_6), Pai('7s', S_7), Pai('8s', S_8), Pai('9s', S_9),
            Pai('1s', S_1), Pai('2s', S_2), Pai('3s', S_3), Pai('4s', S_4), Pai('5s', S_5), Pai('6s', S_6), Pai('7s', S_7), Pai('8s', S_8), Pai('9s', S_9),
            Pai('1r', R_1), Pai('2r', R_2), Pai('3r', R_3), Pai('4r', R_4), Pai('5r', R_5), Pai('6r', R_6), Pai('7r', R_7), Pai('8r', R_8), Pai('9r', R_9),
            Pai('hatu', HATU), Pai('hatu', HATU), Pai('hatu', HATU), Pai('hatu', HATU),
            Pai('tyun', TYUN), Pai('tyun', TYUN), Pai('tyun', TYUN), Pai('tyun', TYUN),
        ]
        self.dora = None
        self.load_data()

    # 初期ロード
    def load_data(self):
        self.screen.blit(pg.image.load(BG_IMG), (0, 0))
        self.screen.blit(pg.image.load(BG_YAMA), (380,380))
        pg.display.flip()

    # ゲームオーバー後のニューゲーム
    def new(self):
        # self.all_sprites = pg.sprite.Group()
        # self.all_sprites.add()
        self.run()

    # プレイ中動作
    def run(self):
        self.playing = True
        while self.playing:
            for _ in range(4): # 東西南北
                self.new_ba()
                turn = 0
                while len(self.pais) != 0: # １ゲーム
                    tumo = self.pais.pop()
                    self.player_list[turn % 4].action(tumo)

                    turn += 1
                    self.clock.tick(FPS)
                    self.events()
                    self.update()
                    self.draw()

    def new_ba(self):
        # 牌をシャッフル
        self.pais = random.sample(self.basic_pais, len(self.basic_pais))
        self.dora = self.pais.pop()

        # 牌を配る
        for i in range(4):
            hands = [self.pais.pop() for _ in range(5)]
            self.player_list[i].set_hands(hands)

    # 更新処理
    def update(self):
        #アップデート
        pass
        # self.all_sprites.update()

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        pass

    def game_start_screen(self):
        #ゲームスタート画面
        pass

    # TODO: resultの表示
    def game_over_screen(self):
        # ゲームオーバー画面
        pass

    def wait_for_mouse(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.MOUSEBUTTONUP:
                    waiting = False


g = Game()
g.game_start_screen()
while g.running:
    g.new()
    g.game_over_screen()

pg.quit()
