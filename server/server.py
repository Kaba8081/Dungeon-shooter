from datetime import datetime
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

def client(conn, addr, player):
    global player_list, players_num, players_pos
    nick = 'Unnamed'
    conn.send(str.encode('1'))

    while True:
        try:
            data = conn.recv(2048).decode() # request; position
            data = data.split(";")
            reply = [[]]                    # [request, player_list, positions, chat]

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

            print("data: {0}".format(data))
            players_pos[player] = int(data[1].split(",")[0]), int(data[1].split(",")[1])

            reply.append(player_list)
            reply.append(players_pos)

            conn.sendall(str.encode(str(reply)))
        except Exception as e:
            log("Something went wrong...",2)
            log(e,2)
            break

    conn.close()
    log("{0}, disconnected".format(addr),0)

currentPlayer = 0
while True:
    conn, addr = s.accept()
    log('connection from: '+ str(addr),0)
    start_new_thread(client, (conn, addr, currentPlayer))
    currentPlayer += 1