import numpy as np

def get_test_types():
    """Return a list of types to test against"""
    test_types = [
        np.int8, np.uint8,
        np.int16, np.uint16,
        np.int32, np.uint32,
        np.int64, np.uint64,
        np.float32, '<f4', '>f4',
        np.float64, '<f8', '>f8',
        float, int
    ]
    return test_types
