# Code made by Kaba
from ast import literal_eval
from _thread import *
from network import *
from os import path
from os import remove
import pygame as pg
import pickle
import socket
import time

pg.init()

global WIDTH, HEIGHT, TILESIZE, FPS, DEBUG, OFFSET, SERVER_OFFSET, LEVEL
LEVEL = []
WIDTH = 800
HEIGHT = 600
TILESIZE = 48
FPS = 60
DEBUG = False
OFFSET = [0,0]
SERVER_OFFSET = [0,0]

# server stuff
global connected
connected = False
port = 8000      #
server_ip = None # Deafult values

# pygame stuff
clock = pg.time.Clock()
allSprites = pg.sprite.Group()
#buttons = pg.sprite.Group() # not useful, cuz buttons are pygame rects
playerGroup = pg.sprite.Group()
tilesGroup = pg.sprite.Group()

Font = pg.font.SysFont("Arial", 25,bold=False,italic=False)
Font2 = pg.font.SysFont("Arial", 20,bold=False,italic=False)
Font3 = pg.font.SysFont("Arial", 30,bold=False,italic=False)

screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("Dungeon explorer")

# texture loading
player_textures = [] # N, E, S, W <- this order needs to be followed
tile_textures = []
img_dir = path.join(path.dirname(__file__),"textures")

for texture in range(8):
    player_textures.append(pg.transform.scale(pg.image.load(path.join(img_dir,"player_debug{0}.png".format(texture+1))).convert_alpha(),(int(TILESIZE/2),int(TILESIZE/2))))

tile_textures.append(pg.transform.scale(pg.image.load(path.join(img_dir,"o.png")),(TILESIZE,TILESIZE)))

class Button:
    def __init__(self, x, y, text_x, text_y, text, color, font, return_value, width=140, height=60,):
        self.text_x, self.text_y = text_x, text_y
        self.width, self.height = width, height
        self.value = return_value
        self.x, self.y = x, y
        self.text = text
        self.font = font
        self.color = color

        self.label = self.font.render(str(self.text),1,(255,255,255))
    def update(self):
        pg.draw.rect(screen, self.color, pg.Rect(self.x, self.y, self.width, self.height))
        screen.blit(self.label, (self.x + self.text_x, self.y + self.text_y))

        keys = pg.mouse.get_pressed()
        if keys[0]:
            pos = pg.mouse.get_pos()
            if pos[0] - self.x >= 0 and pos[0] - self.x <= self.width and pos[1] - self.y >= 0 and pos[1] - self.y <= self.height:
                return self.value
            else:
                return 0
        else:
            return 0

class Input_Cursor:
    def __init__(self, x, y, time2, distance):
        self.x, self.y = x, y
        self.time2 = time2
        self.tick = 0
        self.dist = distance

    def update(self):
        if self.tick >= self.time2:
            pg.draw.rect(screen, (255,255,255), pg.Rect(self.x, self.y, 20, 3))
        if self.tick >= self.time2*2:
            self.tick = 0

        self.tick += 1
    def forward(self):
        self.x += self.dist
    def back(self):
        self.x -= self.dist

class Player(pg.sprite.Sprite):
    def __init__(self, textures, WIDTH, HEIGHT):
        pg.sprite.Sprite.__init__(self)
        self.txt = textures
        self.image = self.txt[0]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = WIDTH/2, HEIGHT/2
        self.facing = 0 # 0 = S; 1 = SW; 2 = W; 3 = NW; 4 = N; 5 = NE; 6 = E; 7 = SE;
        self.speed = 3

    def update(self, OFFSET, WIDTH, HEIGHT, tiles, playerGroup):
        keys = pg.key.get_pressed()
        x_before = self.rect.x
        y_before = self.rect.y
        OFFSET_x_before = OFFSET[0]
        OFFSET_y_before = OFFSET[1]

        # animations and movement
        if keys[pg.K_s]:
            if keys[pg.K_a] and keys[pg.K_d] or not keys[pg.K_a] and not keys[pg.K_d]:
                self.facing = 0

                if self.rect.bottom + self.speed < (HEIGHT/8)*7:
                    self.rect.y += self.speed
                elif self.rect.bottom + self.speed + 1 > (HEIGHT/8)*7:
                    OFFSET[1] -= self.speed
            elif keys[pg.K_a]: 
                self.facing = 1

                if self.rect.bottom + self.speed < (HEIGHT/8)*7 and self.rect.x - self.speed > WIDTH/8:
                    self.rect.y += self.speed
                    self.rect.x -= self.speed

                else:
                    if self.rect.bottom + self.speed < (HEIGHT/8)*7:
                        self.rect.y += self.speed
                    elif self.rect.bottom + self.speed + 1 > (HEIGHT/8)*7:
                        OFFSET[1] -= self.speed
                    if self.rect.left - self.speed > WIDTH/8:
                        self.rect.x -= self.speed
                    elif self.rect.left - self.speed - 1 < WIDTH/8:
                        OFFSET[0] += self.speed
            elif keys[pg.K_d]:
                self.facing = 7

                if self.rect.bottom + self.speed + 1 < (HEIGHT/8)*7 and self.rect.right < (WIDTH/8)*7:
                    self.rect.y += self.speed
                    self.rect.x += self.speed

                else:
                    if self.rect.bottom + self.speed < (HEIGHT/8)*7:
                        self.rect.y += self.speed
                    elif self.rect.bottom + self.speed + 1 > (HEIGHT/8)*7:
                        OFFSET[1] -= self.speed
                    if self.rect.right + self.speed + 1 < (WIDTH/8)*7:
                        self.rect.x += self.speed
                    elif self.rect.right + self.speed + 1> (WIDTH/8)*7:
                        OFFSET[0] -= self.speed
        elif keys[pg.K_w]:
            if keys[pg.K_a] and keys[pg.K_d] or not keys[pg.K_a] and not keys[pg.K_d]:
                self.facing = 4

                if self.rect.top - self.speed > HEIGHT/8:
                    self.rect.y -= self.speed
                elif self.rect.top - self.speed - 1 < HEIGHT/8:
                    OFFSET[1] += self.speed
            elif keys[pg.K_a]:
                self.facing = 3
                
                if self.rect.top - self.speed - 1 > HEIGHT/8 and self.rect.left - 1 > WIDTH/8:
                    self.rect.y -= self.speed
                    self.rect.x -= self.speed

                else:
                    if self.rect.top - self.speed > HEIGHT/8:
                        self.rect.y -= self.speed
                    elif self.rect.top - self.speed - 1 < HEIGHT/8:
                        OFFSET[1] += self.speed
                    if self.rect.left- self.speed > WIDTH/8:
                        self.rect.x -= self.speed
                    elif self.rect.left- self.speed - 1< WIDTH/8:
                        OFFSET[0] += self.speed
            elif keys[pg.K_d]:
                self.facing = 5

                if self.rect.top - self.speed - 1 > HEIGHT/8 and self.rect.right + 1 < (WIDTH/8)*7:
                    self.rect.y -= self.speed
                    self.rect.x += self.speed

                else:
                    if self.rect.top - self.speed > HEIGHT/8:
                        self.rect.y -= self.speed
                    elif self.rect.top - self.speed - 1 < HEIGHT/8:
                        OFFSET[1] += self.speed
                    if self.rect.right + self.speed < (WIDTH/8)*7:
                        self.rect.x += self.speed
                    elif self.rect.right + self.speed  + 1 > (WIDTH/8)*7:
                        OFFSET[0] -= self.speed      
        else:
            if keys[pg.K_a]:
                self.facing = 2

                if self.rect.left - self.speed > WIDTH/8:
                    self.rect.x -= self.speed
                elif self.rect.left - self.speed - 1< WIDTH/8:
                    OFFSET[0] += self.speed
            if keys[pg.K_d]:
                self.facing = 6

                if self.rect.right + self.speed < (WIDTH/8)*7:
                    self.rect.x += self.speed
                elif self.rect.right + self.speed + 1> (WIDTH/8)*7:
                    OFFSET[0] -= self.speed

        if not len(pg.sprite.groupcollide(playerGroup, tiles, False, False)) == 0:
            self.rect.x = x_before
            self.rect.y = y_before
            OFFSET[0] = OFFSET_x_before
            OFFSET[1] = OFFSET_y_before

        self.image = self.txt[self.facing]

    def draw_hitbox(self, screen):
        pg.draw.line(screen, (0,255,0), (self.rect.left, self.rect.top), (self.rect.right, self.rect.top))
        pg.draw.line(screen, (0,255,0), (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom))
        pg.draw.line(screen, (0,255,0), (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom))
        pg.draw.line(screen, (0,255,0), (self.rect.right, self.rect.bottom), (self.rect.right, self.rect.top))
        pg.draw.line(screen, (0,255,0), (self.rect.left, self.rect.top), (self.rect.right, self.rect.bottom))
        pg.draw.line(screen, (0,255,0), (self.rect.right, self.rect.top), (self.rect.left, self.rect.bottom))

class Other_Player(pg.sprite.Sprite):
    def __init__(self, username, x, y, txt):
        pg.sprite.Sprite.__init__(self)
        self.txt = txt
        self.image = self.txt[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.username = username

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw_hitbox(self, screen):
        pg.draw.line(screen, (0,0,255), (self.rect.left, self.rect.top), (self.rect.right, self.rect.top))
        pg.draw.line(screen, (0,0,255), (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom))
        pg.draw.line(screen, (0,0,255), (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom))
        pg.draw.line(screen, (0,0,255), (self.rect.right, self.rect.bottom), (self.rect.right, self.rect.top))
        pg.draw.line(screen, (0,0,255), (self.rect.left, self.rect.top), (self.rect.right, self.rect.bottom))
        pg.draw.line(screen, (0,0,255), (self.rect.right, self.rect.top), (self.rect.left, self.rect.bottom))

class Tile(pg.sprite.Sprite):
    def __init__(self, txt, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = txt
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x, self.y = x, y

    def update(self, OFFSET):
        self.rect.x = self.x
        self.rect.y = self.y

        self.rect.x += OFFSET[0] 
        self.rect.y += OFFSET[1]

    def draw_hitbox(self, screen):
        pg.draw.line(screen, (255,0,0), (self.rect.left, self.rect.top), (self.rect.right, self.rect.top))
        pg.draw.line(screen, (255,0,0), (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom))
        pg.draw.line(screen, (255,0,0), (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom))
        pg.draw.line(screen, (255,0,0), (self.rect.right, self.rect.bottom), (self.rect.right, self.rect.top))

def get_other_pos(value):
    return (float(value[0]) + float(WIDTH/2) + float(SERVER_OFFSET[0]), float(value[1]) + float(HEIGHT/2) + float(SERVER_OFFSET[1]))

def CheckForNewPlayers(request, usernames):
    for index, player in enumerate(request[1]):
        if player not in usernames:
            usernames.append(player)
            p2_pos = get_other_pos(request[2][index])
            p2 = Other_Player(player, p2_pos[0], p2_pos[1], player_textures)
            allSprites.add(p2)
    return usernames

def updateMap(current_lvl):
    global tilesGroup, LEVEL
    lvl_dir = path.join(path.dirname(__file__),"levels")
    tilesGroup = pg.sprite.Group()
    
    file_contents = None
    with open(path.join(lvl_dir, "temp.lvl"), "rb") as file:
        file_contents = file.read()
        with open(path.join(lvl_dir, "level{0}.lvl".format(current_lvl)), "wb") as file2:
            pickle.dump(file_contents, file2)
        
    remove(path.join(lvl_dir, "temp.lvl"))
    
    file_contents = literal_eval(file_contents.decode('utf-8'))
    LEVEL = []
    for x in file_contents:
        empty_list = []
        for y in x:
            empty_list.append(0)
        LEVEL.append(empty_list)
    for index_y, y in enumerate(file_contents):
        for index_x, x in enumerate(y):
            if file_contents[index_x][index_y] == 1:
                tile = Tile(tile_textures[0], index_x*TILESIZE, index_y*TILESIZE)
                tilesGroup.add(tile)
            LEVEL[index_x][index_y] = file_contents[index_x][index_y]

def draw_debug(WIDTH, HEIGHT):
    # lines
    pg.draw.line(screen, (0,255,255), (WIDTH/8, HEIGHT/8), ((WIDTH/8)*7, HEIGHT/8))
    pg.draw.line(screen, (0,255,255), (WIDTH/8, HEIGHT/8), (WIDTH/8, (HEIGHT/8)*7))
    pg.draw.line(screen, (0,255,255), (WIDTH/8, (HEIGHT/8)*7), ((WIDTH/8)*7, (HEIGHT/8)*7))
    pg.draw.line(screen, (0,255,255), ((WIDTH/8)*7, HEIGHT/8), ((WIDTH/8)*7, (HEIGHT/8)*7))

    # text

def multiplayer_game(n, username): # main game function
    global DEBUG, FPS, SERVER_OFFSET, OFFSET, LEVEL
    pg.display.set_caption("Dungeon explorer - {0}".format(username))
    lvl_dir = path.join(path.dirname(__file__),"levels")
    # server stuff
    client_id = None
    players_list = None
    current_players = [username]
    positions = None
    chat = None
    current_lvl = 0

    p = Player(player_textures, WIDTH, HEIGHT)
    playerGroup.add(p)

    # getting data
    test = n.send("REQUEST_LOAD_CHARACTER-{0};{1};{2}".format(username,"0.0,0.0",None))
    req1 = literal_eval(test) 
    # [request, player_list, positions, chat]; request = client_id; pos
    client_id = int(req1[0][0].split(";")[0])
    SERVER_OFFSET[0] = int(req1[0][0].split(";")[1])# - WIDTH/2
    SERVER_OFFSET[1] = int(req1[0][0].split(";")[2])# - HEIGHT/2
    positions = req1[2]

    while True: # main game loop
        mouse_pos = pg.mouse.get_pos()
        mouse_button = pg.mouse.get_pressed()
        request = ""
        reply = "" #[request, player_list, positions, chat]; request = client_id; pos , server_request
        screen.fill((0,0,0))

        # input 
        for event in pg.event.get():
            if event.type == pg.QUIT:
                n.send("REQUEST_LOGOUT;{0},{1}".format(p.rect.x + SERVER_OFFSET[0] + OFFSET[0] - WIDTH/2, p.rect.y + SERVER_OFFSET[1] + OFFSET[1] - HEIGHT/2))
                pg.quit()
                return 1

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F12:
                    DEBUG = not DEBUG

        # update
        tilesGroup.update(OFFSET)
        playerGroup.update(OFFSET, WIDTH, HEIGHT, tilesGroup, playerGroup)
        
        # server update
        try:
            reply = literal_eval(n.send("{0};{1},{2};{3}".format(request, p.rect.x + SERVER_OFFSET[0] + OFFSET[0] - WIDTH/2, p.rect.y + SERVER_OFFSET[1] + OFFSET[1] - HEIGHT/2, current_lvl)))
            if str(reply[3]) == "REQUEST_DOWNLOAD-MAP":
                recived_f = path.join(lvl_dir, "temp.lvl")
                with open(recived_f, "wb") as file:
                    data = n.receive()
                    while True:
                        data2 = n.receive()
                        if data2 == b"done":
                            file.write(data)
                            file.close()
                            break
                        file.write(data)
                        data += data2
                reply_test = literal_eval(n.send("{0};{1},{2};{3}".format(request, p.rect.x + SERVER_OFFSET[0] + OFFSET[0] - WIDTH/2, p.rect.y + SERVER_OFFSET[1] + OFFSET[1] - HEIGHT/2, current_lvl)))
                current_lvl = int(list(reply_test)[len(list(reply_test))-1]) 
                updateMap(current_lvl)
        except Exception as e: 
            label = Font3.render("Connection Lost!",1,(255,255,255))
            screen.blit(label, (10,10))
            print(e)

        current_players = CheckForNewPlayers(reply, current_players)

        for player1 in current_players:
            if not player1 == username:
                for index, player in enumerate(reply[1]):
                    if player1 == player:
                        pos = get_other_pos(reply[2][index])
                        for player2 in allSprites:
                            if player2.username == player1:
                                player2.update(pos[0], pos[1])

        # draw
        tilesGroup.draw(screen)
        allSprites.draw(screen)
        playerGroup.draw(screen)
        if DEBUG:
            p.draw_hitbox(screen)
            for sprite in allSprites:
                sprite.draw_hitbox(screen)
            draw_debug(WIDTH, HEIGHT)
        pg.display.flip()
        clock.tick(FPS)

def connecting(n, test):
    global connected
    while True:
        result = int(n.connect())
        if result == 1:
            connected = True
            return
        print("Tried connecting to: "+ str(n.server) +", but failed")

def main():
    buttons = []
    b = Button(WIDTH/2-70, HEIGHT/2, 43, 17, 'Start', (100, 245, 65), Font, 1, 140, 60)
    buttons.append(b)
    b = Button(WIDTH/2-70,HEIGHT/2+120, 28, 17, 'Wyjscie', (200, 40, 30), Font, 2, 140, 60)
    buttons.append(b)

    i = Input_Cursor(WIDTH/4, HEIGHT/2, 60, 10)
    ip = ''

    creator = Font2.render("Made by Kaba", 1, (255,255,255))
    label = Font3.render("Podaj ip serwera:",1,(255,255,255))

    while True:
        screen.fill((0,0,0))

        for button in buttons:
            value = button.update()
        
            if value == 1:
                buttons2 = []
                b = Button(WIDTH/4,(HEIGHT/4)*3, 30, 17, 'Powrot',(100, 245, 65), Font, 1)
                buttons2.append(b)

                back = False
                
                while True: 
                    screen.fill((0,0,0))
                    
                    for button in buttons2:
                        value = button.update()
                        
                        if value == 1:
                            back = True

                    # ip input 
                    i.update()
                    ip_input = Font2.render(ip, 1, (255,255,255))

                    screen.blit(label,(WIDTH/2-140, HEIGHT/4))
                    screen.blit(ip_input,(WIDTH/2-200, HEIGHT/2-20))

                    screen.blit(creator, (WIDTH-140, HEIGHT-25))
                    clock.tick(60)
                    pg.display.flip()

                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            pg.quit()
                            return 1
                        if event.type == pg.KEYDOWN:
                            if str(event.key) in "46 48 49 50 51 52 53 54 55 56 57".split(" "):
                                ip += str(chr(int(event.key)))
                                i.forward()

                            elif str(event.key) == '8':
                                i.back()
                                if len(ip) > 0:
                                    ip = ip[:-1]

                            elif str(event.key) == '13':
                                global connected
                                n = Network(ip)
                                label0 = Font3.render("Searching for a game.",1,(255,255,255))
                                label1 = Font3.render("Searching for a game..",1,(255,255,255))
                                label2 = Font3.render("Searching for a game...",1,(255,255,255))
                                username_label = Font3.render("Enter your username:",1,(255,255,255))

                                i2 = Input_Cursor(WIDTH/4-10, HEIGHT/2, 60, 17)

                                tick = 0
                                start_new_thread(connecting,(n,None))

                                while True:
                                    screen.fill((0,0,0))
                                    
                                    if connected: 
                                        username = ""
                                        while True:
                                            screen.fill((0,0,0))
                                            username_text = Font3.render(str(username),1,(255,255,255))

                                            screen.blit(username_text,(WIDTH/4,HEIGHT/2-35))
                                            screen.blit(username_label,(WIDTH/2-150,HEIGHT/4))

                                            i2.update()

                                            for event in pg.event.get():
                                                if event.type == pg.QUIT:
                                                    pg.quit()
                                                    return 1
                                                if event.type == pg.KEYDOWN:
                                                    if event.key == pg.K_RETURN:
                                                        multiplayer_game(n, username)
                                                        return 1
                                                    elif event.key == pg.K_BACKSPACE:
                                                        username = username[:-1]
                                                        if len(username) > 0:
                                                            i2.back()
                                                    else:
                                                        len1 = len(username)
                                                        username += event.unicode
                                                        if len1 != len(username):
                                                            i2.forward()

                                            pg.display.flip()
                                            clock.tick(60)

                                    if tick >= 0 and tick <= 60:
                                        screen.blit(label0,(10,10))
                                    elif tick > 60 and tick <= 120:
                                        screen.blit(label1,(10,10))
                                    elif tick > 120 and tick <= 180:
                                        screen.blit(label2,(10,10))
                                    elif tick >= 180:
                                        tick = 1
                                    
                                    tick += 1

                                    for event in pg.event.get():
                                        if event.type == pg.QUIT:
                                            pg.quit()
                                            return 1

                                    pg.display.flip()
                                    clock.tick(60)

                    if back:
                        break

            elif value == 2:
                pg.quit()
                return 1

        screen.blit(creator, (WIDTH-140, HEIGHT-25))
        clock.tick(60)
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return 1

if __name__ == "__main__":
    main()

