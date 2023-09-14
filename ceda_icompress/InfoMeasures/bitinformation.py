import numpy as np

from ceda_icompress.InfoMeasures.bitcount import bitpaircount
from ceda_icompress.InfoMeasures.signedexponent import signed_exponent

def bitinformation(X, axis=0, convert_exponent=True, base=2):
    """Calculate the bitwise information content, as defined in Shannon
    Information Theory, and on the webpage:
        https://github.com/esowc/Elefridge.jl.

    *** This is not current!  Replace!! ***
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

    ### probability mass function version replaces  
    ### conditional probability version ###
    if convert_exponent:
        X = signed_exponent(X)

    # calculate the slices
    a_slice = tuple(
        slice(0, -1) if i==axis else slice(None) for i in range(0, X.ndim)
    )
    b_slice = tuple(
        slice(1, None) if i==axis else slice(None) for i in range(0, X.ndim)
    )
    A = X.view()[a_slice]
    B = X.view()[b_slice]

    # get the counts of pairs of bits 00 01 10 11
    C = bitpaircount(A, B)
    # probability mass function of the bitpairs
    P = C.astype(np.float64) / B.count()
    Pm = np.ma.masked_equal(P, 0.0)
    # conditional probabilities
    Pr = np.ma.sum(Pm, axis=0)[np.newaxis, ...]
    Ps = np.ma.sum(Pm, axis=1)[:, np.newaxis,...]
    # mutual information
    M = np.ma.sum(Pm * np.ma.log(Pm / (Ps * Pr)), axis=(0,1)) / np.ma.log(base)
    return M
