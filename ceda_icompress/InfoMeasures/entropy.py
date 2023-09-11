import numpy as np

def entropy(P, base=2):
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
    B = np.log(base)
    # initialise entropy
    idx = np.where((P > 0.0) & (P < 1.0))
    Hr = P[idx] * np.log(P[idx])
    H = np.sum(Hr) / B
    # return the entropy
    return -1.0 * H