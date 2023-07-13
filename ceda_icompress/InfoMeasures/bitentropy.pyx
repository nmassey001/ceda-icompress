import numpy as np
cimport numpy as np

from ceda_icompress.InfoMeasures.whichUint import whichUint

cpdef bitentropy(np.ndarray A, int base=2):
    """Calculate the bit entropy of a numpy array.
    Code converted to Python from https://github.com/esowc/Elefridge.jl

    Args:
        A (numpy array): array to calculate bitentropy for.
        base (int, optional): convert to a base, default is 2.

    Returns:
        float: the bit entropy of the array.
    """
    # type declarations
    cdef np.ndarray Av
    cdef np.int n
    cdef np.float64_t E
    cdef np.float64_t m
    cdef np.float64_t p
    cdef int x

    # get the type of the array when converted to a UInt
    t_uint = whichUint(A.dtype)

    # convert the array to the UInt type, flatten it and sort it
    Av = A.view(dtype=t_uint).flatten()
    Av.sort()

    # get the size of the array
    n = Av.size
    E = 0.0     # entropy
    m = 1.0     # counter

    for x in np.arange(0, n-1):
        if Av[x] == Av[x+1]:
            m += 1.0
        else:
            p = m/n
            E -= p*np.log(p)
            m = 1.0

    p = m/n         # complete for last adjacent values
    E -= p*np.log(p)

    # convert to given base, 2 i.e. [bit] by default
    E /= np.log(base)

    print(E)

    return E
