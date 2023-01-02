from decimal import DivisionByZero
import math

try:
    a, b, c = map(float, input().split())

    Delta = (b*b - (4 * a * c)) 

    bhasKaraPositivo = (- b + math.sqrt(Delta)) / (2*a)
    bhasKaraNegativo = (- b - math.sqrt(Delta)) / (2*a)
    print("R1 = %.5f" % bhasKaraPositivo)
    print("R2 = %.5f" % bhasKaraNegativo)
except (ZeroDivisionError, ValueError) as error:
        print("Impossivel calcular")



    


        







