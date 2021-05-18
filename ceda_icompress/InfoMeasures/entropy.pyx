import numpy as np
cimport numpy as np

cpdef entropy(np.ndarray P, int base=2):
    """Calculate the information entropy, as defined is Shannon Information
    Theory, with an optional base to take the log.

    Information entropy is defined as:
        H = -sum_(i=1)^N(p_i * log_b (p_i))

    Inputs:
        P (numpy array): array to calculate bitentropy for.
        base (int, optional): base to calculate entropy for.

    Returns:
        float: the entropy of the input probabilities
    """

    cdef np.float64_t H             # return entropy
    cdef int x                      # counter
    cdef np.float64_t B             # log base
    B = np.log(base)

    # initialise entropy
    H = 0.0

    for x in range(P.size):
        # calculate the entropy 1.0 and 0.0 contribute 0 to the entropy
        if P[x] > 0.0 and P[x] < 1.0:
            H += P[x] * (np.log(P[x]) / B)

    # return the entropy
    return -1.0 * H
