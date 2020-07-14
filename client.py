from pickle import TRUE
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
        self.player_no = int(n.getP())
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
        self.fonpai_img = [self.bg_tou, self.bg_nan, self.bg_sya, self.bg_pei]
        self.ura = pg.image.load(URA).convert_alpha()
        self.tumo_button_img = pg.image.load(TUMO).convert_alpha()
        self.skip_button_img = pg.image.load(SKIP).convert_alpha()
        self.tumo_1_img = pg.image.load(TUMO_1).convert_alpha()
        self.bg_img_opa60 = pg.image.load(BG_IMG_OPA60).convert_alpha()
        self.senpai_img = pg.image.load(SENPAI).convert_alpha()

        self.ura_mini = pg.transform.scale(self.ura, (65, 103)).convert_alpha()

        self.drawing([*self.get_bg_img_list(), *self.get_tepai_others_list()])

    def run(self):
        self.drawing(self.get_wind_list(0))
        current_ba_count = -1
        current_turn = -1

        while self.running:
            self.clock.tick(10)
            try:
                self.game = self.n.send("get")
                print("send get")
            except:
                self.running = False
                print("Couldn't get game")
                break

            self.player = self.game.player_list[self.player_no]
            turn_pos = self.game.current_turn + self.game.ba_count

            # ツモ・ロンされた時結果を表示して次の場に移行する
            if self.game.ba_end:
                self.drawing(self.get_result_screen_list())
                pg.time.delay(3000)
                self.n.send("new_ba")
                print("send new_ba")
                current_turn = -1
                pg.time.delay(1000)
                self.drawing([*self.get_bg_img_list(), *
                              self.get_tepai_others_list()])
                pg.time.delay(500)  # 早すぎると描画が正常に行われない為、ディレイ
                continue

            # 場が変わったら場を描画
            if current_ba_count != self.game.ba_count:
                current_ba_count = self.game.ba_count
                print(self.game.dora)
                self.drawing(
                    [*self.get_wind_list(current_ba_count), *self.get_dora_list()])

            # ターン毎に捨て牌と他家ツモ表示
            if current_turn != self.game.current_turn:
                current_turn = self.game.current_turn
                self.drawing([*self.get_tumo_others_list(turn_pos),
                              *self.get_sutepai_list(turn_pos),
                              *self.get_info_text_list(turn_pos, current_ba_count)])

            # このユーザーのターン
            if self.player_no == turn_pos % 4:
                if self.player.action == 0:
                    self.n.send("tumo")
                    print("send tumo")
                    self.drawing(self.get_tepai_list())
                    pg.time.delay(1000)  # test
                if self.player.action == 1:
                    self.drawing(self.get_tepai_list())
                    print("draw tepai")
                    self.n.send("hantei")
                    print("send hantei")
                    self.player.able_to_win = True
                if self.player.able_to_win:
                    # tumo / skip button
                    self.drawing(self.get_tumo_button_list())
                    if self.wait_for_mouse_click_agari():  # tumo
                        print("ツモ！")
                        self.drawing(self.get_tumo_effect_list())
                        pg.time.delay(1500)  # 余韻
                        print(self.player.score)
                        self.n.send("agari_tumo")
                        # TODO: リザルト画面

                        break
                    else:  # skip
                        self.drawing(self.remove_tumo_and_skip_button_list())
                        self.n.send("reject")
                        print("続行")
                if self.player.action == 2:
                    num = self.player.dahai()
                    self.n.send(f'dahai_{num}')
                    print(f"send dahai_{num}")
                if self.player.action == 3:
                    self.drawing([*self.get_tepai_list(),
                                  *self.get_sutepai_list(turn_pos)])
                    self.n.send("next")
                    print("send next")

                # 流局
                if len(self.game.tiles) <= 0:
                    self.n.send("new_ba")
                    print("send new_ba")
            else:
                # ターンが変わる毎に手牌表示
                if current_turn != self.game.current_turn:
                    self.drawing(self.get_tepai_list())
                # 別のユーザーのターンの時
                print("waiting...")

            self.events()

# メモ: Rect(切り抜く画像の始点x, 切り抜く画像の始点y, 切り抜く大きさx, 切り抜く大きさy)

    def drawing(self, args_rect_list):
        rect_list = args_rect_list
        pg.display.update(rect_list)

    def get_tepai_others_list(self):
        rect_list = []

        # 下家手牌
        for i in range(5):
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (869, 400 + (i * 65))))

        # 対面手牌
        for i in range(5):
            rect_list.append((self.screen.blit(pg.transform.rotate(
                self.ura_mini, 0), (450 + (i * 65), 40))))

        # 上家手牌
        for i in range(5):
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (20, 300 + (i * 65))))

        return rect_list

    # return: 現場、各ポイント、余り牌のRect_list
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

        return rect_list

    # return: 背景と山のRect_list
    def get_bg_img_list(self):
        rect_list = list()
        rect_list.append(self.screen.blit(self.bg_img, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_yama, (380, 380)))

        return rect_list

    # return: 場風のRect_list
    def get_wind_list(self, ba_count):
        rect_list = []
        # 自分
        rect_list.append(self.screen.blit(
            self.fonpai_img[(4 + (self.player_no - ba_count)) % 4], (391, 597)))
        # 下家
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + ((self.player_no - ba_count) + 1)) % 4], 90),  (594, 598)))
        # 対面
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + ((self.player_no - ba_count) + 2)) % 4], 180), (594, 396)))
        # 上家
        rect_list.append(self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + ((self.player_no - ba_count) + 3)) % 4], 270), (392, 396)))
        return rect_list

    # return: 自分の手牌のRect_list
    def get_tepai_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.bg_img, (0, 850),
                                          (0, 850, WIDTH, HEIGHT - 850)))
        # player手牌
        for k, hand in enumerate(self.game.player_list[self.player_no].hands, 3):
            if k == 8:
                k = 9  # ツモは距離を離す
            rect_list.append(self.screen.blit(pg.image.load(
                os.path.join('Images', hand.pic)).convert_alpha(), (k * TILE_WIDTH, 850)))

        return rect_list

    # return: turnに応じたプレイヤーの捨て牌Rect_list
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

    # return: 他家がツモしている描写Rect_list
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

    # return: 現場のドラRect_list
    def get_dora_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.bg_dora, (10, 10)))
        rect_list.append(self.screen.blit(pg.transform.scale(pg.image.load(
            os.path.join('Images', self.game.dora.pic)), (44, 72)).convert_alpha(), (110, 20)))
        return rect_list

    # return: ツモ・スキップボタンのRect_list
    def get_tumo_button_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.tumo_button_img, (480, 750)))
        rect_list.append(self.screen.blit(self.skip_button_img, (700, 750)))
        return rect_list

    # return: ツモ・スキップボタンの表示を非表示化するRect_list
    def remove_tumo_and_skip_button_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(
            self.bg_img, (480, 750), (480, 750, WIDTH - 480, 85)))
        return rect_list

    # return: ツモした時のエフェクトRect_list

    def get_tumo_effect_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.tumo_1_img, (350, 600)))
        return rect_list

    # return: リザルト画面のRect_list
    def get_result_screen_list(self):
        # TODO: フェードイン効果を追加する
        rect_list = []
        font = pg.font.Font(FONT_NAME, 48)
        font_mini = pg.font.Font(FONT_NAME, 32)
        title = None
        score = self.game.winner_player.score
        if score >= 10:
            title = "役満！"
        else:
            title = "和了！"
        text_title = font.render(f'ツモ！{title}謝謝！', True, YELLOW)
        text_score = font_mini.render(f'加点：{score}', True, YELLOW)
        # TODO: 役内訳を表示する

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_result, (0, 200)))
        rect_list.append(self.screen.blit(self.senpai_img, (100, 200)))
        rect_list.append(self.screen.blit(text_title, (600, 350)))
        rect_list.append(self.screen.blit(text_score, (800, 420)))

        return rect_list

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()

    # ロン・ツモ用のマウスクリックヘルパー関数
    def wait_for_mouse_click_agari(self):
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
