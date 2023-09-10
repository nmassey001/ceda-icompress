import numpy as np

class UIntConversionException(Exception):
    pass

def whichUint(t=np.int8):
    """Return the numpy integer type to recast an array to, based on the actual
    type of the numpy array, passed in as the dtype

    Args:
        t (numpy dtype): type of array to recast to integer representation

    Returns:
        numpy dtype: the type of the recast array
    """
    if t == np.int8 or t == np.uint8:
        return np.uint8
    elif t == np.int16 or t == np.uint16:
        return np.uint16
    elif t == np.int32 or t == np.uint32:
        return np.uint32
    elif t == np.int64 or t == np.uint64:
        return np.uint64
    elif t == np.float16 or t == '<f2' or t == '>f2':
        return np.uint16
    elif t == np.float32 or t == '<f4' or t == '>f4':
        return np.uint32
    elif t == np.float64 or t == '<f8' or t == '>f8':
        return np.uint64
    else:
        raise UIntConversionException(
            "Cannot convert type: {}".format(t)
        )

def whichint(t=np.int8):
    """Return the numpy integer type to recast an array to, based on the actual
    type of the numpy array, passed in as the dtype

    Args:
        t (numpy dtype): type of array to recast to integer representation

    Returns:
        numpy dtype: the type of the recast array
    """
    if t == np.int8 or t == np.uint8:
        return np.int8
    elif t == np.int16 or t == np.uint16:
        return np.int16
    elif t == np.int32 or t == np.uint32:
        return np.int32
    elif t == np.int64 or t == np.uint64:
        return np.int64
    elif t == np.float16 or t == '<f2' or t == '>f2':
        return np.int16
    elif t == np.float32 or t == '<f4' or t == '>f4':
        return np.int32
    elif t == np.float64 or t == '<f8' or t == '>f8':
        return np.int64
    else:
        raise UIntConversionException(
            "Cannot convert type: {}".format(t)
        )