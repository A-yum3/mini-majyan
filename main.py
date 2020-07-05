import pygame as pg
import random
from pygame.locals import *
from settings import *
from player import *
from tile import *

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
        # self.player_list = [You(), Cpu(), Cpu(), Cpu()]
        self.player = You()
        self.font_name = pg.font.match_font(FONT_NAME)
        self.dora = None
        self.tiles = None
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
            # for _ in range(4): # 東西南北
            self.load_data()
            self.new_ba()
            self.player.pop_hands = []
            turn = 0
            while len(self.tiles) != 0: # １ゲーム
                tumo = self.tiles.pop()
                print(len(self.tiles))
                # self.player_list[turn % 4].action(tumo)
                # 理牌
                self.player.hands.sort(key=lambda hai: f'{hai.kind}{hai.value}')
                self.player.hands.append(tumo)
                self.draw()

                agareru, score = judge(self.player.hands, self.dora)

                if agareru and score >= 5 :
                # if True:  #deb
                    self.screen.blit(pg.image.load(TUMO), (480, 750))
                    self.screen.blit(pg.image.load(SKIP), (700, 750))
                    pg.display.update()
                    if self.wait_for_mouse_click():
                        print("ツモ！")
                        print(score)
                        # TODO: 得点計算
                        break
                    else:
                        self.draw()
                        print("続行")

                self.player.dahai()
                self.draw()
                # TODO: 他家がロン出来るかチェック

                turn += 1
                self.clock.tick(FPS)
                self.events()
                self.update()
            print('end!')

    def new_ba(self):
        # 牌をシャッフル
        self.tiles = Tile.create_yamahai()
        self.dora = self.tiles.pop()

        # 牌を配る
        # for i in range(4):
        hands = [self.tiles.pop() for _ in range(5)]
        self.player.set_hands(hands)
            # self.player_list[i].set_hands(hands)

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
        self.screen.blit(pg.image.load(BG_IMG), (0, 0))
        self.screen.blit(pg.image.load(BG_YAMA), (380,380))

        self.screen.blit(pg.transform.scale(pg.image.fromstring(self.dora.img_string, self.dora.img_size, "RGB"), (53, 87)), (20, 20))

        for x, hand in enumerate(self.player.hands, 3):
            if x == 8: x = 9
            self.screen.blit(pg.image.fromstring(hand.img_string, hand.img_size, "RGB"), (x * TILE_WIDTH, 850))

        for x, hand in enumerate(self.player.pop_hands, 0):
            self.screen.blit(pg.transform.scale(pg.image.fromstring(hand.img_string, hand.img_size, "RGB"), (53, 87)), (((x % 5)+7) * 53, 650 + (87 * int(x / 5))))

        pg.display.update()

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
