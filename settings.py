import os


# Constant
TITLE = "Mini 麻雀"
WIDTH = 1024
HEIGHT = 1024
FPS = 60
FONT_NAME = os.path.join('font', 'ackaisyo.ttf')
TILE_WIDTH = 89
TILE_HEIGHT = 145
TILE_MINI_SIZE = (int(TILE_WIDTH * 0.6), int(TILE_HEIGHT * 0.6))
WIND_BUDGE_WIDTH = int(41 * 1.1)
WIND_BUDGE_HEIGHT = int(41 * 1.1)

# Music
BGM_TITLE = os.path.join('music', 'lobby.wav')
BGM_GAME = os.path.join('music', 'game.wav')
SE_DAHAI = os.path.join('music', 'dahai11.wav')
SE_START = os.path.join('music', 'start.wav')
SE_NOTEN = os.path.join('music', 'noten.wav')
# 好みで男性女性音声切り替える場合はコメントを逆にする
# SE_TUMO = os.path.join('music', 'tumo_ma.wav')
SE_TUMO = os.path.join('music', 'tumo_fe.wav')
# SE_RON = os.path.join('music', 'ron_ma.wav')
SE_RON = os.path.join('music', 'ron_fe.wav')
SE_BURN = os.path.join('music', 'burn.wav')
SE_YAKU = os.path.join('music', 'yaku.wav')
SE_SCORE = os.path.join('music', 'score.wav')
SE_RANK1 = os.path.join('music', '1.wav')
SE_RANK24 = os.path.join('music', '2-4.wav')

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
BG_IMG_OPA40 = os.path.join('Images', 'opa40.png')
TUMO = os.path.join('Images', 'tumo.png')
TUMO_1 = os.path.join('Images', 'tumo_1.png')
RON = os.path.join('Images', 'ron.png')
RON_1 = os.path.join('Images', 'ron_1.png')
SKIP = os.path.join('Images', 'skip.png')
URA = os.path.join('Images', 'ura.png')
SENPAI = os.path.join('Images', 'senpai.png')
KOUHAI = os.path.join('Images', 'kouhai.png')
RESULT_BAR = os.path.join('Images', 'last_result_other.png')
RESULT_BAR_ONE = os.path.join('Images', 'last_result_one.png')
HUDE = os.path.join('Images', 'hude.png')
HAN = os.path.join('Images', 'han.png')
TEN = os.path.join('Images', 'ten.png')
KAKUNIN = os.path.join('Images', 'kakunin.png')
YAKUMAN = os.path.join('Images', 'yakuman.png')
BG_MENU = os.path.join('Images', 'tanfang_bg.png')
BG_SCHOOL = os.path.join('Images', 'school.png')
BG_SUZUME = os.path.join('Images', 'suzume.png')
LOGO = os.path.join('Images', 'logo.png')
BATTLE = os.path.join('Images', 'syoubu.png')
SUZUME = os.path.join('Images', 'bird_suzume.png')
OLAS = os.path.join('Images', 'olas.png')

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
