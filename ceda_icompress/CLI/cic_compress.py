#! /usr/bin/env python
import click
from netCDF4 import Dataset
import sys
import json
import numpy as np
from datetime import datetime, timezone
import time
import os.path
from ceda_icompress.CLI.cic_analyse import load_dataset
from ceda_icompress.BitManipulation.bitshave import BitShave
from ceda_icompress.BitManipulation.bitgroom import BitGroom
from ceda_icompress.BitManipulation.bitset import BitSet
from ceda_icompress.BitManipulation.bitmask import BitMask
from ceda_icompress.CLI import CIC_FILE_FORMAT_VERSION

COMPRESSION = 'zlib'

def copy_dim(input_dim, output_group):
    output_dim = output_group.createDimension(
        dimname = input_dim.name, 
        size = input_dim.size
    )

def create_output_var(input_var, output_group, params, bit_manipulate):
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
    chunking = None

    # what type should we use? If we aren't manipulating the bits then check
    # whether we can convert a float64 to float32 or int64 to int32
    var_type = input_var.dtype

    if not bit_manipulate:
        if input_var.dtype == np.int64 and params["conv_int"]:
            var_type = np.int32
        elif input_var.dtype == np.float64 and params["conv_float"]:
            var_type = np.float32

    # create the output variable
    output_var = output_group.createVariable(
        varname = input_var.name,
        datatype = var_type, 
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

    return output_var

def process_var(input_var, output_group, analysis, params):
    # are we going to manipulate the bits?
    bit_manipulate = (output_group.name in analysis["groups"] and 
        input_var.name in analysis["groups"][output_group.name]["vars"])

    # create the var
    output_var = create_output_var(
        input_var, output_group, params, bit_manipulate
    )
    # bitshave / bitgroom the data if the variable is in the analysis file
    if (bit_manipulate):
        # get the variable analysis from the analysis dictionary
        Va = analysis["groups"][output_group.name]["vars"][input_var.name]
        # check to see if number of bits to retain are enforced?
        if "retainbits" in Va:
            NSB = Va["retainbits"]
        else:
            NSB = -1

        # get a pointer to the function to use
        if params["method"] == "bitshave":
            method = BitShave(input_var, NSB, Va, params["conf_int"])
        elif params["method"] == "bitgroom":
            method = BitGroom(input_var, NSB, Va, params["conf_int"])
        elif params["method"] == "bitset":
            method = BitSet(input_var, NSB, Va, params["conf_int"])
        elif params["method"] == "bitmask":
            method = BitMask(input_var, NSB, Va, params["conf_int"])

        # add a description of the compression to the variable
        atts = output_var.__dict__
        atts["compression"] = (
            f"ceda-icompress: keepbits: {method.NSB}, "
            f"method: {method.method}, "
            f"bitmask: {method.mask:<032b}."
        )
        # add to the history of the variable
        nowtime = datetime.now().replace(microsecond=0).isoformat()
        history = (f"{nowtime} altered by ceda-icompress: lossy compression.")
        if "history" in atts:
            atts["history"] += " " + history
        else:
            atts["history"] = history
        output_var.setncatts(atts)

        if params["debug"]:
            print(
                f"Processing variable: {input_var.name}\n"
                f"    Retained bits  : {method.NSB}\n"
                f"    Bitmask        : {method.mask:<032b}"
            )
        st = time.time()
        # do each individual timestep to prevent memory swapping
        t_dim = -1
        s = []
        dc = 0
        for d in input_var.dimensions:
            dim = output_group.dimensions[d]
            if d == "time" or d == "t":
                t_dim = dc
                t_len = dim.size
                # create the slices
                s.append(slice(0,1,1))
            else:
                s.append(slice(0,dim.size,1))
            dc += 1

        pc = params["pchunk"]
        if t_dim == -1:
            # copy the data from input_var to output_var, doing the bitshave or bitgroom
            # no time dimension so do all the variable at once
            output_var[:] = method.process(input_var[:])
        else:
            for t in range(0, t_len, pc):
                # modify the slice for the time dimensions
                s[t_dim] = slice(t,t+pc,1)
                output_var[s] = method.process(input_var[s])
        ed = time.time()
        if params["debug"]:
            print("    Time taken     :", ed-st)
    else:
        output_var[:] = input_var[:]


def process_groups(input_group, output_group, analysis, params):
    # input_group might be a Dataset
    # copy the metadata
    atts = input_group.__dict__
    output_group.setncatts(atts)

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
@click.option("-c", "--ci", default=0.99, type=float, 
              help="The confidence interval - how much information to "
                   "retain. default = 0.99 (99%)")
@click.option("-I", "--conv_int", is_flag=True, default=False,
              help="Convert 64 bit integers to 32 bit integers")
@click.option("-F", "--conv_float", is_flag=True, default=False,
              help="Convert 64 bit floats to 32 bit floats")
@click.option("-m", "--method", default="bitshave", type=str,
              help="Method to use for bit manipulation: bitshave | bitgroom | "
                   "bitset | bitmask")
@click.option("-o", "--output", default=None, type=str,
              help="Output file name")
@click.option("-D", "--debug", default=False, is_flag=True,
              help="Provide debug info")
@click.option("-P", "--pchunk", default=10000, type=int,
              help="Number of timesteps to process per iteration")
@click.argument("file", type=str)
def compress(file, analysis_file, deflate, force, conv_int, conv_float,
             ci, method, output, debug, pchunk):
    # convert the files to complete paths
    file = os.path.abspath(file)
    output = os.path.abspath(output)
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

    # check that the version matches
    version_err_msg = (
        f"Version of file: {analysis_file} does not match current version:"
        f" {CIC_FILE_FORMAT_VERSION}.  Please recalculate analysis."
    )
    try:
        version = analysis["version"]
        if version != CIC_FILE_FORMAT_VERSION:
            print(version_err_msg)
            sys.exit(0)
    except KeyError:
        print(version_err_msg)
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
            print(f"Analysed file: {analysis_input_file}, does not match "
                  f"file to be compressed: {file}")
            sys.exit(0)
    except KeyError:
        print(f"Could not find file key in analysis file: {str(analysis_file)}")
        sys.exit(0)

    # get the bit manipulation method
    if method not in ["bitshave", "bitgroom", "bitset", "bitmask"]:
        print(f"Unknown bit manipulation method: {method}")
        sys.exit(0)

    # check that we aren't going to overwrite the input with the output
    if file == output:
        print("Input and output file are the same")
        sys.exit(0)


    # open the input file
    input_ds = load_dataset(file)
    # process it, along with the analysis]
    params = {"conf_int"   : ci,
              "deflate"    : deflate,
              "method"     : method,
              "conv_int"   : conv_int,
              "conv_float" : conv_float,
              "debug"      : debug,
              "pchunk"     : pchunk}
    paramstr = ""
    for p in params:
        paramstr += f"    {p:<12}: {params[p]}\n"
    if params["debug"]:
        print(f"Processing compression on file: \n"
              f"    {file}\n"
              f"with parameters: \n"
              f"{paramstr[:-1]}")
    process(input_ds, output_ds, analysis, params)

def main():
    compress()

if __name__ == "__main__":
    main()