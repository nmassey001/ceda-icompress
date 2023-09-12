import numpy as np

from ceda_icompress.BitManipulation.bitmasks import (
    get_sigexp_bitmask, get_man_bitmask, get_bitgroom_bitmask
)
from ceda_icompress.BitManipulation.bitmanip import BitManipulation

class BitGroom(BitManipulation):
    """Reduce the information content in an array by quantising each element in
    the array.  The quantisation is acheived by setting bits to alternate zeros
    and ones after the NSB bit.  (NSB = number of significant bits).
    This is known as bit grooming.
    One exception is not to do any bit grooming on the exact representation of
    zero.

    Code inspired by https://github.com/esowc/Elefridge.jl
    See also https://gmd.copernicus.org/articles/9/3199/2016/gmd-9-3199-2016.pdf    

    """

    def __init__(self, A, NSB=None, analysis=None, ci=None):
        """Initialise the BitGroom by deriving the bitmask from the inputs
        Args:
            A (numpy array)  : the array that is to be processed 
            NSB (int)        : override the number of bits, if the user has 
                               requested
            analysis (dict)  : result of result of cic_analyse
            ci (float)       : confidence interval, e.g. 0.99
        Side effects:
            self.mask (int)       : the mask
            self.groom_mask (int) : the secondary mask
        """
        super().__init__(A, NSB, analysis, ci)
        self.get_NSB(NSB, analysis, ci)
        bit_mask = get_sigexp_bitmask(A.dtype)
        # get the bit mask for the mantissa
        man_mask = get_man_bitmask(A.dtype, self.NSB)
        # construct the main mask
        self.mask = bit_mask | man_mask
        # the groom mask is the alternating 0s and 1s AND-ed with the logical not
        # of the above mask
        self.groom_mask = get_bitgroom_bitmask(A.dtype) & ~self.mask

    def process(self, A):
        """
        Args:
            A (numpy array): array to quantise by groomig bits.
                            array should be float16, float32 or float64
            NSB (int)      : number of significant bits.  Set all bits to alternate
                            zeros then ones after this bit.

        Returns:
            numpy array: the quantised array
        """
        # get a view of the array as the uint
        Av = A.view(dtype=self.t_uint)

        # for bitgroom, we logical AND the same mask as bitshave (set all to zero)
        # then we logical OR with the groom mask
        Ar = np.ma.bitwise_and(Av, self.mask)
        Ar = np.ma.bitwise_or(Ar, self.groom_mask)

        # convert back to the original type
        Ar = Ar.view(dtype=A.dtype)
        return Ar