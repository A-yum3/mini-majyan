import pygame as pg
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
        self.new()

    # ニューゲーム
    def new(self):
        self.player_list = [User(0), User(1), User(2), User(3)]
        self.ba_count = -1
        self.new_ba()

    def new_ba(self):
        self.current_turn = 0
        self.ba_count += 1
        # 捨て牌をリセット
        self.all_pop_pai = []
        # 全員の捨て牌リセット,
        for i in range(4):
            self.player_list[i].pop_hands = []
        # 牌をシャッフル
        self.tiles = Tile.create_yamahai()
        self.dora = self.tiles.pop()
        # 牌を配る
        for i in range(4):
            hands = [self.tiles.pop() for _ in range(5)]
            self.player_list[i].set_hands(hands)

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
        agareru, score = judge(player.hands, self.dora)
        # 親は素点＋２
        if player_no == self.ba_count:
            score += 2
        if agareru and score >= 5:
            player.able_to_win = True
            player.score = score
        player.action = 2

    def dahai(self, player_no, data):
        dahai_no = int(data[-1])
        player = self.player_list[player_no]
        player.pop_hands.append(player.hands.pop(dahai_no))
        # 理牌
        player.hands.sort(
            key=lambda hai: f'{hai.kind}{hai.value}')
        player.able_to_win = False
        player.action = 3

    def next_turn(self, player_no):
        self.current_turn += 1
        self.player_list[player_no].action = 0

    def connected(self):
        return self.ready
