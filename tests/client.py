from datetime import datetime
import colorama
import socket

colorama.init()

class Network():
    def __init__(self, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = port 
        self.addr = (self.server, self.port)

    def connect(self):
        self.client.connect(self.addr)
        data = self.client.recv(6144*9).decode()
        return data

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048*9).decode()
        except socket.error as e:
            print(e)

print("--- Client side test ---")
server_addres = input("Enter the server ip: ")

ip = "127.0.0.1"
port = 8000

try:
    ip, port = server_addres.split(":")
    port = int(port)
except Exception as e:
    print("["+ colorama.Fore.RED + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + "Cos poszlo nie tak...")
    print("["+ colorama.Fore.RED + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + str(e))

n = Network(ip, port)

try:
    n.connect()
    print("["+ colorama.Fore.GREEN + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + "Połączono z hostem na "+ str(ip) + ":" + str(port) + ", test zakończony pomyślnie.")
except Exception as e: 
    print("["+ colorama.Fore.RED + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + "Cos poszlo nie tak...")
    print("["+ colorama.Fore.RED + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + str(e))

input("Naciśnij klawisz aby wyjsć...")
