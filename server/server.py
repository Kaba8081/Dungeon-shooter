from datetime import datetime
from _thread import *
from os import path
import colorama
import socket

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server_ip, port))
except Exception as e:
    log("Something went wrong...",2)
    log(e,2)

s.listen(player_limit)
log("Server started waiting for connections...",0)

def client(conn, addr, player):
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
                log("{0} from {1}".format(data[0], addr),0)

                conn.sendall(str.encode(str(reply)))
        except Exception as e:
            log("Something went wrong...",2)
            log(e,2)

    conn.close()

currentPlayer = 1
while True:
    conn, addr = s.accept()
    log('connection from: '+ str(addr),0)
    start_new_thread(client, (conn, addr, currentPlayer))
    currentPlayer += 1