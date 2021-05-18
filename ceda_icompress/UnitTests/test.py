from netCDF4 import Dataset
import os

from ceda_icompress.InfoMeasures.bitentropy import bitentropy

if __name__ == "__main__":
    file_name = os.path.join(
        os.environ["HOME"],
        "Archive/Sentinel5",
        "S5P_OFFL_L1B_RA_BD6_20180521T204524_20180521T222654_03128_01_010000_20180522T023759.nc"
    )

    ds = Dataset(file_name, "r")
    # 2.7GB field
    f = (
        ds.groups["BAND6_RADIANCE"].
        groups["STANDARD_MODE"].
        groups["OBSERVATIONS"].
        variables["radiance"]
    )
    print(f.size)
    #be = bitentropy(f)
