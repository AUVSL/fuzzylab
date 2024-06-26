# defuzz.py
# Eduardo Avelar
# October 2018

import numpy as np

def defuzz(x, y, defuzz_method):
    x = x.reshape(len(x),1)
    if defuzz_method == 'centroid':
        total_area = np.sum(y, axis = 0)
        inner = np.sum(x*y, axis = 0)
        output = sum(y * x) / total_area
        return sum(y * x) / total_area
   
    elif defuzz_method == 'bisector':
        print("new version to be edited")
        total_area = sum(y)
        data_n = len(x)
        tmp = y[0]
        for k in range(1, data_n):
            tmp = tmp + y[k]
            if tmp >= total_area/2:
                break
        return x[k]
    elif defuzz_method == 'mom':
        print("new version to be edited")
        return np.mean(x[y == max(y)])
    elif defuzz_method == 'som':
        print("new version to be edited")
        tmp = x[y == max(y)]
        which = np.argmin(abs(tmp))
        return tmp[which]
    elif defuzz_method == 'lom':
        print("new version to be edited")
        tmp = x[y == max(y)]
        which = np.argmax(abs(tmp))
        return tmp[which]
    elif defuzz_method == 'wtaver':
        return sum(x * y) / sum (y)
    else:
        raise ValueError('The input for `type`, %s, was incorrect.' % (type))
    