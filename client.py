from pickle import *
import pygame as pg
from pygame import display, draw
from pygame.locals import *

from player import *
from settings import *
from tile import *

# TODO: 音楽の追加


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
        self.fonpai_img = [self.bg_tou, self.bg_nan, self.bg_sya, self.bg_pei]
        self.ura = pg.image.load(URA).convert_alpha()
        self.tumo_button_img = pg.image.load(TUMO).convert_alpha()
        self.skip_button_img = pg.image.load(SKIP).convert_alpha()
        self.ron_button_img = pg.image.load(RON).convert_alpha()
        self.tumo_efe_img = pg.image.load(TUMO_1).convert_alpha()
        self.ron_efe_img = pg.image.load(RON_1).convert_alpha()
        self.bg_img_opa60 = pg.image.load(BG_IMG_OPA60).convert_alpha()
        self.senpai_img = pg.image.load(SENPAI).convert_alpha()

        self.ura_mini = pg.transform.scale(self.ura, (65, 103)).convert_alpha()

        self.drawing([*self.get_bg_img_list(), *self.get_tepai_others_list()])

    def run(self):
        self.drawing(self.get_wind_list(0))
        current_ba_count = -1
        current_turn = -1
        current_tiles_len = 0

        while self.running:
            self.clock.tick(30)
            try:
                self.game = self.n.send("get")
                print("send get")
            except:
                self.running = False
                print("Couldn't get game")
                break

            self.player = self.game.player_list[self.player_no]
            player_other1 = self.game.player_list[(self.player_no + 1) % 4]
            player_other2 = self.game.player_list[(self.player_no + 2) % 4]
            player_other3 = self.game.player_list[(self.player_no + 3) % 4]
            turn_pos = self.game.current_turn + self.game.ba_count

            if self.player.ready and player_other1.ready and player_other2.ready and player_other3.ready:
                # 同期後、勝利プレイヤーがリセットを送る
                if self.game.winner_player.name == self.player_no:
                    self.n.send("new_ba")
                continue

            if self.player.ready or player_other1.ready or player_other2.ready or player_other3.ready:
                continue

            if current_turn == -1:
                self.drawing([*self.get_bg_img_list(), *
                              self.get_tepai_others_list()])

            # ツモ・ロンされた時結果を表示して次の場に移行する
            if self.game.ba_end:
                if self.game.is_ron:
                    self.drawing(self.get_ron_effect_list())  # TODO: 表示調整
                elif self.game.is_tumo:
                    self.drawing(self.get_tumo_effect_list())  # TODO: 表示調整
                pg.time.delay(1500)  # 余韻
                self.drawing(self.get_result_screen_list())
                pg.time.delay(3000)
                current_turn = -1
                self.n.send("ready")
                continue

            # 場が変わったら場を描画
            if current_ba_count != self.game.ba_count:
                current_ba_count = self.game.ba_count
                print(self.game.dora)
                self.drawing(
                    [*self.get_wind_list(current_ba_count), *self.get_dora_list()])

            # ターン毎に捨て牌と他家ツモ表示
            if current_turn != self.game.current_turn:
                self.drawing(self.remove_tumo_others_list(current_turn))
                current_turn = self.game.current_turn
                self.drawing([*self.get_tumo_others_list(turn_pos),
                              *self.get_sutepai_list(),
                              *self.get_info_text_list(turn_pos, current_ba_count),
                              *self.get_tepai_list(),
                              *self.get_wind_list(current_ba_count)])

            # 残り牌数が違う時描写
            if current_tiles_len != len(self.game.tiles):
                current_tiles_len = len(self.game.tiles)
                self.drawing([*self.remove_nokori_text_list(),
                              *self.get_nokori_text_list()])

                # このユーザーのターン
            if self.player_no == turn_pos % 4:
                if self.player.action == 0:
                    self.n.send("tumo")
                    print("send tumo")
                    self.drawing(self.get_tepai_list())
                    pg.time.delay(1000)  # deb
                if self.player.action == 1:
                    self.drawing(self.get_tepai_list())
                    print("draw tepai")
                    self.n.send("hantei")
                    print("send hantei")
                self.player.able_to_win = True  # deb
                if self.player.able_to_win:
                    # tumo / skip button
                    self.drawing(self.get_tumo_button_list())
                    if self.wait_for_mouse_click_agari():  # tumo
                        print("ツモ！")
                        print(self.player.score)
                        self.n.send("agari_tumo")
                    else:  # skip
                        self.drawing(self.remove_tumo_and_skip_button_list())
                        self.n.send("reject")
                        print("続行")
                if self.player.action == 2:
                    num = self.player.dahai()
                    self.game = self.n.send(f'dahai_{num}')
                    print(f"send dahai_{num}")
                    self.drawing([*self.get_tepai_list(),
                                  *self.get_sutepai_list()])
                print("ron waiting")
                if (self.player.action == 3
                    and player_other1.judge_phase_end
                    and player_other2.judge_phase_end
                        and player_other3.judge_phase_end):
                    self.n.send("next")
                    print("send next")
                    # 流局
                if len(self.game.tiles) <= 0:
                    self.n.send("ryukyoku")

            else:
                # 別のユーザーのターンの時
                print("waiting...")
                # TODO: 他人の捨て牌でロン出来る機能の追加
                if not self.player.judge_phase_end:
                    print("ロン判定")
                    self.game = self.n.send("hantei_ron")
                    if self.game.player_list[self.player_no].able_to_win:
                        self.drawing(self.get_ron_button_list())
                        if self.wait_for_mouse_click_agari():
                            print("ロン！")
                            self.n.send("agari_ron")
                            # TODO:同時ロンが出来ないので考慮する
                        else:
                            self.n.send("reject_win")
                            print("続行")
                            self.drawing(
                                self.remove_tumo_and_skip_button_list())
                    self.n.send("end_of_judge")
            self.events()

# メモ: Rect(切り抜く画像の始点x, 切り抜く画像の始点y, 切り抜く大きさx, 切り抜く大きさy)
# current_turn % 4(turn_pos) は親(東)の位置を表している

    # params: Rect_list
    # return: None, 画面の更新

    def drawing(self, args_rect_list):
        rect_list = args_rect_list
        pg.display.update(rect_list)

    # return: 他家の手牌Rect_list
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

    def get_nokori_text_list(self):
        rect_list = []
        nokori_pai_count_text = self.font.render(
            f'余 {len(self.game.tiles)}', True, CYAN)
        rect_list.append(self.screen.blit(nokori_pai_count_text, (485, 530)))
        return rect_list

    def remove_nokori_text_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(
            self.bg_yama, (480, 520), (100, 140, 80, 30)))

        return rect_list

    # return: 現場、各ポイント、余り牌のRect_list
    def get_info_text_list(self, turn, ba_count):
        rect_list = []
        wind_list = ['東', '南', '西', '北']
        xy_list = [(500, 570), (570, 510), (500, 440), (440, 510)]

        rect_list.append(self.screen.blit(
            self.bg_yama, (380, 380), (0, 0, 270, 273)))

        wind_text = self.font.render(f'{wind_list[ba_count]}', True, CYAN)
        for i in range(4):
            point_text = self.font.render(
                f'{self.game.player_list[(turn + i) % 4].point}', True, YELLOW)
            rect_list.append(self.screen.blit(
                pg.transform.rotate(point_text, 90 * i), xy_list[i]))
        rect_list.append(self.screen.blit(wind_text, (503, 485)))

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

    # return: プレイヤーの捨て牌Rect_list
    def get_sutepai_list(self):
        rect_list = []

        # player捨て牌
        for k, hand in enumerate(self.game.player_list[self.player_no].pop_hands, 0):
            x = 370 + ((k % 5) * 53)
            y = 650 + (87 * int(k / 5))
            temp_img = pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic)), TILE_MINI_SIZE).convert_alpha()
            rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 下家捨て牌
        for k, hand in enumerate(self.game.player_list[(self.player_no - 3) % 4].pop_hands, 0):
            x = 650 + (87 * int(k / 5))
            y = 600 - ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic)), TILE_MINI_SIZE), 90).convert_alpha()
            rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 対面捨て牌
        for k, hand in enumerate(self.game.player_list[(self.player_no - 2) % 4].pop_hands, 0):
            x = 600 - ((k % 5) * 53)
            y = 300 - (87 * int(k / 5))
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic)), TILE_MINI_SIZE), 180).convert_alpha()
            rect_list.append(self.screen.blit(temp_img, (x, y)))

        # 上家捨て牌
        for k, hand in enumerate(self.game.player_list[(self.player_no - 1) % 4].pop_hands, 0):
            x = 280 - (87 * int(k / 5))
            y = 380 + ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic)), TILE_MINI_SIZE), 270).convert_alpha()
            rect_list.append(self.screen.blit(temp_img, (x, y)))

        return rect_list

    # return: 他家がツモしている描写Rect_list
    def get_tumo_others_list(self, current_turn):
        rect_list = []

        # 下家
        if current_turn % 4 == (self.player_no + 1) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (869, 270)))

        # 対面
        if current_turn % 4 == (self.player_no + 2) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 0), (325, 40)))

        # 上家
        if current_turn % 4 == (self.player_no + 3) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 90), (20, 690)))

        return rect_list

    def remove_tumo_others_list(self, current_turn):
        rect_list = []

        # 下家
        if current_turn % 4 == (self.player_no + 1) % 4:
            rect_list.append(self.screen.blit(
                self.bg_img, (869, 270), (869, 270, 103, 65)))

        if current_turn % 4 == (self.player_no + 2) % 4:
            rect_list.append(self.screen.blit(
                self.bg_img, (325, 40), (325, 40, 65, 103)))

        if current_turn % 4 == (self.player_no + 3) % 4:
            rect_list.append(self.screen.blit(
                self.bg_img, (20, 690), (20, 690, 103, 65)))

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

    # return: ロン・スキップボタンのRect_list
    def get_ron_button_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.ron_button_img, (480, 750)))
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
        print(self.game.winner_player)

        if self.game.winner_player.name % 4 == self.player_no:
            rect_list.append(self.screen.blit(self.tumo_efe_img, (350, 600)))

        # TODO: 後で位置調整する
        # 下家
        if self.game.winner_player.name % 4 == self.player_no + 1:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 90), (500, 300)))

        # 対面
        if self.game.winner_player.name % 4 == self.player_no + 2:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 180), (350, 424)))

        # 上家
        if self.game.winner_player.name % 4 == self.player_no + 3:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 270), (100, 300)))

        return rect_list

    def get_ron_effect_list(self):
        rect_list = []
        print(self.game.winner_player)

        if self.game.winner_player.name % 4 == self.player_no:
            rect_list.append(self.screen.blit(self.ron_efe_img, (350, 600)))

        # TODO: 後で位置調整する
        # 下家
        if self.game.winner_player.name % 4 == self.player_no + 1:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 90), (500, 300)))

        # 対面
        if self.game.winner_player.name % 4 == self.player_no + 2:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 180), (350, 424)))

        # 上家
        if self.game.winner_player.name % 4 == self.player_no + 3:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 270), (100, 300)))

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
        text_name = font.render(
            f'Player {self.game.winner_player.name}', True, YELLOW)
        # TODO: 役内訳を表示する
        # TODO: 上がり時の手牌表示

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_result, (0, 200)))
        rect_list.append(self.screen.blit(self.senpai_img, (100, 200)))
        rect_list.append(self.screen.blit(text_name, (600, 350)))
        rect_list.append(self.screen.blit(text_title, (600, 400)))
        rect_list.append(self.screen.blit(text_score, (800, 470)))

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
