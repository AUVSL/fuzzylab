# trapmf.py
# Eduardo Avelar
# October 2018

import numpy as np

def trapmf(x, params):
    # x shape = (number of pixels, 1)
    """
    Trapezoidal membership function generator.

    Parameters
    ----------
    x : 1d array
        Independent variable.
    params : 1d array, length 4
        Four-element vector.  Ensure a <= b <= c <= d.

    Returns
    -------
    y : 1d array
        Trapezoidal membership function.
    """
    assert len(params) == 4, 'Trapezoidal membership function must have four parameters.'
    
    a, b, c, d = np.asarray(params)
    assert a <= b, 'First parameter must be less than or equal to second parameter.'
    assert b <= c, 'Second parameter must be less than or equal to third parameter.'
    assert c <= d, 'Third parameter must be less than or equal to fourth parameter.'

    if type(x) is not np.ndarray:
        x = np.asarray([x])

    #y = np.zeros(len(x))
    y = np.zeros_like(x) #add 20240624

    # Left slope
    if a != b:
        maskleft = (a < x) & (x < b) #add 20240624
        #index = np.logical_and(a < x, x < b)
        y[maskleft] = (x[maskleft]-a)/(b-a) #add 20240624
        #y[index] = (x[index] - a) / (b - a)
        
    # Right slope
    if c != d:
        maskright = (c < x) & (x < d)    #add 20240624
        #index = np.logical_and(c < x, x < d)            
        y[maskright] = (d-x[maskright]) / (d - c)  #add 20240624
        #y[index] = (d - x[index]) / (d - c)

    # Top
    #index = np.logical_and(b <= x, x <= c)           
    #y[index] = 1
    maskmid = (b <=x) & (x<=c)  #add 20240624
    y[maskmid] = 1  #add 20240624

    return y