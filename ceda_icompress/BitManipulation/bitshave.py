import numpy as np

from ceda_icompress.BitManipulation.bitmasks import (
    get_sigexp_bitmask, get_man_bitmask
)
from ceda_icompress.BitManipulation.bitmanip import BitManipulation

class BitShave(BitManipulation):
    """Reduce the information content in an array by rounding down 
    (quantising) each element in the array.  The quantisation is acheived by
    setting bits to zero after the NSB bit.  (NSB = number of significant 
    bits)

    Code inspired by https://github.com/esowc/Elefridge.jl"""

    def __init__(self, A, NSB=None, analysis=None, ci=None):
        """Initialise the BitShave by deriving the bitmask from the inputs
        Args:
            A (numpy array)  : the array that is to be processed 
            NSB (int)        : override the number of bits, if the user has 
                               requested
            analysis (dict)  : result of cic_analyse
            ci (float)       : confidence interval, e.g. 0.99
        Side effects:
            self.mask (int)   : the mask
        """
        super().__init__(A, NSB, analysis, ci)
        # get the number of significant bits
        self.get_NSB(NSB, analysis, ci)
        # get the bit mask for the sign bit and exponent for the data type
        bit_mask = get_sigexp_bitmask(A.dtype)
        # get the bit mask for the mantissa
        man_mask = get_man_bitmask(A.dtype, self.NSB)
        self.mask = bit_mask | man_mask
        self.method = "bitshave"

    def process(self, A):
        """
        Args:
            A (numpy array): array to quantise by rounding down bits.
                            array should be float16, float32 or float64
        Returns:
            numpy array: the quantised array
        """
        # get a view of the array as the uint
        Av = A.view(dtype=self.t_uint)
        # do the bitwise and between the mask and the uint array
        Ar = np.ma.bitwise_and(Av, self.mask)
        # convert back to the original type
        Ar = Ar.view(dtype=A.dtype)
        return Ar