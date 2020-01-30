from datetime import datetime
import colorama
import socket

colorama.init()

port = 8000
server_ip = "25.96.204.7"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("sztynks"+str(socket.gethostbyaddr(server_ip)))
try:
    s.bind((server_ip, port))
    print("Server address: "+ str(server_ip) + ":" + str(port))
except socket.error as e:
    str(e)

def log(message):
    print("["+ colorama.Fore.GREEN + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + message)

s.listen(2)
log("server started, waiting for connections...")

while True:
    conn, addr = s.accept()
    log('connection from: '+ str(addr))
    conn.close()
    break

log("Test ended with positive result!")
input("press any key to exit...")
