import numpy as np

from ceda_icompress.BitManipulation.bitmasks import (
    get_sigexp_bitmask
)
from ceda_icompress.BitManipulation.bitmanip import (
    BitManipulation, BitManipulationError
)
from ceda_icompress.InfoMeasures.keepbits import free_entropy, binom_confidence

class BitMask(BitManipulation):
    """Reduce the information content in an array by rounding down (quantising)
    each element in the array.  The quantisation is acheived by setting bits to
    zero if they have zero bit information from the bitinformation analysis.

    Code inspired by https://github.com/esowc/Elefridge.jl

    Args:
        A (numpy array): array to quantise by rounding down bits.
                         array should be float16, float32 or float64
        bit (numpy array): the bit information from the analysis

    Returns:
        numpy array: the quantised array
    """
    def __init__(self, A, NSB=None, analysis=None, ci=None):
        """Initialise the BitMask by deriving the bitmask from the inputs
        Args:
            A (numpy array)  : the array that is to be processed 
            NSB (int)        : override the number of bits, if the user has 
                               requested
            analysis (numpy array) : result of cic_analyse
            ci (float)       : confidence interval, e.g. 0.99
        Side effects:
            self.mask (int)       : the mask
            self.groom_mask (int) : the secondary mask
        """
        super().__init__(A, NSB, analysis, ci)
        # check we have the analysis data!
        if not "bitinfo" in analysis:
            raise BitManipulationError(
                "No bitinfo key in analysis data"
            )
        # get the information
        bi = np.array(analysis["bitinfo"])
        # get the location of the mantissa bits
        if not "manbit" in analysis:
            raise BitManipulationError(
                "No manbit key in analysis data"
            )
        manbit = analysis["manbit"]
        # get the number of elements
        if not "elements" in analysis:
            raise BitManipulationError(
                "No elements key in analysis data"
            )
        elements = int(analysis["elements"])
        # see the keepbits function in Infomeasures.keepbits for more info
        threshold = binom_confidence(elements, ci) - 0.5
        # build the mask
        self.mask = 0
        self.NSB = 0
        for i in range(manbit[0], manbit[1]):
            if bi[i] > threshold:           # significantly different to zero
                self.mask |= (0b1 << i)
                self.NSB += 1
        # add the sign and exponent mask
        bit_mask = get_sigexp_bitmask(A.dtype)
        self.mask |= bit_mask
        self.method = "bitmask"

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