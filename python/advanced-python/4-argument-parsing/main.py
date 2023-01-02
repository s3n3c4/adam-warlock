# def myfunction(*args, **kwargs):
#     print(args[0])
#     print(args[1])
#     print(args[2])
#     print(args[3])
#     print(kwargs['KEYONE'])
#     print(kwargs['KEYTWO'])

# myfunction('Hey', True, 19, 'wow', KEYONE="TESTE", KEYTWO=7)

from colorsys import rgb_to_hls
import sys
import getopt

filename = "texto.txt"
message = "Hello"

opts, args = getopt.getopt(sys.argv[1:], "f:m:", ['filename', 'message'])

for opt, arg in opts:
    if opt == '-f':
        filename = arg
    if opt == '-m':
        message = arg

with open(filename, 'w+') as f:
    f.write(message)
