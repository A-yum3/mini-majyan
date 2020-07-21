import time
from pickle import *
import pygame as pg
from pygame import display, draw
from pygame.locals import *

from player import *
from settings import *
from tile import *
from network import *


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
        self.kouhai_img = pg.image.load(KOUHAI).convert_alpha()
        self.kouhai_mini_img = pg.transform.scale(
            pg.image.load(KOUHAI), (461, 615)).convert_alpha()
        self.result_bar_img = pg.image.load(RESULT_BAR).convert_alpha()
        self.result_bar_one_img = pg.image.load(RESULT_BAR_ONE).convert_alpha()
        self.ura_mini = pg.transform.scale(self.ura, (65, 103)).convert_alpha()
        self.hude_img = pg.image.load(HUDE).convert_alpha()
        self.han_img = pg.image.load(HAN).convert_alpha()
        self.ten_img = pg.image.load(TEN).convert_alpha()
        self.kakunin_img = pg.image.load(KAKUNIN).convert_alpha()
        self.olas_img = pg.image.load(OLAS).convert_alpha()
        self.yakuman_img = pg.image.load(YAKUMAN).convert_alpha()

        self.se_dahai = pg.mixer.Sound(SE_DAHAI)
        self.se_tumo = pg.mixer.Sound(SE_TUMO)
        self.se_ron = pg.mixer.Sound(SE_RON)
        self.se_yaku = pg.mixer.Sound(SE_YAKU)
        self.se_score = pg.mixer.Sound(SE_SCORE)
        self.se_noten = pg.mixer.Sound(SE_NOTEN)
        self.se_rank1 = pg.mixer.Sound(SE_RANK1)
        self.se_rank2_4 = pg.mixer.Sound(SE_RANK24)

        pg.mixer.music.load(BGM_GAME)
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

    def run(self):
        self.drawing([*self.get_bg_img_list(), *self.get_tepai_others_list()])
        self.drawing(self.get_wind_list(0))
        current_ba_count = -1
        current_turn = -1
        current_tiles_len = 0

        while self.running:
            self.clock.tick(30)
            try:
                self.game = self.n.send("get")
                # print("send get")
            except:
                self.running = False
                print("Couldn't get game")
                break

            # # debug
            # self.last_result_flow()
            # pg.time.delay(5000)
            # raise "stop"

            if (self.game.ba_count == 4):
                print("end game")
                pg.mixer.music.stop()
                self.last_result_flow()
                if self.wait_for_mouse_click_kakunin():
                    self.running = False
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

            # ツモ・ロンされた時結果を表示する。流局時はそのまま次の場に移行する
            if (self.game.ba_end
                and self.player.judge_phase_end
                and player_other1.judge_phase_end
                and player_other2.judge_phase_end
                    and player_other3.judge_phase_end):
                if self.game.ron_count >= 2:
                    self.is_ron = False
                self.result_flow()
                self.n.send("ready")
                continue

            # 場が変わったら場を描画
            if current_ba_count != self.game.ba_count:
                time.sleep(3)
                print("Change ba")
                pg.mixer.music.play(-1)
                current_ba_count = self.game.ba_count
                current_tiles_len = 0
                current_turn = -1
                if current_ba_count == 3:
                    self.drawing(self.get_olas_list())
                    pg.time.delay(2000)
                self.drawing_change_ba_screen(current_ba_count)

            # ターン毎に捨て牌と他家ツモ表示
            if current_turn != self.game.current_turn:
                print("Change Turn")
                self.drawing(self.remove_tumo_others_list(turn_pos - 1))
                current_turn = self.game.current_turn
                self.drawing([*self.get_tumo_others_list(turn_pos),
                              *self.get_sutepai_list(),
                              *self.get_info_text_list(current_ba_count),
                              *self.get_tepai_list(),
                              *self.get_wind_list(current_ba_count),
                              *self.remove_nokori_text_list(),
                              *self.get_nokori_text_list()])

            # 残り牌数が違う時描写
            if current_tiles_len != len(self.game.tiles):
                current_tiles_len = len(self.game.tiles)
                print(current_tiles_len)
                self.drawing([*self.remove_nokori_text_list(),
                              *self.get_nokori_text_list()])

            #  エラー

            # このユーザーのターン
            if self.player_no == turn_pos % 4:

                if self.player.action == 0:
                    self.n.send("tumo")
                    print("send tumo")
                    pg.time.delay(1000)
                    continue
                if self.player.action == 1:
                    self.drawing(self.get_tepai_list())
                    print("draw tepai")
                    self.n.send("hantei")
                    print("send hantei")
                    continue
                # self.player.able_to_win = True  # deb
                if self.player.able_to_win:
                    self.drawing(self.get_tumo_button_list())
                    if self.wait_for_mouse_click_agari():  # tumo
                        print("ツモ！")
                        print(self.player.score)
                        self.n.send("agari_tumo")
                    else:  # skip
                        self.drawing(self.remove_tumo_and_skip_button_list())
                        self.n.send("reject")
                        print("続行")
                    continue
                if self.player.action == 2:
                    num = self.player.dahai()
                    self.n.send(f'dahai_{num}')
                    print(f"send dahai_{num}")
                    self.se_dahai.play()
                    continue
                self.drawing([*self.get_tepai_list(),
                              *self.get_sutepai_list()])
                print("ron waiting")
                if (self.player.action == 3
                    and player_other1.judge_phase_end
                    and player_other2.judge_phase_end
                        and player_other3.judge_phase_end):

                    # 流局
                    if len(self.game.tiles) <= 0:
                        self.n.send("ryukyoku")
                        print("send ryukyoku")
                    else:
                        self.n.send("next")
                        print("send next")

            # 別のユーザーのターンの時
            else:

                # print("waiting...")
                # print(self.player.judge_phase_end)
                if not self.player.judge_phase_end:
                    self.se_dahai.play()
                    print("ロン判定")
                    self.game = self.n.send("hantei_ron")
                    print("send hantei_ron")
                    if self.game.player_list[self.player_no].able_to_win:
                        self.drawing(self.get_ron_button_list())
                        if self.wait_for_mouse_click_agari():
                            print("ロン！")
                            self.n.send("agari_ron")
                        else:
                            self.n.send("reject_win")
                            print("続行")
                            self.drawing(
                                self.remove_tumo_and_skip_button_list())
                    self.n.send("end_of_judge")
                    print("send end_of_judge")
            self.events()

# メモ: Rect(切り抜く画像の始点x, 切り抜く画像の始点y, 切り抜く大きさx, 切り抜く大きさy)
# current_turn % 4(==turn_pos) は親(東)の位置(始点)を表している

    # params: Rect_list
    # return: None, 画面の更新
    def drawing(self, args_rect_list):
        rect_list = args_rect_list
        pg.display.update(rect_list)

    # return: オーラス表示Rect_list
    def get_olas_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(self.olas_img, (300, 300)))
        return rect_list

    # return: None, 場が変わった時の初期描画
    def drawing_change_ba_screen(self, current_ba_count):
        self.drawing(
            [*self.get_bg_img_list(),
            *self.get_dora_list(),
            *self.get_tepai_others_list(),
            *self.get_tepai_list(),
            *self.get_info_text_list(current_ba_count),
            #  *self.remove_nokori_text_list(),
            *self.get_nokori_text_list(),
            *self.get_wind_list(current_ba_count)])

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
                self.ura_mini, 180), (450 + (i * 65), 40))))

        # 上家手牌
        for i in range(5):
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ura_mini, 270), (20, 300 + (i * 65))))

        return rect_list

    # return: 残り牌数Rect_list
    def get_nokori_text_list(self):
        rect_list = []
        nokori_pai_count_text = self.font.render(
            f'余 {len(self.game.tiles)}', True, CYAN)
        rect_list.append(self.screen.blit(nokori_pai_count_text, (485, 530)))
        return rect_list

    # return: 残り牌数非表示化Rect_list
    def remove_nokori_text_list(self):
        rect_list = []
        rect_list.append(self.screen.blit(
            self.bg_yama, (475, 525), (95, 145, 80, 35)))

        return rect_list

    # return: 現場、各ポイント、余り牌のRect_list
    def get_info_text_list(self, ba_count):
        rect_list = []
        wind_list = ['東', '南', '西', '北']
        xy_list = [(500, 570), (570, 510), (500, 440), (440, 510)]

        rect_list.append(self.screen.blit(
            self.bg_img, (380, 380), (380, 380, 270, 273)))

        rect_list.append(self.screen.blit(
            self.bg_yama, (380, 380), (0, 0, 270, 273)))

        wind_text = self.font.render(f'{wind_list[ba_count]}', True, CYAN)
        for i in range(4):
            point_text = self.font.render(
                f'{self.game.player_list[(self.player_no + i) % 4].point}', True, YELLOW)
            rect_list.append(self.screen.blit(
                pg.transform.rotate(point_text, 90 * i), xy_list[i]))
        rect_list.append(self.screen.blit(wind_text, (503, 485)))

        return rect_list

    # return: 背景と山のRect_list
    def get_bg_img_list(self):
        rect_list = []
        font = pg.font.Font(FONT_NAME, 32)
        name = font.render(f'あなたはPlayer{self.player_no}', True, WHITE)
        rect_list.append(self.screen.blit(self.bg_img, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_yama, (380, 380)))
        rect_list.append(self.screen.blit(name, (700, 0)))

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
            y = 655 + (87 * int(k / 5))
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
            y = 290 - (87 * int(k / 5))
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

    # return: 他家のツモを非表示Rect_list
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

        if self.game.winner_player.name == self.player_no:
            rect_list.append(self.screen.blit(self.tumo_efe_img, (350, 600)))

        # 下家
        if self.game.winner_player.name == (self.player_no + 1) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 90), (650, 350)))

        # 対面
        if self.game.winner_player.name == (self.player_no + 2) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 180), (380, 270)))

        # 上家
        if self.game.winner_player.name == (self.player_no + 3) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.tumo_efe_img, 270), (270, 300)))

        return rect_list

    # return: ロンの表示効果Rect_list
    def get_ron_effect_list(self):
        rect_list = []
        print(self.game.winner_player)

        if self.game.winner_player.name == self.player_no:
            rect_list.append(self.screen.blit(self.ron_efe_img, (350, 600)))

        # TODO: 後で位置調整する
        # 下家
        if self.game.winner_player.name == (self.player_no + 1) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 90), (650, 350)))

        # 対面
        if self.game.winner_player.name == (self.player_no + 2) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 180), (380, 270)))

        # 上家
        if self.game.winner_player.name == (self.player_no + 3) % 4:
            rect_list.append(self.screen.blit(pg.transform.rotate(
                self.ron_efe_img, 270), (270, 300)))

        return rect_list

    # return: リザルト画面の背景Rect_list
    def get_result_back_screen_list(self, chara_img):
        rect_list = []

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_result, (0, 200)))
        rect_list.append(self.screen.blit(chara_img, (0, 200)))
        rect_list.append(self.screen.blit(self.han_img, (750, 550)))

        return rect_list

    # return: リザルト画面の手牌表示Rect_list
    def get_result_tepai_list(self, player):
        rect_list = []

        for mentu in player.agari_hands:
            for i, pai in enumerate(mentu.mentu1.tiles):
                rect_list.append(self.screen.blit(pg.transform.scale(pg.image.load(
                    os.path.join('Images', pai.pic)), TILE_MINI_SIZE).convert_alpha(), (600 + (i * int(TILE_WIDTH * 0.6)), 250)))

            for i, pai in enumerate(mentu.mentu2.tiles):
                rect_list.append(self.screen.blit(pg.transform.scale(pg.image.load(
                    os.path.join('Images', pai.pic)), TILE_MINI_SIZE).convert_alpha(), (789 + (i * int(TILE_WIDTH * 0.6)), 250)))

        return rect_list

    # return: リザルト画面の最終スコア表示Rect_list
    def get_result_score_text_list(self, player):
        rect_list = []

        font = pg.font.Font(FONT_NAME, 60)
        score = player.score
        text_score = font.render(f'{score}', True, YELLOW)

        if player.score >= 10:
            rect_list.append(self.screen.blit(self.yakuman_img, (520, 550)))
        rect_list.append(self.screen.blit(text_score, (790, 580)))
        rect_list.append(self.screen.blit(self.ten_img, (830, 630)))

        return rect_list

    # return: リザルト画面の基本テキストRect_list
    def get_result_base_text_list(self, player, tumo_ron):
        rect_list = []

        font = pg.font.Font(FONT_NAME, 48)
        text_title = None
        score = player.score
        title = font.render(f'和了！', True, YELLOW)
        if tumo_ron == 0:
            text_title = font.render(f'ツモ！', True, YELLOW)
        else:
            text_title = font.render(f'ロン！', True, YELLOW)
        text_name = font.render(
            f'Player{self.game.winner_player.name}', True, YELLOW)

        rect_list.append(self.screen.blit(text_name, (500, 350)))
        rect_list.append(self.screen.blit(title, (870, 350)))
        rect_list.append(self.screen.blit(text_title, (700, 350)))

        return rect_list

    # return: リザルト画面の役表示テキストRect_list
    def get_result_yaku_text_list(self, yaku, pos):
        rect_list = []

        font_mini = pg.font.Font(FONT_NAME, 32)
        rect_list.append(self.screen.blit(
            font_mini.render(yaku, True, WHITE), pos))

        return rect_list

    # return: None リザルト画面表示
    def result_screen_flow(self, chara_img, tumo_ron, player):
        self.drawing(self.get_result_back_screen_list(chara_img))
        self.drawing(self.get_result_tepai_list(player))
        self.drawing(self.get_result_base_text_list(player, tumo_ron))

        count = 0
        pos_list = [(500, 420), (500, 470), (500, 520),
                    (500, 570), (700, 420), (700, 470), (700, 530)]

        pg.time.delay(1000)
        for index, i in enumerate(player.judge_yaku, 0):
            if i == 0:
                continue
            if index == 0:
                self.drawing(self.get_result_yaku_text_list(
                    "タンヤオ", pos_list[count]))
                count += 1
            elif index == 1:
                self.drawing(self.get_result_yaku_text_list(
                    "チャンタ", pos_list[count]))
                count += 1
            elif index == 2:
                self.drawing(self.get_result_yaku_text_list(
                    "緑一色", pos_list[count]))
                count += 1
            elif index == 3:
                self.drawing(self.get_result_yaku_text_list(
                    "チンヤオ", pos_list[count]))
                count += 1
            elif index == 4:
                self.drawing(self.get_result_yaku_text_list(
                    "スーパレッド", pos_list[count]))
                count += 1
            elif index == 5:
                self.drawing(self.get_result_yaku_text_list(
                    "赤ドラ", pos_list[count]))
                count += 1
            elif index == 6:
                self.drawing(self.get_result_yaku_text_list(
                    "ドラ", pos_list[count]))
                count += 1
            self.se_yaku.play()
            pg.time.delay(500)

        pg.time.delay(1000)
        self.drawing(self.get_result_score_text_list(player))
        self.se_score.play()

    # return: None, タイプ別リザルト画面表示処理
    def result_flow(self):
        # # debug
        # self.game.is_ron = True
        # self.game.winner_player = self.game.player_list[self.player_no]
        # self.game.winner_player.agari_hands = [
        #     Agari(Mentu('koutu', [Tile('souzu', 2) for x in range(3)]), Mentu('koutu', [Tile('souzu', 7) for x in range(3)]))]
        # self.game.winner_player.judge_yaku = [1, 1, 1, 1, 1, 3, 1]
        # self.game.winner_player.score = 5

        pg.mixer.music.stop()
        if self.game.is_ron:
            self.se_ron.play()
            self.drawing(self.get_ron_effect_list())
            pg.time.delay(1500)  # 余韻
            self.result_screen_flow(
                self.senpai_img, 0, self.game.winner_player)
        elif self.game.is_tumo:
            self.se_tumo.play()
            self.drawing(self.get_tumo_effect_list())
            pg.time.delay(1500)  # 余韻
            self.result_screen_flow(
                self.kouhai_img, 1, self.game.winner_player)
        else:
            font = pg.font.Font(FONT_NAME, 60)
            text = font.render('流局', True, WHITE)
            if self.game.ron_count >= 2:
                text_d = font.render('同時ロン', True, WHITE)
                self.drawing(self.screen.blit(text_d, (450, 500)))
            self.se_noten.play()
            self.drawing([self.screen.blit(self.bg_img_opa60, (0, 0)),
                          self.screen.blit(text, (450, 450))])

    # return: 最終リザルト発表の背景Rect_list
    def get_last_result_screen_bg_list(self):
        rect_list = []
        font = pg.font.Font(FONT_NAME, 48)

        syukyoku_text = font.render("終局", True, WHITE)

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(syukyoku_text, (450, 100)))
        rect_list.append(self.screen.blit(self.kouhai_mini_img, (0, 200)))

        return rect_list

    # return: 最終リザルト発表の詳細Rect_list
    def get_last_result_screen_rank_player_list(self, rank, player):
        rect_list = []
        pos_bg = [(380, 300), (450, 450), (500, 550), (550, 650)]
        pos_rank_text = [(405, 300), (475, 455), (525, 555), (575, 655)]
        pos_rank_back_text = [(425, 350), (485, 490), (535, 590), (585, 690)]
        pos_hude = [(400, 300), (470, 455), (520, 555), (570, 655)]
        pos_player_name_text = [(500, 330), (560, 480), (610, 580), (660, 680)]
        pos_ten = [(830, 330), (815, 470), (865, 570), (915, 670)]
        pos_point = [(785, 325), (785, 472), (835, 572), (880, 672)]
        font = pg.font.Font(FONT_NAME, 48)
        font_mini = pg.font.Font(FONT_NAME, 32)
        rank_text = None
        rank_back_text = None
        player_name_text = None
        point_text = None

        if rank == 0:
            rect_list.append(self.screen.blit(
                self.result_bar_one_img, pos_bg[rank]))
            rank_text = font.render(f'{rank + 1}', True, YELLOW)
            rank_back_text = font.render(f'位', True, YELLOW)
            player_name_text = font.render(
                f'Player {player.name}', True, YELLOW)
            point_text = font.render(
                f'{player.point}', True, YELLOW)
            rect_list.append(self.screen.blit(pg.transform.scale(
                self.hude_img, (65, 109)), pos_hude[rank]))
            rect_list.append(self.screen.blit(pg.transform.scale(
                self.ten_img, (48, 42)), pos_ten[rank]))
            rect_list.append(self.screen.blit(point_text, pos_point[rank]))
        else:
            rect_list.append(self.screen.blit(
                self.result_bar_img, pos_bg[rank]))
            rank_text = font_mini.render(f'{rank + 1}', True, WHITE)
            rank_back_text = font_mini.render(f'位', True, WHITE)
            player_name_text = font_mini.render(
                f'Player {player.name}', True, WHITE)
            point_text = font_mini.render(
                f'{player.point}', True, WHITE)
            rect_list.append(self.screen.blit(self.hude_img, pos_hude[rank]))
            rect_list.append(self.screen.blit(self.ten_img, pos_ten[rank]))
            rect_list.append(self.screen.blit(point_text, pos_point[rank]))

        rect_list.append(self.screen.blit(rank_text, pos_rank_text[rank]))
        rect_list.append(self.screen.blit(
            rank_back_text, pos_rank_back_text[rank]))
        rect_list.append(self.screen.blit(
            player_name_text, pos_player_name_text[rank]))

        return rect_list

    # return: None, 最終リザルト画面表示処理
    def last_result_flow(self):
        self.drawing(self.get_last_result_screen_bg_list())

        player_list = sorted(self.game.player_list,
                             key=lambda player: player.point, reverse=True)
        # 3, 2, 1, 0...
        for i in reversed(range(4)):
            self.drawing(
                self.get_last_result_screen_rank_player_list(i, player_list[i]))
            if i == 0:
                self.se_rank1.play()
            else:
                self.se_rank2_4.play()

            pg.time.delay(2000)

        self.drawing(self.screen.blit(self.kakunin_img, (800, 800)))
        # TODO: 確認ボタンクリックでタイトルに戻る

        pg.time.delay(3000)

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()

        # ロン・ツモ用のマウスクリックHelper関数

    def wait_for_mouse_click_kakunin(self):
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
                    if x >= 800 and x <= 921 and y >= 800 and y <= 850:
                        waiting = False
                        return True

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
