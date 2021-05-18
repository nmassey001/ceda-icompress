import numpy as np
cimport numpy as np

from ceda_icompress.InfoMeasures.whichUint import whichUint

cpdef bitcount(np.ndarray A):
    """Calculate the number of times that bit=1 occurs at each bit position in
    the type of the input array, across all array elements.
    For example, in a 32 bit type, count how many 1s are in position 0 across
    the whole array.  Repeat for the other 31 positions.

    Code inspired by https://github.com/esowc/Elefridge.jl

    Args:
        A (numpy array): array to calculate bitcount for.

    Returns:
        numpy array: the bit count of the array.
            This will be 8 elements wide for a byte.
                        16               for a short int.
                        32               for an int / float.
                        64               for a long int / double
    """
    # type declarations
    cdef np.ndarray Av
    cdef np.ndarray N
    cdef int x                          # loop counter
    cdef int n_bits                     # number of bits

    # get the UInt type of the array so we can create the count array
    t_uint = whichUint(A.dtype)             # type
    n_bits = A.itemsize*8                   # number of bits per array element
    N = np.zeros((n_bits,), dtype=np.int32) # count array

    # convert the array to a view of the array in the UInt type and flatten it
    Av = A.view(dtype=t_uint).flatten()

    # now loop over each element of the array and count the bits in the position
    for x in range(0, Av.size):
        for b in np.arange(0, n_bits, dtype=t_uint):
            # define the mask based on the datatype
            mask = t_uint(0b1) << b
            # see if that bit is set - bitwise and with mask and add to bitcount
            # if it is
            if (Av[x] & mask) > 0:
                N[b] += 1
    return N


cpdef bitpaircount(np.ndarray A):
    """Calculate the number of times that bitpairs occur at each bit position in
    the type of the input array, across all array elements.
    The bit pairs are: 00, 01, 10, 11
    For example, in a 32 bit type, count:
      1. how many 00s are in position n & n+1 (as a pair)
      2. how many 01s are in position n & n+1 (as a pair)
      3. how many 10s are in position n & n+1 (as a pair)
      4. how many 11s are in position n & n+1 (as a pair)
    Repeat for n=0..N-1, where N is the size of the flattened array

    Returns:
     numpy array(4,B): the bit pair count of the array.
         B will be 8 elements wide for a byte.
                  16               for a short int.
                  32               for an int / float.
                  64               for a long int / double
         4 reflects that there are 4 pairs, the positions are:
                  0 : 00
                  1 : 01
                  2 : 10
                  3 : 11
    """
    # type declarations
    cdef np.ndarray Av
    cdef np.ndarray N
    cdef int x                          # loop counter
    cdef int n_bits                     # number of bits

    # get the UInt type of the array so we can create the count array
    t_uint = whichUint(A.dtype)             # type
    n_bits = A.itemsize*8                   # number of bits per array element
    N = np.zeros((4, n_bits-1,), dtype=np.int32) # count array

    # convert the array to a view of the array in the UInt type and flatten it
    Av = A.view(dtype=t_uint).flatten()

    # now loop over each element of the array and count the bits in the position
    for x in range(0, Av.size):
        for b in np.arange(0, n_bits-1, dtype=t_uint):
            # position mask for this bit pair
            #bs = t_uint(b)
            p_mask = t_uint(0b11) << b
            # and it and then shift right by b to get just the bit pair
            # in the 0 and 1 position in the binary string
            bitpair = (Av[x] & p_mask) >> b
            # this bitpair translates directly to the decimal index of the N
            # count array for this position
            N[bitpair, b] += 1
    return N
