if __name__ == '__main__':        
    x = int(input())
    y = int(input())
    z = int(input())
    n = int(input())

    firstNumbers = [x, y, z]
    
    list = []
    div = (x + y + z) / 3

    def class_calc():
        for x in range(0, n+1):
            for y in range(0, n+1):
                for z in range(0, n+1):
                    a = [x,y,z]
                    if x + y + z == n:
                        continue
                    list.append(a)

    if div == 1:
        for x in range(0, n):
            for y in range(0, n):
                for z in range(0, n):
                    a = [x,y,z]
                    if x + y + z == n:
                        continue
                    list.append(a)

    elif div != 1 and n != 2 and n:
            for x in range(0, n+1):
                for y in range(0, n+1):
                    for z in range(0, n+1):
                        a = [x,y,z]
                        if x + y + z == n or y == n:
                            continue
                        list.append(a)

    elif div != 1 and n == 2:
            for x in range(0, n+1):
                for y in range(0, n+1):
                    for z in range(0, n+1):
                        a = [x,y,z]
                        if x + y + z == n:
                            continue
                        list.append(a)

                        
try:
    index = int(list.index(firstNumbers))
    index+=1
    print(list[0:index])
except:
    print(list)