"""Bit Manipulation base class to derive concrete classes from"""

from ceda_icompress.InfoMeasures.keepbits import keepbits
from ceda_icompress.InfoMeasures.whichUint import whichUint

import numpy as np

class BitManipulationError(Exception):
    pass

class BitManipulation:
    def __init__(self, A, NSB, analysis, ci):
        """Side effects:
            self.t_uint (str) : the type of array A
        """

        # NSB = number of signficant bits, -1 to derive NSB from bitinfo
        # analysis = results of cic_analysis
        # ci = confidence interval
        # check that the type is compatible, either a float16, float32 or float64
        if not (A.dtype in [np.float16, "<f2", ">f2",
                            np.float32, "<f4", ">f4",
                            np.float64, "<f8", ">f8"]):
            raise TypeError("Unsupported type for bitshave : {}".format(
                                A.dtype
                            ))
        # get the type
        self.t_uint = whichUint(A.dtype)
        
    def get_NSB(self, NSB, analysis, ci):
        """Side effects:
            self.NSB (int)    : the number of significant bits
        """

        # only need to determine keep bits if not set by user
        if NSB == -1:
            # check we have the analysis data!
            if not "bitinfo" in analysis:
                raise BitManipulationError(
                    "No bitinfo key in analysis data"
                )
            # get the information
            bi = np.array(analysis["bitinfo"])
            # get the location of the mantissa bits
            if not "manbit" in analysis:
                raise BitManipulationError(
                    "No manbit key in analysis data"
                )
            manbit = analysis["manbit"]
            # get the number of elements the analysis was performed on
            if not "elements" in analysis:
                raise BitManipulationError(
                    "No elements key in analysis data"
                )
            elements = analysis["elements"]        
            # calculate the number of bits to retain
            self.NSB = keepbits(bi, manbit, elements, ci)
        else:
            self.NSB = NSB

    def process(self, A):
        # process an array using the BitManipulation
        # A = numpy array
        raise NotImplementedError
