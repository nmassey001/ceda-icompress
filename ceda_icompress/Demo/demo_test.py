import numpy as np
from numpy.random import default_rng

from ceda_icompress.InfoMeasures.bitcount import bitcount
from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.display import (displayBitCount,
                                                displayBitCountVertical,
                                                displayBitCountLegend)
from ceda_icompress.InfoMeasures.display import (displayBitInformation,
                                                displayColorBar,
                                                displayBitPosition)
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp

if __name__ == "__main__":
    # test the bit count and bit information routines and print them out
    x = np.arange(0.0, 100.0, dtype=np.float32)
    print("---------- Bit count ----------")
    bc = bitcount(x)
    sig, man, exp = getsigmanexp(x.dtype)
    sized = x.dtype.itemsize
    L = bc.size
    X = np.max(bc)
    W = int(np.log10(X)+2)
    displayBitPosition(L)
    displayBitCount(bc, sig, man, exp, sized)
    displayBitCountLegend()
    displayBitCountVertical(bc, sig, man, exp, sized)

    print("---------- Bit Information ----------")
    bi = bitinformation(x)
    L = bi.size
    displayBitPosition(L)
    displayBitInformation(bi)
    displayColorBar()

    # random
    print("---------- Random ints --------------")
    rng = default_rng(1000)
    rints = rng.integers(low=0, high=1000, size=100, dtype='i') - 1000

    sig, man, exp = getsigmanexp(rints.dtype)
    sized = rints.dtype.itemsize

    bc = bitcount(rints)
    L = bc.size
    displayBitPosition(L)
    displayBitCount(bc, sig, man, exp, sized)
    displayBitCountLegend()

    br = bitinformation(rints)
    L = br.size
    displayBitPosition(L)
    displayBitInformation(br)
    displayColorBar()

    print("---------- Random floats -----------")
    rng = default_rng(1000)
    rflts = rng.random(100, dtype=np.float32) * 1

    sig, man, exp = getsigmanexp(rflts.dtype)
    sized = rflts.dtype.itemsize

    bc = bitcount(rflts)
    L = bc.size
    displayBitPosition(L)
    displayBitCount(bc, sig, man, exp, sized)
    displayBitCountLegend()

    bf = bitinformation(rflts)
    L = bf.size
    displayBitPosition(L)
    displayBitInformation(bf)
    displayColorBar()
