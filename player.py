# Sprite classes
import pygame as pg
from settings import *


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hands = []
        self.pop_hands = []
        self.point = 50

    def set_hands(self,hands):
        self.hands = hands

    def action(self, tumo):
        self.hands.append(tumo)
        # TODO: 役判別を書く
        # TODO: 1個牌を選ぶ

class Cpu(Player):
    def __init__(self):
        super().__init__()

class You(Player):
    def __init__(self):
        super().__init__()