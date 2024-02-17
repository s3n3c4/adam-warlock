if __name__ == '__main__':        
    x = int(input())
    y = int(input())
    z = int(input())
    n = int(input())

    firstNumbers = [x, y, z]
    
    list = []

    def class_calc():
        for j in range(0, x+1):
            for k in range(0, y+1):
                for l in range(0, z+1):
                    a = [j,k,l]
                    if j + k + l == n:
                        continue
                    list.append(a)

    class_calc()

                        
try:
    index = int(list.index(firstNumbers))
    index+=1
    print(list[0:index])
except:
    print(list)