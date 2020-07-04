# Sprite classes
import pygame as pg
from pygame.locals import *
from settings import *
import sys


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hands = []
        self.pop_hands = []
        self.point = 40

    def set_hands(self,hands):
        self.hands = hands

    def dahai(self):
        hand = None
        while hand == None:
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_1:
                        hand = self.hands.pop(0)
                    if event.key == K_2:
                        hand = self.hands.pop(1)
                    if event.key == K_3:
                        hand = self.hands.pop(2)
                    if event.key == K_4:
                        hand = self.hands.pop(3)
                    if event.key == K_5:
                        hand = self.hands.pop(4)
                    if event.key == K_6:
                        hand = self.hands.pop(5)
        self.pop_hands.append(hand)
        return hand

class Cpu(Player):
    def __init__(self):
        super().__init__()

class You(Player):
    def __init__(self):
        super().__init__()

