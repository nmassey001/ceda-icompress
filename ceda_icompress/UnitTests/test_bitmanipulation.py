import unittest
import numpy as np
from numpy.random import default_rng

from ceda_icompress.BitManipulation.bitshave import bitshave
from ceda_icompress.BitManipulation.bitset import bitset
from ceda_icompress.BitManipulation.bitgroom import bitgroom
from test_types import get_test_types


class bitshaveTest(unittest.TestCase):
    """Test the bitshave function with known answers."""
    def test_int32(self):
        # generate some random numbers
        rng = default_rng(100)
        rints = rng.integers(low=0, high=100000, size=100, dtype='i')
        # test the bitshave at NSB=20
        with self.assertRaises(TypeError):
            bitshave(rints, NSB=20)

    def test_float16(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random([100], dtype='<f') * 1000 - 500
        rflts = rflts.astype(dtype=np.float16)
        # test the bitshave at NSB=3
        x = bitshave(rflts, NSB=5)
        print(rflts[0], x[0])

    def test_float32(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype='<f') * 1000 - 500
        # test the bitrounddown at NSB=11
        x = bitshave(rflts, NSB=11)
        print(rflts[0], x[0])

    def test_float64(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype=np.float64) * 1000 - 500
        # test the bitrounddown at NSB=26
        x = bitshave(rflts, NSB=11)
        print(rflts[0], x[0])


class bitsetTest(unittest.TestCase):
    """Test the bitset function with known answers."""
    def test_int32(self):
        # generate some random numbers
        rng = default_rng(100)
        rints = rng.integers(low=0, high=100000, size=100, dtype='i')
        # test the bitshave at NSB=20
        with self.assertRaises(TypeError):
            bitset(rints, NSB=20)

    def test_float16(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype='<f') * 1000 - 500
        rflts = rflts.astype(dtype=np.float16)
        # test the bitshave at NSB=6
        x = bitset(rflts, NSB=9)
        print(rflts[1], x[1])

    def test_float32(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype='<f') * 1000 - 500
        # test the bitrounddown at NSB=11
        x = bitset(rflts, NSB=11)
        print(rflts[0], x[0])

    def test_float64(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype=np.float64) * 1000 - 500
        # test the bitrounddown at NSB=26
        x = bitset(rflts, NSB=10)
        print(rflts[56], x[56])


class bitgroomTest(unittest.TestCase):
    """Test the bitgroom function with known answers."""
    def test_int32(self):
        # generate some random numbers
        rng = default_rng(100)
        rints = rng.integers(low=0, high=100000, size=100, dtype='i')
        # test the bitshave at NSB=20
        with self.assertRaises(TypeError):
            bitgroom(rints, NSB=20)

    def test_float16(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype='<f') * 1000 - 500
        rflts = rflts.astype(dtype=np.float16)
        # test the bitshave at NSB=6
        x = bitgroom(rflts, NSB=6)
        print(rflts[1], x[1])

    def test_float32(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype='<f') * 1000 - 500
        # test the bitrounddown at NSB=11
        x = bitgroom(rflts, NSB=11)
        print(rflts[0], x[0])

    def test_float64(self):
        # generate some floating point random numbers
        rng = default_rng(1000)
        rflts = rng.random(100, dtype=np.float64) * 1000 - 500
        # test the bitrounddown at NSB=26
        x = bitgroom(rflts, NSB=26)
        print(rflts[56], x[56])


if __name__ == '__main__':
    unittest.main(bitgroomTest())
