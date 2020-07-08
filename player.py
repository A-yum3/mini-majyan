# Sprite classes
from abc import abstractmethod
import pygame as pg
from pygame.locals import *
from settings import *
import sys
import copy
from tile import *

# TODO: private要素をリファクタリング

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hands = []
        self.pop_hands = []
        self.point = 40
        self.wind_img = None

    def set_hands(self,hands):
        self.hands = hands

    def set_wind_img(self, wind_img):
        self.wind_img = wind_img

    @abstractmethod
    def dahai(self):
        pass

class You(Player):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def dahai(self):
        hand = None
        while hand == None:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
                    x, y = event.pos
                    print(x)
                    print(y)
                    if y >= 850 and y <= 990:
                        if x >= 270 and x <= 350:
                            hand = self.hands.pop(0)
                            break
                        elif x >= 355 and x <= 433:
                            hand = self.hands.pop(1)
                            break
                        elif x >= 448 and x <= 530:
                            hand = self.hands.pop(2)
                            break
                        elif x >= 535 and x <= 630:
                            hand = self.hands.pop(3)
                            break
                        elif x >= 635 and x <= 710:
                            hand = self.hands.pop(4)
                            break
                        elif x >= 800 and x <= 890:
                            hand = self.hands.pop(5)
                            break
        self.pop_hands.append(hand)
        return hand

class Cpu(Player):
    def __init__(self):
        super().__init__()
        self.reset_pai_dic()

    #TODO: 東西南北変わる時にリセットする
    def reset_pai_dic(self):
        self.pai_dic = {
        'souzu_1': 3, 'souzu_2': 3, 'souzu_3': 3, 'souzu_4': 3, 'souzu_5': 3,
        'souzu_6': 3, 'souzu_7': 3, 'souzu_8': 3, 'souzu_9': 3,
        'akazu_1': 1, 'akazu_2': 1, 'akazu_3': 1, 'akazu_4': 1, 'akazu_5': 1,
        'akazu_6': 1, 'akazu_7': 1, 'akazu_8': 1, 'akazu_9': 1,
        'tsangenpai_10': 4,'tsangenpai_11': 4 }

    #TODO: 自分のhandsの分も引く →タイミングを考慮
    def declear_pai_dic(self, pai):
        self.pai_dic[pai] -= 1

    def dahai(self, dora):
        mentu_kouho = copy.deepcopy(self.hands)
        mentu_kouho.sort(key=lambda hai: f'{hai.kind}{hai.value}')

        #TODO: メンツが２つあって５P以下の時は期待値が一番低くなる牌を切る状態になっているので修正する
        l_koutu = sorted([x for x in set(mentu_kouho) if mentu_kouho.count(x) >= 3])
        try:
            mentu = None
            if len(l_koutu) >= 1:
                for koutu in l_koutu:
                    mentu = Mentu(Mentu.KIND[1], [koutu for x in range(3)])
                    [mentu_kouho.remove(mentu.tiles[_]) for _ in range(3)]
            else:
                mentu = find_one_syuntu(mentu_kouho)
                [mentu_kouho.remove(mentu.tiles[_]) for _ in range(3)]
        except NoMentu:
            pass


            point_list = [0 for _ in range(len(mentu_kouho))]
            for index, pai in enumerate(mentu_kouho, 0):
                # 赤牌
                if pai.kind == Tile.SUUPAI[1] or (pai.kind == Tile.JIHAI and pai.value == 11):
                    point_list[index] += 15
                # ドラ
                if pai.kind == dora.kind and pai.value == dora.value:
                    point_list[index] += 15

            for index in range(len(mentu_kouho) - 1):

                pai_1_v = mentu_kouho[index].value
                pai_2_v = mentu_kouho[index + 1].value
                pai_1_k = mentu_kouho[index].kind
                pai_2_k = mentu_kouho[index + 1].kind

                # 検索用
                pai_1_prev = f'{pai_1_k}_{pai_1_v - 1}'
                pai_2_next = f'{pai_2_k}_{pai_2_v+ 1}'
                pai_1 = f'{pai_1_k}_{pai_1_v}'
                pai_2 = f'{pai_2_k}_{pai_2_v}'
                pai_1_2_between = f'{pai_1_k}_{pai_1_v + 1}'
                tile_is_souzu = pai_1_k == Tile.SUUPAI[0]


                if pai_1_k == pai_2_k:
                    # リャンメン
                    if ((pai_1_v != 1 or pai_2_v != 9)
                    and (pai_1_v + 1 == pai_2_v)
                    and not(pai_1_v == 10)):
                        nokori = self.pai_dic[pai_1_prev] + self.pai_dic[pai_2_next]
                        all_count = 6 if tile_is_souzu else 2
                        rate = nokori / all_count

                        # どちらかが既に山に０枚だったら成立しない
                        if self.pai.dic[pai_1_prev] < 1 or self.pai.dic[pai_2_next] < 1:
                            rate = 0

                        point_list[index] += 10 * rate
                        point_list[index + 1] += 10 * rate

                    # カンチャン
                    elif pai_1_v + 2 == pai_2_v:
                        nokori = self.dic[pai_1_2_between]
                        all_count = 3 if tile_is_souzu else 1
                        rate = nokori / all_count

                        point_list[index] += 5 * rate
                        point_list[index + 1] += 5 * rate

                    # ペンチャン
                    elif ((pai_1_v == 1 or pai_2_v == 9)
                    and pai_1_v + 1 == pai_2_v):
                        nokori = None
                        all_count = 3 if tile_is_souzu else 1
                        if pai_1_v == 1: # 3の枚数
                            nokori = self.dic[pai_2_next]
                        else : # 7の枚数
                            nokori = self.dic[pai_1_prev]
                        rate = nokori / all_count

                        point_list[index] += 5 * rate
                        point_list[index + 1] + 5 * rate

                    # トイツ --アカズはトイツが発生しない
                    elif pai_1_v == pai_2_v:
                        nokori = self.dic[pai_1]
                        all_count = 1
                        if pai_1_v == 10 or pai_1_v == 11: # 發中
                            all_count = 2
                        rate = nokori / all_count

                        point_list[index] += 8 * rate
                        point_list[index + 1] += 8 * rate

            hand_idx = point_list.index(min(point_list))
            hand = self.hands.pop(hand_idx)
            self.pop_hands.append(hand)
            return hand







