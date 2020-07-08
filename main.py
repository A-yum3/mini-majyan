import pygame as pg
import random
from pygame.locals import *
from settings import *
from player import *
from tile import *

# TODO: マルチプレイヤー化

class Game:
    def __init__(self):
        self.running = True
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = False
        self.player_list = [You(1), You(2), You(3), You(4)]
        # self.font_name = pg.font.match_font(FONT_NAME)
        self.dora = None
        self.tiles = None
        # self.all_pop_pai = None
        self.load_data()

    ####################
    ##  データロード  ##
    ####################

    def load_data(self):
        self.bg_img = pg.transform.scale(pg.image.load(BG_IMG), (WIDTH, HEIGHT)).convert()
        self.bg_yama = pg.image.load(BG_YAMA)
        self.bg_dora = pg.image.load(BG_DORA)
        self.bg_tou = pg.transform.scale(pg.image.load(BG_TOU), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_nan = pg.transform.scale(pg.image.load(BG_NAN), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_sya = pg.transform.scale(pg.image.load(BG_SYA), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_pei = pg.transform.scale(pg.image.load(BG_PEI), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_result = pg.image.load(BG_RESULT)
        self.my_ron = pg.image.load(MY_RON)
        self.my_tumo = pg.image.load(MY_TUMO)
        self.fonpai_img = [self.bg_tou, self.bg_nan, self.bg_sya, self.bg_pei]
        self.ura = pg.image.load(URA)

        self.draw_bg_img()
        pg.display.flip()

    # ニューゲーム
    def new(self):
        self.run()

    # プレイ中動作
    def run(self):
        self.playing = True
        self.load_data()
        while self.playing:
            for t_n_s_p in range(4): # 東南西北
                self.new_ba()
                for i in range(4):
                    self.player_list[i].pop_hands = []
                turn = 0

                while len(self.tiles) > 0: # １ゲーム
                    player = self.player_list[turn % 4]
                    # TODO: 全般的に関数化する
                    # TODO: ４人用にself.player部を変更する
                    tumo = self.tiles.pop()
                    print(len(self.tiles)) #TODO: 残り牌描画

                    # 理牌
                    player.hands.sort(key=lambda hai: f'{hai.kind}{hai.value}')
                    player.hands.append(tumo)
                    self.draw(turn)

                    agareru, score = judge(player.hands, self.dora)

                    if agareru and score >= 5 :
                    # if True:  #deb
                        self.screen.blit(pg.image.load(TUMO), (480, 750))
                        self.screen.blit(pg.image.load(SKIP), (700, 750))
                        pg.display.update()
                        if self.wait_for_mouse_click():
                            print("ツモ！")
                            print(score)
                            # TODO: リザルト画面、点数交換
                            break
                        else:
                            self.draw(turn)
                            print("続行")

                    player.dahai()
                    self.draw(turn)
                    # TODO: 他家がロン出来るかチェック

                    turn += 1
                    self.clock.tick(FPS)
                    self.events()
                print('end!')
                self.player_list.append(self.player_list.pop(0))


    ####################
    ##      更新      ##
    ####################

    def new_ba(self):
        # 捨て牌をリセット
        self.all_pop_pai = []

        # 牌をシャッフル
        self.tiles = Tile.create_yamahai()
        self.dora = self.tiles.pop()

        # 牌を配る
        for i in range(4):
            hands = [self.tiles.pop() for _ in range(5)]
            self.player_list[i].set_hands(hands)
            # print(self.player_list[i].hands)

        # 自風決定
        wind_img_list = [self.bg_tou, self.bg_nan, self.bg_sya, self.bg_pei]
        for i in range(4):
            self.player_list[i].set_wind_img(wind_img_list[i])

    # 更新処理
    def update(self):
        #TODO: 後でrun()にあるやつを切り出す
        pass

    ####################
    ##      描画      ##
    ####################

    def draw(self, turn):
        self.draw_bg_img()

        self.screen.blit(self.bg_dora, (10, 10))
        self.screen.blit(pg.transform.scale(pg.image.fromstring(self.dora.img_string, self.dora.img_size, "RGB"), (44, 72)), (110, 20))

        # TODO: 表示域を指定して更新部分のみ描写
        # TODO: 他人のターン時他人のツモ裏表示（CPU戦のみ）

        self.draw_wind(turn)
        self.draw_tepai(turn)
        self.draw_sutepai(turn)
        pg.display.update()

    def draw_bg_img(self):
        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.bg_yama, (380,380))

    def draw_wind(self, turn):
        self.screen.blit(self.player_list[turn % 4].wind_img, (391, 597))
        self.screen.blit(pg.transform.rotate(self.player_list[(turn + 1) % 4].wind_img, 90),  (594, 598))
        self.screen.blit(pg.transform.rotate(self.player_list[(turn + 2) % 4].wind_img, 180), (594, 396))
        self.screen.blit(pg.transform.rotate(self.player_list[(turn + 3) % 4].wind_img, 270), (392, 396))

    def draw_tepai(self, turn):
        ura_mini = pg.transform.scale(self.ura, (65, 103))
        # for文で纏められそうだが、今のままで分かりやすいのでこれでもヨシ
        # player手牌
        for k, hand in enumerate(self.player_list[turn % 4].hands, 3):
            if k == 8: k = 9 # ツモは距離を離す
            self.screen.blit(pg.image.fromstring(hand.img_string, hand.img_size, "RGB").convert(), (k * TILE_WIDTH, 850))

        # 上家手牌
        for i in range(5):
            self.screen.blit(pg.transform.rotate(ura_mini, 90), (20, 300 + (i * 65)))

        # 対面手牌
        for i in range(5):
            self.screen.blit(pg.transform.rotate(ura_mini, 0), (450 + (i * 65), 40))

        # 下家手牌
        for i in range(5):
            self.screen.blit(pg.transform.rotate(ura_mini, 90), (869, 400 + (i * 65)))

    def draw_sutepai(self, turn):
        # for文で纏められそうだが、今のままで分かりやすいのでこれでもヨシ
        # player捨て牌
        for k, hand in enumerate(self.player_list[turn % 4].pop_hands, 0):
            x = 370 + ((k % 5) * 53)
            y = 650 + (87 * int(k / 5))
            temp_img = pg.transform.scale(pg.image.fromstring(hand.img_string, hand.img_size, "RGB").convert(), TILE_MINI_SIZE)
            self.screen.blit(temp_img, (x, y))

        # 上家捨て牌
        for k, hand in enumerate(self.player_list[(turn + 3) % 4].pop_hands, 0):
            x = 280 - (87 * int(k / 5))
            y = 380 + ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.fromstring(hand.img_string, hand.img_size, "RGB").convert(), TILE_MINI_SIZE), 270)
            self.screen.blit(temp_img, (x, y))

        # 対面捨て牌
        for k, hand in enumerate(self.player_list[(turn + 2) % 4].pop_hands, 0):
            x = 600 - ((k % 5) * 53)
            y = 300 - (87 * int(k / 5))
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.fromstring(hand.img_string, hand.img_size, "RGB").convert(), TILE_MINI_SIZE), 180)
            self.screen.blit(temp_img, (x, y))

        # 下家捨て牌
        for k, hand in enumerate(self.player_list[(turn + 1) % 4].pop_hands, 0):
            x = 650 + (87 * int(k / 5))
            y = 600 - ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.fromstring(hand.img_string, hand.img_size, "RGB").convert(), TILE_MINI_SIZE), 90)
            self.screen.blit(temp_img, (x, y))

    ####################
    ##    特別処理    ##
    ####################

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def game_start_screen(self):
        #ゲームスタート画面
        pass

    # TODO: resultの表示
    def game_over_screen(self):
        # ゲームオーバー画面
        g.running = False

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

    def wait_for_mouse_click(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    return False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if x >= 490 and x <= 675 and y >= 760 and y <= 830:
                        waiting = False
                        return True
                    elif x >= 710 and x <= 900 and y >= 760 and y <= 820:
                        waiting = False
                        return False


g = Game()
g.game_start_screen()
while g.running:
    g.new()
    g.game_over_screen()

pg.quit()
