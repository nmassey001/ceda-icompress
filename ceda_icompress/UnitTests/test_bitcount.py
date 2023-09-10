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
        zdist = np.ma.ones(
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
            zdist = np.ma.zeros(
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
            zdist = np.ma.zeros(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # right shift on 64 bit numbers & python types not supported by numpy
            if typ in [np.uint64, np.int64, np.float64, '<f8', '>f8', float, int]:
                continue
            # calculate the bitpaircounts
            C = bitpaircount(zdist, axis=0)
            # the zero pair should be the DIM_LEN-1
            assert((C[0,:] == DIM_LEN-1).all())
            # all others should be zero
            for i in range(1, 4):
                assert((C[i,:] == 0).all())

    def test_ones_float32(self):
        # generate a load of zeros
        zdist = np.ma.ones(
            shape = (DIM_LEN,),
            dtype = np.float32
        )
        # 23 bits for mantissa
        man = 23
        sig = 30
        # calculate the bitpaircounts
        C = bitpaircount(zdist, axis=0)
        # pair 00
        assert((C[0,:man] == DIM_LEN-1).all())
        assert((C[0,man:sig] == 0).all())
        assert((C[0,sig:] == DIM_LEN-1).all())
        # pair 01
        assert((C[1,:] == 0).all())
        # pair 10
        assert((C[2,:] == 0).all())
        # pair 11
        assert((C[3,0:man] == 0).all())
        assert((C[3,man:sig] == DIM_LEN-1).all())
        assert((C[sig:] == DIM_LEN-1).all())


if __name__ == '__main__':
    unittest.main()
