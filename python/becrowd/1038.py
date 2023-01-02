a, b = map(int, input().split())
listPrices = [0, 4.00, 4.50, 5.00, 2.00, 1.50]

total = (listPrices[a] * b)
print("Total: R$ %0.2f" % total)

