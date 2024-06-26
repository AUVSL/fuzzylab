# trimf.py
# Eduardo Avelar
# October 2018

import numpy as np

def trimf(x, params):
    """
    Triangular membership function generator.

    Parameters
    ----------
    x : 1d array
        Independent variable.
    params : 1d array, length 3
        Three-element vector controlling shape of triangular function.
        Requires a <= b <= c.

    Returns
    -------
    y : 1d array
        Triangular membership function.
    """
    assert len(params) == 3, 'Triangular membership function must have three parameters.'

    a, b, c = np.asarray(params)
    assert a <= b, 'First parameter must be less than or equal to second parameter.'
    assert b <= c, 'Second parameter must be less than or equal to third parameter.'

    if type(x) is not np.ndarray:
        x = np.asarray([x])

    #y = np.zeros(len(x))
    y = np.zeros_like(x) #add 20240624
  
    # Left slope
    if a != b:
        maskleft = (a < x) & (x < b) #add 20240624
        #index = np.logical_and(a < x, x < b)
        y[maskleft] = (x[maskleft] - a) / (b - a) #add 20240624
        #y[index] = (x[index] - a) / (b - a)

    # Right slope
    if b != c:    
        maskright = (b < x) & (x < c) #add 20240624
        #index = np.logical_and(b < x, x < c)      
        y[maskright] = (c - x[maskright]) / (c - b) #add 20240624
        #y[index] = (c - x[index]) / (c - b)

    # Center
    #y[x == b] = 1
    maskcenter = (x == b) #add 20240624
    y[maskcenter] = 1 #add 20240624
    
    return y
