import numpy as np
from numpy.random import default_rng

from ceda_icompress.InfoMeasures.bitcount import bitcount
from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.display import displayBitCount,\
                                                displayBitCountLegend
from ceda_icompress.InfoMeasures.display import displayBitInformation,\
                                                displayColorBar,\
                                                displayBitPosition
if __name__ == "__main__":
    # test the bit count and bit information routines and print them out
    x = np.arange(0.0, 100.0, dtype=np.float32)
    print("---------- Bit count ----------")
    bc = bitcount(x)
    displayBitPosition(bc)
    displayBitCount(bc, x)
    displayBitCountLegend()

    print("---------- Bit Information ----------")
    bi = bitinformation(x)
    displayBitPosition(bi)
    displayBitInformation(bi)
    displayColorBar()

    # random
    print("---------- Random ints --------------")
    rng = default_rng(1000)
    rints = rng.integers(low=0, high=1000, size=100, dtype='i') - 1000

    bc = bitcount(rints)
    displayBitPosition(bc)
    displayBitCount(bc, rints)
    displayBitCountLegend()

    br = bitinformation(rints)
    displayBitPosition(br)
    displayBitInformation(br)
    displayColorBar()

    print("---------- Random floats -----------")
    rng = default_rng(1000)
    rflts = rng.random(100, dtype=np.float32) * 1

    bc = bitcount(rflts)
    displayBitPosition(bc)
    displayBitCount(bc, rflts)
    displayBitCountLegend()

    bf = bitinformation(rflts)
    displayBitPosition(bf)
    displayBitInformation(bf)
    displayColorBar()
