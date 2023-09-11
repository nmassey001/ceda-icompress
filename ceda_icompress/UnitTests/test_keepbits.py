import unittest
import numpy as np

from ceda_icompress.InfoMeasures.keepbits import keepbits
from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp
from test_types import get_test_types

DIM_LEN=1000

class keepbitsTest(unittest.TestCase):
    """Test the keepbits calculation."""
    def test_zeros(self):
        for typ in get_test_types():
            # generate a load of zeros
            shape = (DIM_LEN,)
            zdist = np.ma.zeros(
                shape,
                dtype = typ
            )
            sig, man, exp = getsigmanexp(zdist.dtype)
            # calculate the infocontent - should be zero
            C = bitinformation(zdist)
            x = keepbits(C, man, shape, 0.95)

if __name__ == '__main__':
    unittest.main()
