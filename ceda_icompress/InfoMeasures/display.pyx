##### Lovely colours! ######
import numpy as np
cimport numpy as np

from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp

class bcolors:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERT = '\033[7m'

    class fg:
        MAGENTA = '\033[95m'
        BLUE    = '\033[94m'
        GREEN   = '\033[92m'
        YELLOW  = '\033[93m'
        RED     = '\033[91m'
        GREY    = '\033[37m'
        WHITE   = '\033[97m'
        BLACK   = '\033[30m'

    class bg:
        BLACK   = '\033[40m'
        BLUE    = '\033[44m'
        GREEN   = '\033[42m'
        ORANGE  = '\033[43m'
        RED     = '\033[41m'
        GREY    = '\033[100m'

# a colour bar using ANSI terminal colours, writing to the background
bg_color_bar = ['\033[40m',     # black
                '\033[100m',    # bright black (dark grey)
                '\033[44m',     # blue
                '\033[104m',    # bright blue
                '\033[42m',     # green
                '\033[102m',    # bright green
                '\033[46m',     # cyan
                '\033[106m',    # bright cyan
                '\033[43m',     # yellow
                '\033[103m',    # bright yellow
                '\033[41m',     # red
                '\033[101m',    # bright red
                '\033[45m',     # magenta
                '\033[105m',    # bright magenta
                '\033[47m',     # white (light grey)
                '\033[107m']    # bright white

def displayBitCount(np.ndarray B, np.ndarray A):
    """Display the bit count of an array using colours for the sign bit,
    mantissa and exponent.

    Inputs:
        B (numpy array): array of bitcounts
        A (numpy array): original array bitcounts were taken from

    Returns:
        None

    Outputs:
        The array of bit counts, coloured to reflect the position in the
        original array
            sign     = yellow on grey
            exponent = white on red
            mantissa = white on blue
        Integer (non floating-point) types will be all white on blue (mantissa)
    """
    # get the sign, exponent and mantissa positions in the bitstring
    sig, man, exp = getsigmanexp(A)
    sized = A.dtype.itemsize * 8
    # print the sign bit
    S = ""
    for i in range(0, sized):
        # check if we should change colour
        if i == sig:
            S += bcolors.fg.YELLOW + bcolors.bg.GREY
        elif i >= man[0] and i < man[1]:
            S += bcolors.fg.WHITE + bcolors.bg.BLUE
        elif i >= exp[0] and i < exp[1]:
            S += bcolors.fg.WHITE + bcolors.bg.RED
        S += "{:3d}".format(B[i])
    S += bcolors.ENDC
    print(S)

def displayBitCountLegend():
    """Display the legend for the bit count printout"""
    S  = "\t" + bcolors.fg.YELLOW + bcolors.bg.GREY + " 0 "
    S += bcolors.ENDC + " - sign bit\n"
    S += "\t" + bcolors.fg.WHITE + bcolors.bg.RED + " 1 "
    S += bcolors.ENDC + " - exponent\n"
    S += "\t" + bcolors.fg.WHITE + bcolors.bg.BLUE + " 2 "
    S += bcolors.ENDC + " - mantissa" + bcolors.ENDC
    print(S)

def displayBitInformation(np.ndarray B):
    """Display a colour for each bit information bit."""
    S = ""
    for i in range(0, B.size):
        # calculate the position in the colour bar table
        # bit information is from 0 to 1 so simply multiply and cast to int
        lbg = len(bg_color_bar)
        cb_p = int(B[i] * lbg)
        if (cb_p >= lbg):
            cb_p = lbg - 1
        S += bg_color_bar[cb_p]
        S += "{:3.0f}".format(B[i]*100)
    S += bcolors.ENDC
    print(S)

def displayColorBar():
    """Display the colour bar used to print out the bit information."""
    S = "\t"
    L = len(bg_color_bar)
    for i in range(0, L):
        S += bg_color_bar[i]
        if i == 0:
            S += bcolors.fg.WHITE + "   0"
        elif i == L-1:
            S += bcolors.fg.BLACK + " 100"
        else:
            S += "   "
    S += bcolors.ENDC + " - colour bar"
    print(S)

def displayBitPosition(np.ndarray B):
    """Display the bit position in an easy to read manner."""
    S = ""
    for i in range(0, B.size):
        if i % 2 == 0:  # evens - white on grey
            S += bcolors.fg.WHITE + bcolors.bg.GREY
        else:
            S += bcolors.fg.BLACK + bcolors.bg.GREEN
        S += "{:3d}".format(i)
    S += bcolors.ENDC
    print(S)
