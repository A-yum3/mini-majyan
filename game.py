from pygame.locals import *
from settings import *
from player import *
from tile import *


class Game:
    def __init__(self, id):
        self.playing = False
        self.player_list = None
        self.ready = False
        self.dora = None
        self.tiles = None
        self.id = id
        self.ba_end = None
        self.winner_player = None
        self.current_pop_tile = None
        self.is_ron = None
        self.is_tumo = None
        self.current_turn = None
        self.ba_count = None
        self.new()

    # ニューゲーム
    def new(self):
        self.player_list = [User(0), User(1), User(2), User(3)]
        self.ba_count = -1
        self.new_ba()

    def new_ba(self):
        self.current_turn = 0
        self.ba_count += 1
        self.ba_end = False
        self.winner_player = None
        self.current_pop_tile = None
        self.is_ron = False
        self.is_tumo = False

        # 捨て牌をリセット
        self.all_pop_pai = []
        # 全員の捨て牌リセット,
        for i in range(4):
            self.player_list[i].pop_hands = []
            self.player_list[i].judge_phase_end = True
            self.player_list[i].able_to_win = False
            self.player_list[i].ready = False
        # 牌をシャッフル
        self.tiles = Tile.create_yamahai()
        self.dora = self.tiles.pop()
        # 牌を配る
        for i in range(4):
            hands = [self.tiles.pop() for _ in range(5)]
            self.player_list[i].set_hands(hands)
            # 理牌
            self.player_list[i].hands.sort(
                key=lambda hai: f'{hai.kind}{hai.value}')

            # 飛んだらゲーム終了
            if self.player_list[i].point <= 0:
                self.ba_count = 4

    def tumo(self, player_no):
        tumo = self.tiles.pop()
        player = self.player_list[player_no]
        # 理牌
        player.hands.sort(
            key=lambda hai: f'{hai.kind}{hai.value}')
        player.hands.append(tumo)
        player.action = 1

    def hantei(self, player_no):
        player = self.player_list[player_no]
        # 役判定
        agareru, score, agari_hai, hantei_rel = judge(player.hands, self.dora)

        if agareru and score >= 5:
            player.able_to_win = True
            player.agari_hands = agari_hai
            player.judge_yaku = hantei_rel
            # 親は素点＋２
            if player_no == self.ba_count:
                score += 2
            player.score = score
        player.action = 2

    def hantei_ron(self, player_no):
        player = self.player_list[player_no]
        player.hands.append(self.current_pop_tile)
        self.hantei(player_no)
        # フリテン
        if self.current_pop_tile in player.pop_hands:
            player.able_to_win = False
            player.score = 0
        player.hands.pop()
        player.action = 0

    def dahai(self, player_no, data):
        dahai_no = int(data[-1])
        player = self.player_list[player_no]
        player.pop_hands.append(player.hands.pop(dahai_no))
        self.current_pop_tile = player.pop_hands[-1]
        # 理牌
        player.hands.sort(
            key=lambda hai: f'{hai.kind}{hai.value}')
        player.able_to_win = False

        for i in range(4):
            if i == player_no:
                continue
            self.player_list[i].judge_phase_end = False

        player.action = 3

    def next_turn(self, player_no):
        self.current_turn += 1
        self.player_list[player_no].action = 0

        self.current_pop_tile = None

    def reject_win(self, player_no):
        self.player_list[player_no].able_to_win = False

    def agari_tumo(self, player_no):
        # ツモアガリの時は上家からポイントを頂戴する
        score = self.player_list[player_no].score
        self.player_list[(player_no - 1) % 4].point -= score
        self.player_list[player_no].point += score
        self.winner_player = self.player_list[player_no]
        self.is_tumo = True
        self.ba_end = True

    def agari_ron(self, player_no):
        # ロンはロンされた相手からポイントを頂戴する
        turn_pos = self.current_turn + self.ba_count
        score = self.player_list[player_no].score
        self.player_list[(turn_pos % 4)].point -= score
        self.player_list[player_no].point += score
        self.winner_player = self.player_list[player_no]
        self.is_ron = True
        self.ba_end = True

    def end_of_judge(self, player_no):
        self.player_list[player_no].judge_phase_end = True

    def ryukyoku(self, player_no):
        self.ba_end = True
        self.winner_player = self.player_list[player_no]

    def ready_player(self, player_no):
        self.player_list[player_no].ready = True

    def connected(self):
        return self.ready
