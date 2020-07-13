import pygame as pg
from pygame import draw
from pygame.locals import *
from settings import *
from player import *
from tile import *
from network import Network
pg.font.init()
pg.init()
pg.mixer.init()
win = pg.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
pg.display.set_caption(TITLE)


player_no = None


class Client:
    def __init__(self):
        self.running = True
        self.clock = pg.time.Clock()
        self.game = None
        self.screen = win
        self.turn_no = None
        self.font = pg.font.Font(FONT_NAME, 24)
        print("You are player", player_no)
        self.load_data()
        self.run()

    def load_data(self):
        self.bg_img = pg.transform.scale(
            pg.image.load(BG_IMG), (WIDTH, HEIGHT)).convert()
        self.bg_yama = pg.image.load(BG_YAMA)
        self.bg_dora = pg.image.load(BG_DORA)
        self.bg_tou = pg.transform.scale(pg.image.load(
            BG_TOU), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_nan = pg.transform.scale(pg.image.load(
            BG_NAN), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_sya = pg.transform.scale(pg.image.load(
            BG_SYA), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_pei = pg.transform.scale(pg.image.load(
            BG_PEI), (WIND_BUDGE_WIDTH, WIND_BUDGE_HEIGHT))
        self.bg_result = pg.image.load(BG_RESULT)
        self.my_ron = pg.image.load(MY_RON)
        self.my_tumo = pg.image.load(MY_TUMO)
        self.fonpai_img = [self.bg_tou, self.bg_pei, self.bg_sya, self.bg_nan]
        self.ura = pg.image.load(URA)
        self.tepai_rect = []

        # 上家手牌
        for i in range(5):
            self.tepai_rect.append(self.screen.blit(pg.transform.rotate(
                ura_mini, 90), (20, 300 + (i * 65))))

        # 対面手牌
        for i in range(5):
            self.tepai_rect.append((self.screen.blit(pg.transform.rotate(
                ura_mini, 0), (450 + (i * 65), 40))))

        # 下家手牌
        for i in range(5):
            self.tepai_rect.append(self.screen.blit(pg.transform.rotate(
                ura_mini, 90), (869, 400 + (i * 65))))

    def run(self):
        while self.running:
            self.clock.tick(30)
            try:
                self.game = n.send("fuck")
            except:
                self.running = False
                print("Couldn't get game")
                break
            print("check1")
            self.player = self.game.player_list[player_no]
            print(self.player.name)
            self.turn_no = self.game.current_turn + self.game.ba_count
            print(self.turn_no)
            self.draw(self.turn_no, self.game.ba_count)
            print("check4")
            # このユーザーのターン
            if player_no == self.turn_no % 4:
                if self.player.action == 0:
                    n.send("tumo")
                    print("send tumo")
                    self.draw_tepai(self.turn_no)
                    print("draw tepai")
                    pg.time.delay(2000)
                if self.player.action == 1:
                    n.send("hantei")
                    print("send hantei")
                if self.player.ableToWin:
                    # 上がり選択肢
                    # temp_rect = []
                    # temp_rect.append(self.screen.blit(
                    #     pg.image.load(TUMO), (480, 750)))
                    # temp_rect.append(self.screen.blit(
                    #     pg.image.load(SKIP), (700, 750)))
                    # pg.display.update(temp_rect)

                    # if self.wait_for_mouse_click():
                    #     print("ツモ！")
                    #     print(score)
                    #     # TODO: リザルト画面、点数交換処理
                    #     break
                    # else:
                    #     self.draw(turn)
                    #     print("続行")
                    pass
                if self.player.action == 2:
                    num = self.player.dahai()
                    n.send(f'dahai_{num}')
                    print(f"send dahai_{num}")
                if self.player.action == 3:
                    n.send("next")
                    print("send next")

                # 流局
                if len(self.game.tiles) <= 0:
                    n.send("new_ba")
                    print("send new_ba")
            else:
                # 別のユーザーのターンの時
                print("waiting...")
            print("test")

            self.events()

    ####################
    ##      描画      ##
    ####################

    def draw_info_text(self, turn, t_n_s_p):
        rect_list = []
        wind_list = ['東', '南', '西', '北']
        xy_list = [(500, 570), (570, 510), (500, 440), (440, 510)]

        nokori_pai_count_text = self.font.render(
            f'余 {len(self.game.tiles) - 1}', True, CYAN)
        wind_text = self.font.render(f'{wind_list[t_n_s_p]}', True, CYAN)
        for i in range(4):
            point_text = self.font.render(
                f'{self.game.player_list[(turn + i) % 4].point}', True, YELLOW)
            rect_list.append(self.screen.blit(
                pg.transform.rotate(point_text, 90 * i), xy_list[i]))
        rect_list.append(self.screen.blit(wind_text, (503, 485)))
        rect_list.append(self.screen.blit(nokori_pai_count_text, (485, 530)))

        rect_list.extend(self.tepai_rect)

        pg.display.update(rect_list)

    def draw_bg_img(self):
        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.bg_yama, (380, 380))

    def draw(self, turn, t_n_s_p):
        self.draw_bg_img()
        print("draw bg")

        self.screen.blit(self.bg_dora, (10, 10))
        self.screen.blit(pg.transform.scale(pg.image.load(
            os.path.join('Images', self.game.dora.pic)), (44, 72)), (110, 20))

        print("draw dora")

        self.draw_info_text(turn, t_n_s_p)
        print("draw info")
        self.draw_wind(t_n_s_p)
        print("draw wind")
        self.draw_tepai(turn)
        print("draw tepai")
        self.draw_sutepai(turn)
        print("draw sutepai")

        pg.display.update()

    def draw_wind(self, t_n_s_p):
        # 自分
        self.screen.blit(
            self.fonpai_img[(4 + (t_n_s_p - player_no)) % 4], (391, 597))
        # 下家
        self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (t_n_s_p - (player_no) + 1)) % 4], 90),  (594, 598))
        # 対面
        self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (t_n_s_p - (player_no) + 2)) % 4], 180), (594, 396))
        # 上家
        self.screen.blit(pg.transform.rotate(
            self.fonpai_img[(4 + (t_n_s_p - (player_no) + 3)) % 4], 270), (392, 396))

    def draw_tepai(self, turn):
        ura_mini = pg.transform.scale(self.ura, (65, 103))
        # player手牌
        for k, hand in enumerate(self.game.player_list[player_no].hands, 3):
            if k == 8:
                k = 9  # ツモは距離を離す
            self.screen.blit(pg.image.load(
                os.path.join('Images', hand.pic)), (k * TILE_WIDTH, 850))

    def draw_sutepai(self, turn):
        # player捨て牌
        for k, hand in enumerate(self.game.player_list[player_no].pop_hands, 0):
            x = 370 + ((k % 5) * 53)
            y = 650 + (87 * int(k / 5))
            temp_img = pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic)), TILE_MINI_SIZE)
            self.screen.blit(temp_img, (x, y))

        # 上家捨て牌
        for k, hand in enumerate(self.game.player_list[(player_no - 1) % 4].pop_hands, 0):
            x = 280 - (87 * int(k / 5))
            y = 380 + ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic), TILE_MINI_SIZE), 270))
            self.screen.blit(temp_img, (x, y))

        # 対面捨て牌
        for k, hand in enumerate(self.game.player_list[(player_no + 2) % 4].pop_hands, 0):
            x = 600 - ((k % 5) * 53)
            y = 300 - (87 * int(k / 5))
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic), TILE_MINI_SIZE), 180))
            self.screen.blit(temp_img, (x, y))

        # 下家捨て牌
        for k, hand in enumerate(self.game.player_list[(player_no + 3) % 4].pop_hands, 0):
            x = 650 + (87 * int(k / 5))
            y = 600 - ((k % 5) * 53)
            temp_img = pg.transform.rotate(pg.transform.scale(pg.image.load(
                os.path.join('Images', hand.pic), TILE_MINI_SIZE), 90))
            self.screen.blit(temp_img, (x, y))

    ####################
    ##    特別処理    ##
    ####################

    def events(self):
        # バツボタンを押されたら終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def wait_for_mouse(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.MOUSEBUTTONUP:
                    waiting = False

    def wait_for_mouse_click(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    return False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if x >= 490 and x <= 675 and y >= 760 and y <= 830:
                        waiting = False
                        return True
                    elif x >= 710 and x <= 900 and y >= 760 and y <= 820:
                        waiting = False
                        return False


def main():
    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(60)

        game = n.send("get")
        if game.connected():
            Client()
        else:
            waiting_screen()
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False


def waiting_screen():
    font = pg.font.SysFont("comicsans", 80)
    text = font.render("Waiting for Player...", 1, (255, 0, 0), True)
    win.blit(text, (int(WIDTH/2 - text.get_width() /
                        2), int(HEIGHT/2 - text.get_height()/2)))


def menu_screen():
    global n
    global player_no
    run = True
    clock = pg.time.Clock()
    offline = False

    while run:
        clock.tick(60)
        # メニュー画面描写
        win.fill((128, 128, 128))
        font = pg.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        small_font = pg.font.SysFont("comicsans", 50)
        win.blit(text, (100, 200))

        if offline:
            off = small_font.render(
                "Server Offline, Try Again Later...", 1, (255, 0, 0))
            win.blit(off, (int(WIDTH / 2 - off.get_width() / 2), 500))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                try:
                    n = Network()
                    player_no = int(n.getP())
                    if player_no is None:
                        raise "offline"
                    else:
                        run = False
                        main()
                        break
                except:
                    print("Server offline")
                    offline = True
                    player_no = None


menu_screen()
