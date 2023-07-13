#! /usr/bin/env python
import click
from netCDF4 import Dataset
import sys
import json
from cic_analyse import load_dataset
from ceda_icompress.BitManipulation.bitshave import bitshave
from ceda_icompress.BitManipulation.bitgroom import bitgroom
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp

COMPRESSION = 'zlib'

def copy_dim(input_dim, output_group):
    output_dim = output_group.createDimension(
        dimname = input_dim.name, 
        size = input_dim.size
    )
    
def getNSB(bi, manbit, thresh=0.01):
    """Get the number of significant bits to retain, from the bitInformation"""
    NSB = 0
    for i in range(manbit[1], manbit[0], -1):
        NSB += 1
        if bi[i] < thresh:
            break
    # bit information is in opposite order to bits
    return manbit[0] + NSB


def process_var(input_var, output_group, analysis, params):
    # get the fill value
    try:
        mv = input_var.getncattr("_FillValue")
    except AttributeError:
        mv = None
    # determine the chunking
    if input_var.chunking() == 'contiguous':
        chunking = None
    else:
        chunking = input_var.chunking()

    # create the output variable
    output_var = output_group.createVariable(
        varname = input_var.name, 
        datatype = input_var.dtype, 
        dimensions = input_var.dimensions,
        compression = COMPRESSION,
        complevel = params["deflate"],
        contiguous = False,
        chunksizes = chunking,
        endian = input_var.endian(),
        fill_value = mv,
        chunk_cache = input_var.get_var_chunk_cache()[0]
    )

    # copy the attributes from input_var to output_var
    output_var.setncatts(input_var.__dict__)

    # bitshave / bitgroom the data if the variable is in the analysis file
    if (output_group.name in analysis["groups"] and 
        input_var.name in analysis["groups"][output_group.name]["vars"]):
        # get the variable analysis from the analysis dictionary
        Va = analysis["groups"][output_group.name]["vars"][input_var.name]
        # get BitInformation
        bi = Va["bitinfo"]
        # get the location of the mantissa bits
        manbit = Va["manbit"]
        NSB = getNSB(bi, manbit, thresh=params["thresh"])
        # copy the data from input_var to output_var, doing the bitshave or bitgroom
        print(NSB)
        output_var[:] = bitshave(input_var[:], NSB)
    else:
        output_var[:] = input_var[:]


def process_groups(input_group, output_group, analysis, params):
    # input_group might be a Dataset
    # copy the metadata
    output_group.setncatts(input_group.__dict__)

    # copy the dimensions
    for dim in input_group.dimensions:
        copy_dim(input_group.dimensions[dim], output_group)
    # copy the variables
    for var in input_group.variables:
        process_var(
            input_group.variables[var], output_group, analysis, params
        )
    # copy all the groups belonging to this group recursively
    for grp in input_group.groups:
        new_group = output_group.createGroup(grp.name)
        process_groups(input_group.groups[grp], new_group, analysis, params)


def process(input_ds, output_ds, analysis, params):
    """Process the input dataset, using the analysis, writing to the output_ds"""
    # first copy all the groups, variables and metadata
    process_groups(input_ds, output_ds, analysis, params)
    output_ds.close()


@click.command(
    help="Apply the compression to a netCDF using the analysis derived earlier"
)
@click.option("-a", "--analysis_file", default=None, type=str,
              help="Analysis file generated from cic_analyse.py")
@click.option("-d", "--deflate", default=1, type=int,
              help="Deflate (compression) level to use when writing file")
@click.option("-f", "--force", is_flag=True, 
              help="Force compression of file, even if input file does not " 
              "match the file named in the analysis")
@click.option("-t", "--thresh", default=99.9, type=float, 
              help="The bitinformation threshold - how much information to "
                   "retain, in %. e.g. 99.9%")
@click.option("-I", "--conv_int", is_flag=True, default=False,
              help="Convert 64 bit integers to 32 bit integers")
@click.option("-F", "--conv_float", is_flag=True, default=False,
              help="Convert 64 bit floats to 32 bit floats")
@click.option("-o", "--output", default=None, type=str,
              help="Output file name")
@click.argument("file", type=str)
def compress(file, analysis_file, deflate, force, conv_int, conv_float,
             thresh, output):
    # Load the analysis file
    if analysis_file is None:
        print("Analysis file name not supplied")
        sys.exit(0)
    # Load the analysis file
    try:
        fh = open(analysis_file, "r")
    except FileNotFoundError:
        print(f"Analysis file cannot be found: {str(analysis_file)}")
        sys.exit(0)
    # Parse the analysis file
    try:
        analysis = json.load(fh)
    except Exception as e:
        print(f"Analysis file cannot be parsed: {str(analysis_file)}, reason: {e}")
        sys.exit(0)

    # open the output file - do this before the processing so an error in 
    # created before the (long) processing time if the exceptions are caught
    if output is None:
        print("Output file name not supplied")
        sys.exit(0)
    else:
        try:
            output_ds = Dataset(output, "w", deflate=deflate, format="NETCDF4")
        except Exception as e:
            print(f"Could not open output file {str(output)}, reason: {e}")
            sys.exit(0)

    # check that the name of the file in the analysis file matches the name of
    # the input file
    try:
        analysis_input_file = analysis["file"]
        if analysis_input_file != file and not force:
            print(f"Analysed file: {analysis_input_file}, does not match"
                  f"file to be compressed: {file}")
            sys.exit(0)
    except KeyError:
        print(f"Could not find file key in analysis file: {str(analysis_file)}")
        sys.exit(0)

    # open the input file
    input_ds = load_dataset(file)
    # process it, along with the analysis]
    params = {"thresh"     : (100.0-thresh)/100,
              "deflate"    : deflate,
              "conv_int"   : conv_int,
              "conv_float" : conv_float}
    print(params)
    process(input_ds, output_ds, analysis, params)

def main():
    compress()

if __name__ == "__main__":
    main()