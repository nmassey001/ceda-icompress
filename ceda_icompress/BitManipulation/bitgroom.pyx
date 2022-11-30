import numpy as np
cimport numpy as np

from ceda_icompress.InfoMeasures.whichUint import whichUint
from bitmasks import get_sigexp_bitmask, get_man_bitmask, get_bitgroom_bitmask

cpdef bitgroom(np.ndarray A, int NSB):
    """Reduce the information content in an array by quantising each element in
    the array.  The quantisation is acheived by setting bits to alternate zeros
    and ones after the NSB bit.  (NSB = number of significant bits).
    This is known as bit grooming.
    One exception is not to do any bit grooming on the exact representation of
    zero.

    Code inspired by https://github.com/esowc/Elefridge.jl
    See also https://gmd.copernicus.org/articles/9/3199/2016/gmd-9-3199-2016.pdf

    Args:
        A (numpy array): array to quantise by groomig bits.
                         array should be float16, float32 or float64
        NSB (int)      : number of significant bits.  Set all bits to alternate
                         zeros then ones after this bit.

    Returns:
        numpy array: the quantised array
    """

    # type declarations
    cdef np.ndarray Av
    cdef np.ndarray Ar
    cdef int n_bits
    cdef int x              # loop counter

    # check that the type is compatible, either a float16, float32 or float64
    if not (A.dtype in [np.float16, "<f2", ">f2",
                        np.float32, "<f4", ">f4",
                        np.float64, "<f8", ">f8"]):
        raise TypeError("Unsupported type for bitgroom : {}".format(
                            A.dtype
                        ))

    # get the type of the array when converted to a UInt
    t_uint = whichUint(A.dtype)
    # get the bit mask for the sign bit and exponent for the data type
    bit_mask = get_sigexp_bitmask(A.dtype)
    # get the bit mask for the mantissa
    man_mask = get_man_bitmask(A.dtype, NSB)
    # construct the main mask
    mask = bit_mask | man_mask

    # the groom mask is the alternating 0s and 1s AND-ed with the logical not
    # of the above mask
    groom_mask = get_bitgroom_bitmask(A.dtype) & ~mask

    # get a view of the array as the uint
    Av = A.view(dtype=t_uint)

    # for bitgroom, we logical AND the same mask as bitshave (set all to zero)
    # then we logical OR with the groom mask
    Ar = np.bitwise_and(Av, mask)
    Ar = np.bitwise_or(Ar, groom_mask)

    ### REMEMBER TO MASK OFF THE ZEROS! ###
    # convert back to the original type
    Ar = Ar.view(dtype=A.dtype)
    return Ar
