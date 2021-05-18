
# ceda_icompress

A library and command line client to apply lossy compression to netCDF files,
by rounding bytes and applying run length encoding.

The rounding byte point is determined by Shannon Information Theory.
See:
    https://github.com/esowc/Elefridge.jl/ 
for the inspiration behind this library and more information about the technique.

Also see the paper by Charles Zender:
    https://gmd.copernicus.org/articles/9/3199/2016/gmd-9-3199-2016.pdf
