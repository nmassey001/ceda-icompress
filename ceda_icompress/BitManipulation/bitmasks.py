# bit masks for float16, float32 and float64
import numpy as np

import sys

def get_sig_bitmask(t=np.float32):
    """Get the bitmask for the sign bit for different datatypes.

    Args:
        t (numpy dtype): type of array to get sign bitmask for

    Returns:
        int16|int32|int64: the bitmask for the sign, other bits are
        zero.
    """
    if (t in [np.float16, "<f2", ">f2"]):
        # float16 has 1 sign bit, 5 bit exponent, 10 bit mantissa, so bit
        # 15 is masked to 1, 0 to 14 are masked to 0
        mask = np.uint16(0x8000)
    elif (t in [np.float32, "<f4", ">f4"]):
        # float32 has 1 sign bit, 8 bit exponent, 23 bit mantissa, so bit
        # 31 is masked to 1, 0 to 30 are masked to 0
        mask = np.uint32(0x80000000)
    elif (t in [np.float64, "<f8", ">f8"]):
        # float64 has 1 sign bit, 11 bit exponent, 52 bit mantissa, so bit
        # 63 is masked to 1, 0 to 62 are masked to 0
        mask = np.uint64(0x8000000000000000)
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

def get_exp_bitmask(t=np.float32):
    """Get the bitmask for the exponent bit for different datatypes.

    Args:
        t (numpy dtype): type of array to get exponent bitmask for

    Returns:
        int16|int32|int64: the bitmask for the exponent, other bits are
        zero.
    """
    if (t in [np.float16, "<f2", ">f2"]):
        # float16 has 1 sign bit, 5 bit exponent, 10 bit mantissa, so bits
        # 10 to 14 are masked to 1, 0 to 9 are masked to 0, as is bit 15
        mask = np.uint16(0x7C00)
    elif (t in [np.float32, "<f4", ">f4"]):
        # float32 has 1 sign bit, 8 bit exponent, 23 bit mantissa, so bits
        # 23 to 30 are masked to 1, 0 to 22 are masked to 0, as is bit 31
        mask = np.uint32(0x7F800000)
    elif (t in [np.float64, "<f8", ">f8"]):
        # float64 has 1 sign bit, 11 bit exponent, 52 bit mantissa, so bits
        # 52 to 62 are masked to 1, 0 to 51 are masked to 0, as is bit 63
        mask = np.uint64(0x7FF0000000000000)
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

def get_sigexp_bitmask(t=np.float32):
    """Get the bitmask for the sign bit and exponent for different datatypes.

    Args:
        t (numpy dtype): type of array to get sign and exponent bitmask for

    Returns:
        int16|int32|int64: the bitmask for the sign and exponent, other bits are
        zero.
    """
    # mask here is just the sign and exponent masks ORed together
    mask = get_sig_bitmask(t) | get_man_bitmask(t)
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
