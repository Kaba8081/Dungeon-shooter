from datetime import datetime
from classes import *
from _thread import *
from os import path
import colorama
import socket
import pickle

colorama.init()

def log(message,color):
    if color == 0: # Debug
        print("[{0}{1}{2}][{3}DEBUG{2}]{4}".format(colorama.Fore.GREEN, datetime.now().strftime("%H:%M:%S"), colorama.Style.RESET_ALL, colorama.Fore.GREEN, message))
    if color == 1: # Warning
        print("[{0}{1}{2}][{3}WARNING{2}]{4}".format(colorama.Fore.YELLOW, datetime.now().strftime("%H:%M:%S"), colorama.Style.RESET_ALL, colorama.Fore.YELLOW, message))
    if color == 2: # Error
        print("[{0}{1}{2}][{3}ERROR{2}]{4}".format(colorama.Fore.RED, datetime.now().strftime("%H:%M:%S"), colorama.Style.RESET_ALL, colorama.Fore.RED, message))

port = 8000
server_ip = str(input("Podaj ip serwera: "))
player_limit = int(input("Podaj limit graczy: "))
save_dir = path.join(path.dirname(__file__),"saves")
lvl_dir = path.join(path.dirname(__file__),"levels")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server_ip, port))
except Exception as e:
    log("Something went wrong...",2)
    log(e,2)

s.listen(player_limit)
log("Server started waiting for connections...",0)

global player_list, players_num, players_pos
player_list = []
players_pos = []
players_num = 0

global map, current_lvl
current_lvl = 1
map = []

def save_lvl(map, current_lvl):
    with open(path.join(lvl_dir, "level{0}.lvl".format(current_lvl)),"wb") as file:
        pickle.dump(map, file)

def Game_loop(debug1, debug2):
    generator = Cave_Generator(generator_options)
    cave = generator.generate_cave()

    for index_y, y in enumerate(cave):
        row = ""
        for index_x, x in enumerate(y):
            if cave[index_x][index_y] == 1:
                row += "1"
            else:
                row += "0"
        print(row)
    
    global map, current_lvl
    map = cave
    save_lvl(map, current_lvl)


def client(conn, addr, player):
    global player_list, players_num, players_pos, current_lvl, map
    nick = 'Unnamed'
    conn.send(str.encode('1'))

    while True:
        try:
            data = conn.recv(2048).decode() # request; position; current_lvl

            data = data.split(";")
            reply = [[]]                    # [request, player_list, positions, chat, server_request]

            if not data:
                log("{0} disconnected".format(addr),0)
                break
            if data[0].startswith("REQUEST"): # client requests
                if data[0].startswith("REQUEST_LOAD_CHARACTER"):
                    nick = data[0].split("-")[1]
                    
                    file_contents = None
                    if path.isfile(path.join(save_dir, "{0}.sav".format(nick))):
                        with open(path.join(save_dir, "{0}.sav".format(nick)), "rb") as file:
                            file_contents = pickle.load(file)
                    else:
                        log("There was no save file for {0}, so a new file was created".format(nick),1)
                        with open(path.join(save_dir, "{0}.sav".format(nick)), "wb") as file:
                            file_contents = "0,0"
                            pickle.dump(file_contents,file)

                    file_contents = file_contents.split(",")
                    players_num += 1
                    player_list.append(nick)
                    players_pos.append((int(file_contents[0]),int(file_contents[1])))

                    reply[0].append("{0};{1};{2}".format(player, int(file_contents[0]), int(file_contents[1]))) # client_id; pos
                log("{0} from {1}".format(data[0], addr),0)
            players_pos[player] = data[1].split(",")[0], data[1].split(",")[1]

            reply.append(player_list)
            reply.append(players_pos)
            if data[2] != "None":
                if int(data[2]) != current_lvl:
                    log("Started uploading map file for {0}".format(addr),0)
                    reply2 = reply
                    log("reply2: {0}".format(reply2),0)
                    reply2.append("REQUEST_DOWNLOAD-MAP")
                    log("reply: {0}".format(reply),0)
                    log("reply2: {0}".format(reply2),0)
                    conn.sendall(str.encode(str(reply2)))
                    f = open(path.join(lvl_dir,'level{0}.lvl'.format(current_lvl)),"rb")
                    l = f.read(2048)
                    while l:
                        data = conn.recv(2048).decode()
                        if data == "1":
                            conn.sendall(l)
                            l = f.read(2048)
                        if not l:
                            break
                    conn.sendall(b"done")
                    log("Finished uploading map file for {0}".format(addr),0)
                    conn.recv(2048).decode()
                    reply[3] = str(current_lvl)
                    conn.sendall(str.encode(str(reply)))
                else:
                    reply.append("")
                    conn.sendall(str.encode(str(reply)))
            else:
                reply.append("")
                conn.sendall(str.encode(str(reply)))
        except Exception as e:
            log("Something went wrong...",2)
            log(e,2)
            break

    conn.close()
    log("{0}, disconnected".format(addr),0)

start_new_thread(Game_loop, (None,None))

currentPlayer = 0
while True:
    conn, addr = s.accept()
    log('connection from: '+ str(addr),0)
    start_new_thread(client, (conn, addr, currentPlayer))
    currentPlayer += 1