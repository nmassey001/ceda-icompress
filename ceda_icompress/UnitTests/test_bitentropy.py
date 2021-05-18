import unittest
import numpy as np

from ceda_icompress.InfoMeasures.bitentropy import bitentropy
from test_types import get_test_types

DIM_LEN = 128
N_BITS = 8

class bitentropyTest(unittest.TestCase):
    """Test the bitentropy function with known answers."""
    def test_all_numbers(self):
        # generate a distribution that just contains all the numbers from 0 to
        # 2**n
        # this is a good test as the entropy should be very close to n
        DIM_LEN = 2**N_BITS
        for typ in get_test_types():
            ddist = np.arange(
                0, 2**N_BITS,
                dtype = typ
            )
            E = bitentropy(ddist)
            self.assertTrue(np.round(E)==N_BITS)

    def test_zeros(self):
        # generate a load of zeros
        for typ in get_test_types():
            zdist = np.zeros(
                shape = (DIM_LEN, DIM_LEN, DIM_LEN),
                dtype = typ
            )
            # calculate the bit entropy should be 0
            E = bitentropy(zdist)
            self.assertEqual(E, 0.0)

    def test_ones(self):
        # generate a load of zeros
        for typ in get_test_types():
            zdist = np.ones(
                shape = (DIM_LEN, DIM_LEN, DIM_LEN),
                dtype = typ
            )
            # calculate the bit entropy should be 0
            E = bitentropy(zdist)
            self.assertEqual(E, 0.0)

if __name__ == '__main__':
    unittest.main()
