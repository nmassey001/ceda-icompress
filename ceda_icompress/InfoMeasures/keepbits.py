import numpy as np
from ceda_icompress.InfoMeasures.entropy import entropy

def binom_confidence(n, ci):
    # create a normal distribution generator
    g = np.random.default_rng()
    p = 0.5 + np.quantile(
                g.normal(0,1.0,n), 1-(1-ci)/2
              )/(2*np.sqrt(n))
    # clamp to a max of 1.0
    p = np.minimum([1.0], p)
    return p


def free_entropy(n, ci):
    """Calculate the free entropy for the probability in a binomial distribution
    """
    p = binom_confidence(n, ci)
    # calculate the free entropy of this distribution    
    fe = 1.0 - entropy(np.array([p, 1-p]), 2)
    return fe


def keepbits(bi, manbit, elements, ci):
    """Calculate the number of bits to retain in a data field
    bi       : bit information, calculated from bitinformation,
    manbit   : the start and end range of the mantissa bits for each value
    elements : the number of (non-masked) elements in the array
    ci       : the confidence interval"""

    # calculate the threshold from the shape and confidence interval
    # this is the free entropy of the probability of the binomial distribution 
    # see the methods section in Klower et al, 2021 for more details
    fe = free_entropy(elements, ci)
    # this is from the xbitinfo code and seems like a cheat!
    threshold = np.maximum(fe, 1.5*np.max(bi[:3]))
    # mask the insignificant
    bi[np.where(bi <= threshold)] = 0.0
    # find bits with ci amount of info
    bi_sum = np.cumsum(bi)
    bi_sum = bi_sum / bi_sum[-1]
    i = manbit[0]
    while (bi_sum[i] < 1.0-ci):
        i += 1

    return manbit[1]-i
