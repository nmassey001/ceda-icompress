import numpy as np

from ceda_icompress.InfoMeasures.bitcount import bitcount, bitpaircount
from ceda_icompress.InfoMeasures.entropy import entropy

def bitinformation(A):
    """Calculate the bitwise information content, as defined in Shannon
    Information Theory, and on the webpage:
        https://github.com/esowc/Elefridge.jl.

    Bitwise information content is defined as:
        I = H - q0*H0 - q1*H1

    where:
        I  = information content
        H  = entropy (see entropy.pyx file for definition and code)
        q0 = probability of a bit being 0
        q1 = probability of a bit being 1
        H0 = conditional entropy, conditional on a bit being 0 or 1 given that
             the previous bit is 0
        H1 = conditional entropy, conditional on a bit being 0 or 1 given that
             the previous bit is 1

    Inputs:
        A (numpy array): array to calculate bitinformation for.

    Returns:
        float: the bitinformation of the input array
    """
    N = A.size               # number of elements in the array
    n1 = bitcount(A)[0:-1]   # number of ones in each bit-position
    n0 = N-n1                # number of zeros in each bit-position
    q0 = n0/N                # probability of a zero in each bit-pos
    q1 = n1/N                # probability of a one in each bit-pos

    npair = bitpaircount(A)  # pair counts of 00, 01, 10 and 11

    # preallocate the conditional probability
    pcond = np.zeros_like(npair, dtype=np.float32)
    # these are the conditional probabilities
    # - do not divide by zeros
    # - leave those as zeros from the array definition
    n0_nz = np.nonzero(n0)
    n1_nz = np.nonzero(n1)

    pcond[0][n0_nz] = npair[0][n0_nz] / n0[n0_nz]  # p(0|0) = n(00)/n(0)
    pcond[1][n0_nz] = npair[1][n0_nz] / n0[n0_nz]  # p(1|0) = n(01)/n(0)
    pcond[2][n1_nz] = npair[2][n1_nz] / n1[n1_nz]  # p(0|1) = n(10)/n(1)
    pcond[3][n1_nz] = npair[3][n1_nz] / n1[n1_nz]  # p(1|1) = n(11)/n(1)

    # set nans to 0
    pcond[np.isnan(pcond)] = 0

    # calculate the unconditional entropy
    qi = np.vstack([q0,q1])
    H = np.zeros((qi.shape[1],), dtype=np.float32)
    for i in np.arange(0, qi.shape[1]):
        H[i] = entropy(qi[:,i], 2)

    # calculate the conditional entropies given bit = 0, first, then bit = 1
    pi0 = np.vstack([pcond[0], pcond[1]])
    pi1 = np.vstack([pcond[2], pcond[3]])
    assert(pi0.shape[1] == pi1.shape[1])

    H0 = np.zeros((pi0.shape[1],), dtype=np.float32)
    H1 = np.zeros((pi1.shape[1],), dtype=np.float32)

    for i in np.arange(0, pi0.shape[1]):
        H0[i] = entropy(pi0[:,i], 2)
        H1[i] = entropy(pi1[:,i], 2)

    # Information content
    I = np.abs(H - q0*H0 - q1*H1)

    return I
