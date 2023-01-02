import math

variavelFloat = float(input())


if (variavelFloat >= 0 and variavelFloat <= 25.0000):
    print("Intervalo [0,25]")
elif (variavelFloat >= 25.00001 and variavelFloat <= 50.0000000):
    print("Intervalo (25,50]")
elif (variavelFloat >= 50.0000001 and variavelFloat <= 75.0000000):
    print("Intervalo (50,75]")
elif (variavelFloat >=75.0000001 and variavelFloat <= 100.0000000):
    print("Intervalo (75,100]")
else:
    print("Fora de intervalo")
    
