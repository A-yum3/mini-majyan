import os


# Constant
TITLE = "Mini 麻雀"
# Macbook Proの内蔵モニター設定デフォルトでは表示できない
WIDTH = 1024
HEIGHT = 1024
FPS = 60
FONT_NAME = os.path.join('font', 'ackaisyo.ttf')
TILE_WIDTH = 89
TILE_HEIGHT = 145
TILE_MINI_SIZE = (int(TILE_WIDTH * 0.6), int(TILE_HEIGHT * 0.6))
WIND_BUDGE_WIDTH = int(41 * 1.1)
WIND_BUDGE_HEIGHT = int(41 * 1.1)

# Image
BG_IMG = os.path.join('Images', 'Table_Dif.jpg')
BG_YAMA = os.path.join('Images', 'bg.png')
BG_DORA = os.path.join('Images', 'dora.png')
BG_TOU = os.path.join('Images', 'tou.png')
BG_NAN = os.path.join('Images', 'nan.png')
BG_SYA = os.path.join('Images', 'sya.png')
BG_PEI = os.path.join('Images', 'pei.png')
BG_RESULT = os.path.join('Images', 'result.png')
BG_IMG_OPA60 = os.path.join('Images', 'bg_opa60.png')
TUMO = os.path.join('Images', 'tumo.png')
TUMO_1 = os.path.join('Images', 'tumo_1.png')
RON = os.path.join('Images', 'ron.png')
RON_1 = os.path.join('Images', 'ron_1.png')
SKIP = os.path.join('Images', 'skip.png')
URA = os.path.join('Images', 'ura.png')
SENPAI = os.path.join('Images', 'senpai.png')


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (27, 140, 141)
LIGHTGREY = (189, 195, 199)
GREEN = (60, 186, 84)
RED = (219, 50, 54)
YELLOW = (244, 194, 13)
BLUE = (72, 133, 237)
CYAN = (57, 183, 201)
