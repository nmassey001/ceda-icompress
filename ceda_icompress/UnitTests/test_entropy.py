import unittest
import numpy as np

from ceda_icompress.InfoMeasures.entropy import entropy
from test_types import get_test_types

DIM_LEN=128

class entropyTest(unittest.TestCase):
    """Test the entropy calculation.  Remember that the array passed in is an
    array of probabilities."""
    def test_zeros(self):
        for typ in get_test_types():
            # generate a load of zeros
            zdist = np.ma.zeros(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the entropy - should be 0.0 for all zeros
            C = entropy(zdist)
            assert(C == 0.0)

    def test_ones(self):
        # generate a load of ones
        for typ in get_test_types():
            zdist = np.ma.ones(
                shape = (DIM_LEN,),
                dtype = typ
            )
            # calculate the entropy - should be 0.0 for all ones
            C = entropy(zdist)
            assert(C == 0.0)

    def test_all_same(self):
        # generate a load of the same value
        for typ in get_test_types():
            zdist = np.ma.ones(
                shape = (DIM_LEN,),
                dtype = typ
            ) * 0.5
            # calculate the entropy - should be approximately = 0.5 * DIM_LEN
            # for all the same value
            C = entropy(zdist)
            assert(int(C) == 0.5 * DIM_LEN)

if __name__ == '__main__':
    unittest.main()
