import os



for hostLoop in range(0,255):
    host = '192.168.2.' + str(hostLoop)
    response = os.system("ping -c 1 " + host)

    if response == 256:
        continue
    else:
        print("host is up")
