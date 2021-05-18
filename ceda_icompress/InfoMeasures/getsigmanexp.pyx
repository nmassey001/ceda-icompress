import sys

import numpy as np
cimport numpy as np

def getbord(np.ndarray A):
    """Get the byte order for array A.

    Inputs:
        A (numpy array): array to get the byte order for.

    Returns:
        string: the byte order either >, <, = or |

    """
    # get the byte order from the array
    endian_map = {
        '>': 'big',
        '<': 'little',
        '=': sys.byteorder,
        '|': 'not applicable',
    }
    bord = endian_map[A.dtype.byteorder]
    return bord


def getsigmanexp(np.ndarray A):
    """Get the positions of the sign bit, exponent and mantissa in the
    bitstring of the dtype of the array A.

    Inputs:
        A (numpy array): array to get the sign / mantissa / exponent positions
        for.

    Returns:
        tuple: the positions of the sign, mantissa and exponent (in that order)
    """
    bord = getbord(A)
    # get the type and size (in bits)
    typed = A.dtype.kind
    sized = A.dtype.itemsize * 8
    # man (start, end)
    # exp (start, end)
    # sig pos
    if typed == "i":
        # signed int
        if bord == 'big':
            sig = 0
            man = (1,sized)
            exp = (-1,-1)
        elif bord == 'little':
            sig = sized-1
            man = (0, sized-1)
            exp = (-1,-1)
    elif typed == "u":
        # unsigned int
        sig = -1
        man = (0, sized)
        exp = (-1,-1)
    elif typed == "f":
        # floating point
        sig = 0
        if sized == 16:             # half precision
            exp = (1,6)
            man = (6,16)
        elif sized == 32:           # single precision
            exp = (1,9)
            man = (9,32)
        elif sized == 64:           # double precision
            exp = (1,12)
            man = (12,64)
        if bord == 'little':
            # like the above, but backwards
            sig = sized-1
            man = (sized-man[1], sized-man[0])
            exp = (sized-exp[1], sized-exp[0])
    else:
        raise TypeError("Unsupported type: {}".format(typed))
    return (sig, man, exp)
