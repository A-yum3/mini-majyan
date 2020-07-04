from random import random
import pygame as pg
import os
import random
from settings import *
import copy

class Tile(pg.sprite.Sprite):
    SUUPAI = 'souzu', 'akazu'
    JIHAI = 'sangenpai'
    COLORS = '發中'

    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind # 牌の種類(ソーズ・三元牌)
        self.value = value # 牌の値 1~9 發中
        self.pic = f'{kind}_{value}.png'
        self.img_size = pg.image.load(os.path.join('Images', self.pic)).get_size()
        self.img_string = pg.image.tostring(pg.image.load(os.path.join('Images', self.pic)), "RGB")

    def __repr__(self):
        return self.pic

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
        tiles = [Tile(kind, str(value)) for kind in Tile.SUUPAI for value in range(1, 1 + 9)]
        tiles += [Tile(Tile.SUUPAI[0], str(value)) for value in range(1, 1 + 9) for _ in range(2)]
        tiles += [Tile(Tile.JIHAI, value) for value, label in enumerate(Tile.COLORS, 1) for _in in range(4)]

        random.shuffle(tiles)
        random.shuffle(tiles)
        random.shuffle(tiles)
        return tiles

class Agari:
    def __init__(self, mentu1, mentu2):
        self.mentu1 = mentu1
        self.mentu2 = mentu2

    def __repr__(self):
        return f'[{repr(self.mentu1.tiles[0])},{repr(self.mentu1.tiles[1])},{repr(self.mentu1.tiles[2])}],'\
            f'[{repr(self.mentu2.tiles[0])},{repr(self.mentu2.tiles[1])},{repr(self.mentu2.tiles[2])}]'

class Mentu:
    KIND = 'syuntu', 'koutu'

    def __init__(self, kind, tiles):
        self.kind = kind
        self.tiles = tiles

class NoMentu(Exception):
    pass

def judge(hands):
    agari_hai = []

    mentu_kouho = copy.deepcopy(hands)
    mentu_kouho.sort(key=lambda hai: f'{hai.kind}{hai.value}')

    # コーツの種類
    l_koutu = sorted([x for x in set(mentu_kouho) if mentu_kouho.count(x) >= 3], key=lambda hai: f'{hai.kind}{hai.value}')

    # コーツが0個
    agari_hai.extend(agari_koutu0(mentu_kouho))

    # コーツが1個
    agari_hai.extend(agari_koutu1(mentu_kouho, l_koutu))

    # コーツが2個
    agari_hai.extend(agari_koutu2(mentu_kouho, l_koutu))

    return len(agari_hai) > 0

def agari_koutu0(mentu_kouho):
    try:
        hanteiyou = copy.deepcopy(mentu_kouho)

        first = find_one_syuntu(hanteiyou)
        [hanteiyou.remove(first.tiles[_]) for _ in range(3)]

        second = find_one_syuntu(hanteiyou)
        [hanteiyou.remove(second.tiles[_]) for _ in range(3)]

        return [Agari(first, second)]

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
                [hanteiyou.remove(first.tiles[_]) for _ in range(3)]

                result.append(Agari(first, second))

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






