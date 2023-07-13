# bit masks for float16, float32 and float64
import numpy as np

import sys

def get_sigexp_bitmask(t=np.float32):
    """Get the bitmask for the sign bit and exponent for different datatypes.

    Args:
        t (numpy dtype): type of array to get sign and exponent bitmask for

    Returns:
        int16|int32|int64: the bitmask for the sign and exponent, other bits are
        zero.
    """
    # construct the bitmasks as though little endian, do a byteswap at the
    # end if big endian
    # Code used to generate masks (for float64):
    #   mask = np.uint64(0)
    #   for x in range(52,64):
    #       mask = mask | np.uint64(1 << x)

    if (t in [np.float16, "<f2", ">f2"]):
        # float16 has 1 sign bit, 5 bit exponent, 10 bit mantissa, so bits
        # 10 to 15 are masked to 1, 0 to 9 are masked to 0
        mask = np.uint16(0xFC00)
    elif (t in [np.float32, "<f4", ">f4"]):
        # float32 has 1 sign bit, 8 bit exponent, 23 bit mantissa, so bits
        # 23 to 31 are masked to 1, 0 to 22 are masked to 0
        mask = np.uint32(0xFF800000)
    elif (t in [np.float64, "<f8", ">f8"]):
        # float64 has 1 sign bit, 11 bit exponent, 52 bit mantissa, so bits
        # 52 to 63 are masked to 1, 0 to 51 are masked to 0
        mask = np.uint64(0xFFF0000000000000)
    else:
        raise TypeError("Unsupported type for get_bitmask : {}".format(t))

    # do a byteswap if neccessary
    if t.byteorder == '>':
        # data type is big endian
        mask = mask.byteswap()
    elif t.byteorder == '=' and sys.byteorder == 'big':
        # system is a big endian
        mask = mask.byteswap()
    return mask


def get_man_bitmask(t=np.float32, NSB=64):
    """Get the bitmask for the mantissa that is truncated after the NSB

    Args:
        t (numpy dtype): type of array to get mantissa bitmask for
        NSB (int)) : number of significant bits to retain in the mantissa

    Returns:
        int16|int32|int64: the bitmask for the sign and exponent, other bits are
        zero.
    """
    # construct the bit mask for the mantissa
    if (t in [np.float16, "<f2", ">f2"]):
        # bits 0 to 9 are the mantissa
        # float16 has 1 sign bit, 5 bit exponent, 10 bit mantissa, so bits
        # 10 to 15 are masked to 1, 0 to 9 are masked to 0
        if NSB > 10:
            NSB = 10
        mask = np.uint16(0)
        for x in range(0+(10-NSB), 10):
            bit = np.left_shift([np.uint16(1)], x)
            mask |= bit[0]

    elif (t in [np.float32, "<f4", ">f4"]):
        # float32 has 1 sign bit, 8 bit exponent, 23 bit mantissa, so bits
        # 23 to 31 are masked to 1, 0 to 22 are masked to 0
        if NSB > 23:
            NSB = 23
        mask = np.uint32(0)
        for x in range(0+(23-NSB), 23):
            bit = np.left_shift([np.uint32(1)], x)
            mask |= bit[0]

    elif (t in [np.float64, "<f8", ">f8"]):
        # float64 has 1 sign bit, 11 bit exponent, 52 bit mantissa, so bits
        # 52 to 63 are masked to 1, 0 to 51 are masked to 0
        if NSB > 52:
            NSB = 52
        mask = np.uint64(0)
        for x in range(0+(52-NSB), 52):
            bit = np.left_shift([np.uint64(1)], x)
            mask |= bit[0]

    # do a byteswap if neccessary
    if t.byteorder == '>':
        # data type is big endian
        mask = mask.byteswap()
    elif t.byteorder == '=' and sys.byteorder == 'big':
        # system is a big endian
        mask = mask.byteswap()
    return mask


def get_bitgroom_bitmask(t=np.float32):
    """Get the bitmask for bitgrooming.  This is then logical or-ed with the
    get_man_bitmask.  The bitgrooming bitmasks can be defined as just constants
    of alternate zeros then ones for the length of the mantissa for the
    different types.

    Args:
        t (numpy dtype): type of array to get bitgroom bitmask for

    Returns:
        int16|int32|int64: the bitmask for the bitgrooming, other bits are zero.
    """
    # construct the bitmasks as though little endian, do a byteswap at the
    # end if big endian

    # Code used to generate masks (for float64):
    # mask = np.uint64(0)
    # bit = 0
    # for x in range(0, 52):
    #     mask = mask | np.uint64(bit << x)
    #     bit = 1-bit

    if (t in [np.float16, "<f2", ">f2"]):
        # float16 has 1 sign bit, 5 bit exponent, 10 bit mantissa, so bits
        # 10 to 15 are masked to 1, 0 to 9 are masked to 0
        mask = np.uint16(0xAAAA)
    elif (t in [np.float32, "<f4", ">f4"]):
        # float32 has 1 sign bit, 8 bit exponent, 23 bit mantissa, so bits
        # 23 to 31 are masked to 1, 0 to 22 are masked to 0
        mask = np.uint32(0xAAAAAAAA)
    elif (t in [np.float64, "<f8", ">f8"]):
        # float64 has 1 sign bit, 11 bit exponent, 52 bit mantissa, so bits
        # 52 to 63 are masked to 1, 0 to 51 are masked to 0
        mask = np.uint64(0xAAAAAAAAAAAAAAAA)
    else:
        raise TypeError("Unsupported type for get_bitmask : {}".format(t))

    # do a byteswap if neccessary
    if t.byteorder == '>':
        # data type is big endian
        mask = mask.byteswap()
    elif t.byteorder == '=' and sys.byteorder == 'big':
        # system is a big endian
        mask = mask.byteswap()
    return mask
