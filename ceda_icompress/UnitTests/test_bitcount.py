import unittest
import numpy as np

from ceda_icompress.InfoMeasures.bitcount import bitcount, bitpaircount
from test_types import get_test_types

DIM_LEN = 128

class bitcountTest(unittest.TestCase):
    """Test the bitcount function with known answers."""
    def test_ones_float32(self):
        # generate a load of ones
        # one has the 32 bit IEEE floating point representation as:
        # 0    01111111     00000000000000000000000
        # Sign Exponent     Mantissa
        zdist = np.ones(
            shape = (DIM_LEN,),
            dtype = np.float32,
        )
        # calculate the bitcounts
        C = bitcount(zdist)
        assert(C[30] == 0)
        assert(C[31] == 0)
        # positions 23 -> 29 == DIM_LEN
        assert((C[23:30] == DIM_LEN).all())
        assert((C[:23] == 0).all())
        # That is the 32 bit floating point representation of 1!

    def test_zeros(self):
        # generate a load of zeros
        for typ in get_test_types():
            zdist = np.zeros(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the bitcounts
            C = bitcount(zdist)
            assert((C == 0).all())

class bitpaircountTest(unittest.TestCase):
    """Test the bitpaircount function with known answers."""
    def test_zeros(self):
        # generate a load of zeros
        for typ in get_test_types():
            zdist = np.zeros(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the bitpaircounts
            C = bitpaircount(zdist)
            assert((C[0,:] == DIM_LEN).all())

    def test_ones_float32(self):
        # generate a load of zeros
        zdist = np.ones(
            shape = (DIM_LEN,),
            dtype = np.float32
        )
        # calculate the bitpaircounts
        C = bitpaircount(zdist)
        # pair 00
        assert((C[0,:22] == DIM_LEN).all())
        assert((C[0,22:30] == 0).all())
        assert(C[0,30] == DIM_LEN)
        # pair 01
        assert((C[1,0:29] == 0).all())
        assert(C[1,29] == DIM_LEN)
        assert(C[1,30] == 0)
        # pair 10
        assert((C[2,0:22] == 0).all())
        assert(C[2,22] == DIM_LEN)
        assert((C[2,23:] == 0).all())
        # pair 11
        assert((C[3,0:23] == 0).all())
        assert((C[3,23:29] == DIM_LEN).all())
        assert((C[29:31] == DIM_LEN).all())

if __name__ == '__main__':
    unittest.main()
