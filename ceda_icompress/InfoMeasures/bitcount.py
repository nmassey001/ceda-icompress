import numpy as np

from ceda_icompress.InfoMeasures.whichUint import whichUint

def bitcount(A):
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
    # get the UInt type of the array so we can create the count array
    t_uint = whichUint(A.dtype)             # type
    n_bits = A.itemsize*8                   # number of bits per array element
    N = np.zeros((n_bits,), dtype=np.int32) # count array

    # convert the array to a view of the array in the UInt type and flatten it
    Av = A.view(dtype=t_uint).flatten()

    # now loop over each element of the array and count the bits in the position
    for b in np.arange(0, n_bits, dtype=t_uint):
        # define the mask based on the datatype
        mask = t_uint(0b1) << b
        # mask with the whole array
        Ar = np.ma.bitwise_and(Av, mask)
        # count
        N[b] = np.count_nonzero(Ar)
    return N


def bitpaircount(A, B):
    """Calculate the number of times that bitpairs occur at each bit position in
    the input array (A) compared to the array (B).
    The bit pairs are: 00, 01, 10, 11
    For example, in a 32 bit type, count:
      1. how many 00s are in position An & Bn
      2. how many 01s are in position An & Bn
      3. how many 10s are in position An & Bn
      4. how many 11s are in position An & Bn
    Repeat for n=0..N, where N is the maximum size of the two flattened arrays

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
    # get the UInt type of the array so we can create the count array
    t_uint = whichUint(A.dtype)             # type
    n_bits = A.itemsize*8                   # number of bits per array element
    N = np.zeros((4, n_bits,), dtype=np.int64) # count array

    # 1. convert the arrays to a view of the array in the UInt type 
    # 2. take a slice
    # 3. then flatten it into a bitstream
    # using view before a slice means that the array is not copied
    Av = A.view(dtype=t_uint).flatten()
    Bv = B.view(dtype=t_uint).flatten()

    # count the bits in the position of each array
    for b in np.arange(0, n_bits, dtype=t_uint):
        # position mask for this bit
        b_mask = t_uint(0b1) << b
        # get the bit for A
        Ar = np.ma.bitwise_and(Av, b_mask)
        # get the bit for B
        Br = np.ma.bitwise_and(Bv, b_mask)
        # shift back for each array, A by b-1, B by b
        # this forms the pairs when A + B
        Ab = np.ma.right_shift(Ar, b-1)
        Bb = np.ma.right_shift(Br, b)
        bitpair = np.ma.bitwise_or(Ab, Bb)
        # count up the bit pairs
        for m in np.arange(0, 4, dtype=np.int32):
            N[m, b] += np.count_nonzero(bitpair == m)
    # reshape the array to 2x2
    N = N.reshape((2,2,n_bits))
    return N
