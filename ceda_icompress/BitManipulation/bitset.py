import numpy as np

from ceda_icompress.InfoMeasures.whichUint import whichUint
from ceda_icompress.BitManipulation.bitmasks import (
    get_sigexp_bitmask, get_man_bitmask
)

def bitset(A, NSB):
    """Reduce the information content in an array by rounding up (quantising)
    each element in the array.  The quantisation is acheived by setting bits to
    one after the NSB bit.  (NSB = number of significant bits)

    Code inspired by https://github.com/esowc/Elefridge.jl

    Args:
        A (numpy array): array to quantise by rounding up bits.
                         array should be float16, float32 or float64
        NSB (int)      : number of significant bits.  Set all bits to one
                         after this bit

    Returns:
        numpy array: the quantised array
    """
    # check that the type is compatible, either a float16, float32 or float64
    if not (A.dtype in [np.float16, "<f2", ">f2",
                        np.float32, "<f4", ">f4",
                        np.float64, "<f8", ">f8"]):
        raise TypeError("Unsupported type for bitset : {}".format(
                            A.dtype
                        ))

    # get the type of the array when converted to a UInt
    t_uint = whichUint(A.dtype)
    # get the bit mask for the sign bit and exponent for the data type
    bit_mask = get_sigexp_bitmask(A.dtype)
    # get the bit mask for the mantissa
    man_mask = get_man_bitmask(A.dtype, NSB)
    # for bitset, the mask is the bitwise logical not of the mask for
    # the bit shave
    mask = ~(bit_mask | man_mask)
    # get a view of the array as the uint
    Av = A.view(dtype=t_uint)
    # for bitset the mask is logical or-ed with the array
    # do the bitwise or between the mask and the uint array
    Ar = np.ma.bitwise_or(Av, mask)
    # convert back to the original type
    Ar = Ar.view(dtype=A.dtype)
    return Ar
