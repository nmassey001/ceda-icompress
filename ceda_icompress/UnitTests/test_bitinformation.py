import unittest
import numpy as np

from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from test_types import get_test_types

DIM_LEN=128

class bitinformationTest(unittest.TestCase):
    """Test the entropy calculation.  Remember that the array passed in is an
    array of probabilities."""
    def test_zeros(self):
        for typ in get_test_types():
            # generate a load of zeros
            zdist = np.ma.zeros(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the infocontent - should be zero
            C = bitinformation(zdist)
            assert((C == 0.0).all())

    def test_ones(self):
        # generate a load of ones
        for typ in get_test_types():
            zdist = np.ma.ones(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the infocontent - should be zero
            C = bitinformation(zdist)
            assert((C == 0.0).all())

    def test_all_same(self):
        # generate a load of the same value
        for typ in get_test_types():
            zdist = np.ma.ones(
                shape = (DIM_LEN,),
                dtype = typ
            ) * 0.5
            # calculate the infocontent - should be zero
            C = bitinformation(zdist)
            assert((C == 0.0).all())

    def test_random_float32(self):
        # generate a load of uniform random values
        zdist = np.random.uniform(
            0.0, 1.0,
            size=(DIM_LEN,),
        )
        # calculate the infocontent - should be
        C = bitinformation(zdist)
        assert(int(C) == 0.5 * DIM_LEN)

if __name__ == '__main__':
    unittest.main()
