from pickle import *
import pygame as pg
from pygame import display, draw
from pygame.locals import *

from player import *
from settings import *
from tile import *

# TODO: 総合結果発表画面の作成
# TODO: メニュー画面の詳細作成
# TODO: 音楽の追加
# TODO: フリテン処理
# TODO: 再戦処理
# TODO: 役名を結果に表示する
# TODO: 上がり時の手牌表示
# TODO: オーラスの表示
# TODO: サーバー接続切れの時の処理調整
# TODO: 同時ロンが出来ないので考慮する
# TODO: 役判定が正しく行われてない可能性がある(コーツ・チャンタあたり)
# TODO: ルール説明のPDF


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

            # test
            # self.last_result_flow()

            if self.game.ba_count == 4:
                print("end game")
                self.running = False
                # TODO 総合結果発表画面の作成
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
            if self.game.ba_end:
                self.result_flow()
                self.n.send("ready")
                continue

            # 場が変わったら場を描画
            if current_ba_count != self.game.ba_count:
                print("Change ba")
                current_ba_count = self.game.ba_count
                current_tiles_len = 0
                current_turn = -1
                self.drawing(
                    [*self.get_bg_img_list(),
                     *self.get_dora_list(),
                     *self.get_tepai_others_list(),
                     *self.get_tepai_list(),
                     *self.get_info_text_list(current_ba_count),
                     #  *self.remove_nokori_text_list(),
                     *self.get_nokori_text_list(),
                     *self.get_wind_list(current_ba_count)])

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
                    self.drawing([*self.get_tepai_list(),
                                  *self.get_sutepai_list()])
                    continue
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
                        print("send ryukyoku")

            else:
                # 別のユーザーのターンの時
                # print("waiting...")
                # print(self.player.judge_phase_end)
                if not self.player.judge_phase_end:
                    print("ロン判定")
                    self.game = self.n.send("hantei_ron")
                    print("send hantei_ron")
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
                    print("send end_of_judge")
            self.events()

# メモ: Rect(切り抜く画像の始点x, 切り抜く画像の始点y, 切り抜く大きさx, 切り抜く大きさy)
# current_turn % 4(==turn_pos) は親(東)の位置(始点)を表している

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

    # return: リザルト画面のRect_list
    def get_result_screen_list(self, img):
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

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(self.bg_result, (0, 200)))
        rect_list.append(self.screen.blit(img, (100, 200)))
        rect_list.append(self.screen.blit(text_name, (600, 350)))
        rect_list.append(self.screen.blit(text_title, (600, 400)))
        rect_list.append(self.screen.blit(text_score, (800, 470)))

        return rect_list

    # return: 最終結果発表の背景Rect_list
    def get_last_result_screen_bg_list(self):
        rect_list = []
        font = pg.font.Font(FONT_NAME, 48)
        font_mini = pg.font.Font(FONT_NAME, 32)

        syukyoku_text = font.render("終局", True, WHITE)

        rect_list.append(self.screen.blit(self.bg_img_opa60, (0, 0)))
        rect_list.append(self.screen.blit(syukyoku_text, (450, 100)))
        rect_list.append(self.screen.blit(self.kouhai_mini_img, (0, 200)))

        return rect_list

    def get_last_result_screen_rank_player_list(self, rank, player):
        rect_list = []
        pos_bg = [(380, 300), (450, 450), (500, 550), (550, 650)]
        pos_rank_text = [(405, 300), (475, 455), (525, 555), (575, 655)]
        pos_rank_back_text = [(425, 350), (485, 490), (535, 590), (585, 690)]
        pos_hude = [(0, 0), (470, 455), (520, 555), (570, 655)]
        font = pg.font.Font(FONT_NAME, 48)
        font_mini = pg.font.Font(FONT_NAME, 32)
        rank_text = None
        rank_back_text = None

        if rank == 0:
            rect_list.append(self.screen.blit(
                self.result_bar_one_img, pos_bg[rank]))
            rank_text = font.render(f'{rank + 1}', True, YELLOW)
            rank_back_text = font.render(f'位', True, YELLOW)
        else:
            rect_list.append(self.screen.blit(
                self.result_bar_img, pos_bg[rank]))
            rank_text = font_mini.render(f'{rank + 1}', True, WHITE)
            rank_back_text = font_mini.render(f'位', True, WHITE)
        rect_list.append(self.screen.blit(self.hude_img, pos_hude[rank]))
        rect_list.append(self.screen.blit(rank_text, pos_rank_text[rank]))
        rect_list.append(self.screen.blit(
            rank_back_text, pos_rank_back_text[rank]))

        return rect_list

    # return: None, 結果画面表示処理
    def result_flow(self):
        if self.game.is_ron:
            self.drawing(self.get_ron_effect_list())
            pg.time.delay(1500)  # 余韻
            self.drawing(self.get_result_screen_list(self.senpai_img))
        elif self.game.is_tumo:
            self.drawing(self.get_tumo_effect_list())
            pg.time.delay(1500)  # 余韻
            self.drawing(self.get_result_screen_list(self.kouhai_img))
        pg.time.delay(3000)

    def last_result_flow(self):
        self.drawing(self.get_last_result_screen_bg_list())
        #TODO: 得点順にソートしたプレイヤーリスト
        self.drawing(
            self.get_last_result_screen_rank_player_list(3, 0))
        self.drawing(
            self.get_last_result_screen_rank_player_list(2, 0))
        self.drawing(
            self.get_last_result_screen_rank_player_list(1, 0))
        self.drawing(
            self.get_last_result_screen_rank_player_list(0, 0))

        pg.time.delay(5000)

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()

        # ロン・ツモ用のマウスクリックHelper関数

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
