import numpy as np
from ceda_icompress.InfoMeasures.whichUint import whichUint, whichint
from ceda_icompress.BitManipulation.bitmasks import (
    get_man_bitmask, get_sig_bitmask, get_exp_bitmask)
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp

def exponent_bias(t=np.float32):
    """Get the bias for the exponent in the IEEE floating point representation
    Args:
        T (numpy dtype): data type to get exponent bias for 
    Returns:
        int: the bias (2**(exponent bits-1)-1)
    """
    if (t in [np.float16, "<f2", ">f2"]):
        # half precision - 5 bit exponent
        return 15
    elif (t in [np.float32, "<f4", ">f4"]):
        # full precision - 8 bit exponent
        return 127
    elif (t in [np.float64, "<f8", ">f8"]):
        # double precision - 11 bit exponent
        return 1023


def signed_exponent(A):
    """Convert an array of floating point numbers in A from having a biased
       exponent, into having a signed exponent.
    Args:
        A (numpy array): array to convert
    Returns:
        numpy array: the converted array    
    """

    # get the type of the array when converted to a Uint and int
    t_uint = whichUint(A.dtype)
    t_int = whichint(A.dtype)

    # get the sign and exponent bit masks
    smask = get_sig_bitmask(A.dtype)
    emask = get_exp_bitmask(A.dtype)
    mmask = get_man_bitmask(A.dtype)
    _, man, _ = getsigmanexp(A.dtype)

    # sign and mantissa mask
    smmask = smask | mmask
    # exponent sign mask
    esigmask = smask >> 1
    # exponent bias
    bias = exponent_bias(A.dtype)
    # number of mantissa bits
    mbits = man[1] - man[0]

    # do the conversion
    Av = A.view(dtype=t_uint)
    sm = np.ma.bitwise_and(Av, smmask)
    e0 = np.ma.right_shift(np.ma.bitwise_and(Av, emask), mbits)
    e1 = e0.astype(t_int) - bias

    max_eabs = np.iinfo(t_uint).max >> mbits
    eabs = np.ma.mod(np.abs(e1), max_eabs + 1)
    esign = np.ma.where(e1 < 0, esigmask, 0)
    esigned = np.ma.bitwise_or(esign, np.ma.left_shift(eabs, mbits))
    B = np.ma.bitwise_or(sm, esigned).astype(t_uint)
    return B
