import pygame as pg
from pygame import display, draw
from pygame.locals import *

from player import *
from settings import *
from tile import *


class Client:
    def __init__(self, n, win):
        self.running = True
        self.clock = pg.time.Clock()
        self.game = None
        self.screen = win
        self.font = pg.font.Font(FONT_NAME, 24)
        self.n = n
        self.player_no = n.p
        print("You are player", self.player_no)
        self.load_data()
        self.run()

    def load_data(self):
        self.bg_img = pg.transform.scale(
            pg.image.load(BG_IMG), (WIDTH, HEIGHT)).convert()
        self.bg_yama = pg.image.load(BG_YAMA).convert_alpha()
        self.bg_dora = pg.image.load(BG_DORA).convert_alpha()
        self.bg_tou = pg.transform.scale(pg.image.load(
            BG_TOU), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT)).convert_alpha()
        self.bg_nan = pg.transform.scale(pg.image.load(
            BG_NAN), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT)).convert_alpha()
        self.bg_sya = pg.transform.scale(pg.image.load(
            BG_SYA), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT)).convert_alpha()
        self.bg_pei = pg.transform.scale(pg.image.load(
            BG_PEI), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT)).convert_alpha()
        self.bg_result = pg.image.load(BG_RESULT).convert_alpha()
        self.my_ron = pg.image.load(MY_RON).convert_alpha()
        self.my_tumo = pg.image.load(MY_TUMO).convert_alpha()
        self.fonpai_img = [self.bg_tou, self.bg_pei, self.bg_sya, self.bg_nan]
        self.ura = pg.image.load(URA).convert_alpha()
        self.tepai_rect = []

        self.ura_mini = pg.transform.scale(self.ura, (65, 103)).convert_alpha()
        temp_list = self.get_bg_img_list()

        # 下家手牌
        for i in range(5):
            self.tepai_rect.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (869, 400 + (i * 65))))

        # 対面手牌
        for i in range(5):
            self.tepai_rect.append((self.screen.blit(pg.transform.rotate(
                self.ura_mini, 0), (450 + (i * 65), 40))))

        # 上家手牌
        for i in range(5):
            self.tepai_rect.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (20, 300 + (i * 65))))

        self.drawing([*temp_list, *self.tepai_rect])

    def run(self):
        self.drawing(self.get_wind_list(0))
        current_ba_count = 0
        current_turn = 0

        while self.running:
            self.clock.tick(10)
            try:
                self.game = self.n.send("fuck")
            except:
                self.running = False
                print("Couldn't get game")
                break

            self.player = self.game.player_list[self.player_no]
            turn_no = self.game.current_turn + self.game.ba_count

            # 場が変わったら場を描画
            if current_ba_count != self.game.ba_count:
                current_ba_count = self.game.ba_count
                self.drawing(
                    [*self.get_wind_list(current_ba_count), *self.get_dora_list()])

            if current_turn != turn_no:
                current_turn = turn_no
                self.drawing([*self.get_tumo_others_list(current_turn),
                              *self.get_sutepai_list(current_turn)])

            # このユーザーのターン
            if self.player_no == turn_no % 4:
                if self.player.action == 0:
                    self.n.send("tumo")
                    print("send tumo")
                    self.drawing(self.get_tepai_list())
                    pg.time.delay(2000)
                if self.player.action == 1:
                    self.drawing(self.get_tepai_list())
                    print("draw tepai")
                    self.n.send("hantei")
                    print("send hantei")
                if self.player.able_to_win:
                    # 上がり選択肢
                    # temp_rect = []
                    # temp_rect.append(self.screen.blit(
                    #     pg.image.load(TUMO), (480, 750)))
                    # temp_rect.append(self.screen.blit(
                    #     pg.image.load(SKIP), (700, 750)))
                    # pg.display.update(temp_rect)

                    # if self.wait_for_mouse_click():
                    #     print("ツモ！")
                    #     print(score)
                    #     # TODO: リザルト画面、点数交換処理
                    #     break
                    # else:
                    #     self.drawing(turn)
                    #     print("続行")
                    pass
                if self.player.action == 2:
                    num = self.player.dahai()
                    self.n.send(f'dahai_{num}')
                    print(f"send dahai_{num}")
                if self.player.action == 3:
                    self.drawing([*self.get_tepai_list(),
                                  *self.get_sutepai_list(turn_no)])
                    self.n.send("next")
                    print("send next")

                # 流局
                if len(self.game.tiles) <= 0:
                    self.n.send("new_ba")
                    print("send new_ba")
            else:
                # 別のユーザーのターンの時
                print("waiting...")

            self.events()

    ####################
    ##      描画      ##
    ####################

    def drawing(self, args_rect_list):
        rect_list = args_rect_list
        pg.display.update(rect_list)

    def get_info_text_list(self, turn, ba_count):
        rect_list = []
        wind_list = ['東', '南', '西', '北']
        xy_list = [(500, 570), (570, 510), (500, 440), (440, 510)]

        rect_list.append(self.screen.blit(
            self.bg_yama, (470, 470), (90, 90, 95, 100)))
        nokori_pai_count_text = self.font.render(
            f'余 {len(self.game.tiles) - 1}', True, CYAN)
        wind_text = self.font.render(f'{wind_list[ba_count]}', True, CYAN)
        for i in range(4):
            point_text = self.font.render(
                f'{self.game.player_list[(turn + i) % 4].point}', True, YELLOW)
            rect_list.append(self.screen.blit(
                pg.transform.rotate(point_text, 90 * i), xy_list[i]))
        rect_list.append(self.screen.blit(wind_text, (503, 485)))
        rect_list.append(self.screen.blit(nokori_pai_count_text, (485, 530)))

        rect_list.extend(self.tepai_rect)

        return rect_list

    def get_bg_img_list(self):
        rect_list = list()
        rect_list.append(self.screen.blit(self.bg_img, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_yama, (380, 380)))

        return rect_list

    # 場が変わった時のみ再描画
    def get_wind_list(self, ba_count):
        rect_list = []
        # 自分
        rect_list.append(self.screen.blit(
            self.fonpai_img[(4 + (ba_count - self.player_no)) % 4], (391, 597)))
        # 下家
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (ba_count - (self.player_no) + 1)) % 4], 90),  (594, 598)))
        # 対面
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (ba_count - (self.player_no) + 2)) % 4], 180), (594, 396)))
        # 上家
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (ba_count - (self.player_no) + 3)) % 4], 270), (392, 396)))
        return rect_list

    def get_tepai_list(self):
        rect_list = []
        # メモ: Rect(切り抜く画像の始点x, 切り抜く画像の始点y, 切り抜く大きさx, 切り抜く大きさy)
        rect_list.append(self.screen.blit(self.bg_img, (0, 850),
                                          (0, 850, WIDTH, HEIGHT - 850)))
        # player手牌
        for k, hand in enumerate(self.game.player_list[self.player_no].hands, 3):
            if k == 8:
                k = 9  # ツモは距離を離す
            rect_list.append(self.screen.blit(pg.image.load(
                os.path.join('Images', hand.pic)).convert_alpha(), (k * TILE_WIDTH, 850)))

        return rect_list

    def get_sutepai_list(self, turn):
        rect_list = []

        # player捨て牌
        if turn % 4 == self.player_no:
            for k, hand in enumerate(self.game.player_list[self.player_no].pop_hands, 0):
                x = 370 + ((k % 5) * 53)
                y = 650 + (87 * int(k / 5))
                temp_img = pg.transform.scale(pg.image.load(
                    os.path.join('Images', hand.pic)), TILE_MINI_SIZE).convert_alpha()
                rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 下家捨て牌
        if turn % 4 == self.player_no + 1:
            for k, hand in enumerate(self.game.player_list[(self.player_no + 3) % 4].pop_hands, 0):
                x = 650 + (87 * int(k / 5))
                y = 600 - ((k % 5) * 53)
                temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                    os.path.join('Images', hand.pic), TILE_MINI_SIZE), 90)).convert_alpha()
                rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 対面捨て牌
        if turn % 4 == self.player_no + 2:
            for k, hand in enumerate(self.game.player_list[(self.player_no + 2) % 4].pop_hands, 0):
                x = 600 - ((k % 5) * 53)
                y = 300 - (87 * int(k / 5))
                temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                    os.path.join('Images', hand.pic), TILE_MINI_SIZE), 180)).convert_alpha()
                rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 上家捨て牌
        if turn % 4 == self.player_no + 3:
            for k, hand in enumerate(self.game.player_list[(self.player_no - 1) % 4].pop_hands, 0):
                x = 280 - (87 * int(k / 5))
                y = 380 + ((k % 5) * 53)
                temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                    os.path.join('Images', hand.pic), TILE_MINI_SIZE), 270)).convert_alpha()
                rect_list.append(self.screen.blit(temp_img, (x, y)))

        return rect_list

    def get_tumo_others_list(self, current_turn):
        rect_list = []

        # 下家
        if current_turn % 4 == self.player_no + 1:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (869, 270)))

        # 対面
        if current_turn % 4 == self.player_no + 2:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 0), (325, 40)))

        # 上家
        if current_turn % 4 == self.player_no + 3:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (20, 755)))

        return rect_list

        ####################
        ##    特別処理    ##
        ####################

    def get_dora_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.bg_dora, (10, 10)))
        rect_list.append(self.screen.blit(pg.transform.scale(pg.image.load(
            os.path.join('Images', self.game.dora.pic)), (44, 72)).convert_alpha(), (110, 20)))
        return rect_list

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()

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
