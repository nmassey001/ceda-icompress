# S3-netcdf-python Makefile
# Simple makefile for compiling the Cython externals when developing

# Setup.py will build these externals once on installation, so it is not
# necessary to run this Makefile on installation for a user.
# This Makefile only needs to be used when developing.

all:
	python setup.py build_ext --inplace

clean:
	rm -f *.so *.c
	rm -f ./ceda_icompress/InfoMeasures/*.so ./ceda_icompress/InfoMeasures/*.c
	rm -f ./ceda_icompress/BitManipulation/*.so ./ceda_icompress/BitManipulation/*.c
