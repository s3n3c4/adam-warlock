a, b, c, d = input().split()

if (b > c and d > a) and ((int(c) + int(d)) > (int(a) + int(b))) and (int(a) or int(b) >= 0) and (int(a) % 2 == 0):
    print("Valores aceitos")
else:
    print("Valores nao aceitos")

