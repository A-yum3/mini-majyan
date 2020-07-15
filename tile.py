import copy
import os
import random

import pygame as pg

from settings import *


class Tile(pg.sprite.Sprite):
    SUUPAI = 'souzu', 'akazu'
    JIHAI = 'tsangenpai'  # ソートの関係上
    COLORS = '發中'

    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind  # 牌の種類(ソーズ・三元牌)
        self.value = value  # 牌の値 1~9 發中
        self.pic = f'{kind}_{value}.png'
        # self.img_size = pg.image.load(os.path.join('Images', self.pic)).get_size()
        # self.img_string = pg.image.tostring(pg.image.load(os.path.join('Images', self.pic)), "RGB")

    def __repr__(self):
        return f'{self.kind}_{self.value}'

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.pic == other.pic

    def __hash__(self):
        return hash(self.pic)

    def sort_info(self):
        if Tile.SUUPAI[0] == self.kind:
            return f'0_{self.value}'
        elif Tile.SUUPAI[1] == self.kind:
            return f'1_{self.value}'
        elif Tile.JIHAI[0] == self.kind:
            return f'2_{self.value}'

    def create_yamahai():
        tiles = [Tile(kind, str(value))
                 for kind in Tile.SUUPAI for value in range(1, 1 + 9)]
        tiles += [Tile(Tile.SUUPAI[0], str(value))
                  for value in range(1, 1 + 9) for _ in range(2)]
        tiles += [Tile(Tile.JIHAI, value) for value,
                  label in enumerate(Tile.COLORS, 10) for _in in range(4)]

        random.shuffle(tiles)
        random.shuffle(tiles)
        random.shuffle(tiles)
        return tiles


class Agari:
    def __init__(self, mentu1, mentu2):
        self.mentu1 = mentu1
        self.mentu2 = mentu2

    def __repr__(self):
        return f'[{self.mentu1.tiles[0]},{self.mentu1.tiles[1]},{self.mentu1.tiles[2]}],'\
            f'[{self.mentu2.tiles[0]},{self.mentu2.tiles[1]},{self.mentu2.tiles[2]}]'


class Mentu:
    KIND = 'syuntu', 'koutu'

    def __init__(self, kind, tiles):
        self.kind = kind
        self.tiles = tiles


class NoMentu(Exception):
    pass


def judge(hands, dora):
    agari_hai = []

    mentu_kouho = copy.deepcopy(hands)
    mentu_kouho.sort(key=lambda hai: f'{hai.kind}{hai.value}')

    # コーツの種類
    l_koutu = sorted([x for x in set(mentu_kouho) if mentu_kouho.count(
        x) >= 3], key=lambda hai: f'{hai.kind}{hai.value}')

    # コーツが0個
    agari_hai.extend(agari_koutu0(mentu_kouho))

    # コーツが1個
    agari_hai.extend(agari_koutu1(mentu_kouho, l_koutu))

    # コーツが2個
    agari_hai.extend(agari_koutu2(mentu_kouho, l_koutu))

    score = -1

    if len(agari_hai) > 0:
        # TODO: 関数切り出し
        yakuman_score = agari_hai.pop()
        bonus_score = yakuman_score
        # タンヤオ、チャンタ, 緑一色、 チンヤオ, スーパーレッド
        # 緑 2,3,4,6,8,hatu
        hantei1 = [True for _ in range(5)]
        hantei2 = [True for _ in range(5)]
        bonus_point = [1, 2]
        yakuman_point = [10, 15, 20]
        for mentu in agari_hai:
            count1 = 0
            count2 = 0
            for pai in mentu.mentu1.tiles:
                p_value = int(pai.value)
                # 赤牌
                if pai.kind == Tile.SUUPAI[1] or (pai.kind == Tile.JIHAI and p_value == 11):
                    bonus_score += 1
                    print('red')
                # ドラ
                if pai.kind == dora.kind and p_value == int(dora.value):
                    bonus_score += 1
                    print('dora')

                # タンヤオ
                if not(p_value >= 2 and p_value <= 8):  # 1, 9, 字があったら
                    hantei1[0] = False
                    count1 += 1

                # 緑一色
                if not((p_value == Tile.SUUPAI[0] and
                        (p_value == 2 or p_value == 3 or p_value == 4 or p_value == 6 or p_value == 8)) or
                       (pai.kind == Tile.JIHAI and pai.value == 10)):
                    hantei1[2] = False

                # スーパーレッド
                if not((pai.kind == Tile.SUUPAI[1] or (pai.kind == Tile.JIHAI and p_value == 11))):
                    hantei1[4] = False

            for pai in mentu.mentu2.tiles:
                p_value = int(pai.value)
                # 赤牌
                if pai.kind == Tile.SUUPAI[1]:
                    bonus_score += 1
                    print("レッド")
                # ドラ
                if pai.kind == dora.kind and p_value == int(dora.value):
                    bonus_score += 1
                    print("ドラ")

                # タンヤオ
                if not(p_value >= 2 and p_value <= 8):  # 1, 9, 字があったら
                    hantei2[0] = False
                    count2 += 1

                # 緑一色
                if not((pai.kind == Tile.SUUPAI[0] and
                        (p_value == 2 or p_value == 3 or p_value == 4 or p_value == 6 or p_value == 8)) or
                       (pai.kind == Tile.JIHAI and p_value == 10)):
                    hantei2[2] = False

                # スーパーレッド
                if not((pai.kind == Tile.SUUPAI[1] or (pai.kind == Tile.JIHAI and p_value == 11))):
                    hantei2[4] = False

            # チャンタ
            if not((count1 >= 1 and count1 < 3) and (count2 >= 1 and count2 < 3)):
                hantei1[1] = False
                hantei2[1] = False

            # チンヤオ
            if not(count1 == 3 and count2 == 3):
                hantei1[3] = False
                hantei2[3] = False

        # 点数計算
        for pos in range(2):
            if hantei1[pos] and hantei2[pos]:
                bonus_score += bonus_point[pos]
                print(bonus_point[pos])

        for pos in range(3):
            if hantei1[pos + 2] and hantei2[pos + 2]:
                yakuman_score += yakuman_point[pos]
                print(yakuman_point[pos])

        score = max(yakuman_score, bonus_score)

    return [len(agari_hai) > 0, score]


def agari_koutu0(mentu_kouho):
    try:
        hanteiyou = copy.deepcopy(mentu_kouho)

        first = find_one_syuntu(hanteiyou)
        [hanteiyou.remove(first.tiles[_]) for _ in range(3)]

        second = find_one_syuntu(hanteiyou)
        [hanteiyou.remove(second.tiles[_]) for _ in range(3)]

        return [Agari(first, second), 2]

    except NoMentu:
        return []


def agari_koutu1(mentu_kouho, l_koutu):
    if len(l_koutu) < 1:
        return []

    result = []
    for koutu in l_koutu:
        try:
            hanteiyou = copy.deepcopy(mentu_kouho)

            first = Mentu(Mentu.KIND[1], [koutu for x in range(3)])
            [hanteiyou.remove(first.tiles[_]) for _ in range(3)]

            second = find_one_syuntu(hanteiyou)
            [hanteiyou.remove(second.tiles[_]) for _ in range(3)]

            result.append(Agari(first, second))
            result.append(3)

        except NoMentu:
            continue
    return result


def agari_koutu2(mentu_kouho, l_koutu):
    if len(l_koutu) < 2:
        return []

    result = []
    for i in range(len(l_koutu) - 1):
        for j in range(i + 1, len(l_koutu)):
            try:
                hanteiyou = copy.deepcopy(mentu_kouho)

                first = Mentu(Mentu.KIND[1], [l_koutu[i] for x in range(3)])
                [hanteiyou.remove(first.tiles[_]) for _ in range(3)]

                second = Mentu(Mentu.KIND[1], [l_koutu[j] for x in range(3)])
                [hanteiyou.remove(second.tiles[_]) for _ in range(3)]

                result.append(Agari(first, second))
                result.append(4)

            except NoMentu:
                continue

    return result


def find_one_syuntu(hanteiyou):
    hanteiyou.sort(key=lambda hai: f'{hai.kind}{hai.value}')
    for hanteiyou_one_tile in hanteiyou:
        syuntu_kouho = create_syuntu(hanteiyou_one_tile)
        if syuntu_kouho is None:
            continue
        if syuntu_kouho[1] in hanteiyou and syuntu_kouho[2] in hanteiyou:
            return Mentu(Mentu.KIND[0], syuntu_kouho)
    raise NoMentu()


def create_syuntu(tile):
    if tile.kind in Tile.SUUPAI and int(tile.value) <= 7:
        return [Tile(tile.kind, str(value))
                for value in range(int(tile.value), int(tile.value) + 3)]
