import pygame as pg
from settings import *

class Pai(pg.sprite.Sprite):
    def __init__(self, name, img_url):
        super().__init__()
        self.name = name
        self.img = pg.image.load(img_url)

    def getImg(self):
        return self.name # mainの方でbiltで出力する