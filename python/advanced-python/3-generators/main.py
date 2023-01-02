from telnetlib import theNULL


def infinite_sequence():
    result = 1
    while True:
        yield result
        result *= 5
values = infinite_sequence()



#meu incremento
for i in range(1, 10):
    print("Sou o I: %d" % i)
    print(next(values))

# print(next(values))
# print(next(values))
# print(next(values))
