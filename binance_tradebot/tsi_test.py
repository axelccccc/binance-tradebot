import indicators

close_values = [
    24, 29, 21, 19, 16, 22, 31, 27, 25, 23,
    21, 20, 19, 22, 21, 25, 31, 34, 37, 35
]

close_values = [
    21.21, 21.34, 21.58, 21.51, 21.43, 21.42, 
    21.39, 21.36, 21.40, 21.42, 21.31, 21.28, 
    21.26, 21.24, 21.29, 21.28, 21.30, 21.31, 
    21.34, 21.41, 21.42, 21.40, 21.47, 21.51
]

tsi = indicators.TSI(5, 10, 1, _movav=indicators.SMA)

x = []

for i in range(14, -1, -1):
    if i != 0:
        x.append(tsi.next(close_values[0:-i]))
    else:
        x.append(tsi.next(close_values))

print([float('%.2f' % a) for a in x])

#print(close_values[0:-7])