#! /usr/bin/env python
import click
from netCDF4 import Dataset
import sys
import json
import os.path
from ceda_icompress.CLI.cic_analyse import load_dataset

from ceda_icompress.CLI import CIC_FILE_FORMAT_VERSION

from ceda_icompress.compress import Compress

COMPRESSION = 'zlib'

def load_analysis(analysis_file, input_file_name, force):
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

    # check that the name of the file in the analysis file matches the name of
    # the input file
    try:
        analysis_input_file = analysis["file"]
        if analysis_input_file != input_file_name and not force:
            print(f"Analysed file: {analysis_input_file}, does not match "
                  f"file to be compressed: {input_file_name}")
            sys.exit(0)
    except KeyError:
        print(f"Could not find file key in analysis file: {str(analysis_file)}")
        sys.exit(0)

    return analysis


def open_output_dataset(output, deflate):
    if output is None:
        print("Output file name not supplied")
        sys.exit(0)
    else:
        try:
            output_ds = Dataset(output, "w", deflate=deflate, format="NETCDF4")
        except Exception as e:
            print(f"Could not open output file {str(output)}, reason: {e}")
            sys.exit(0)
    return output_ds


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
    # open the input file - convert to absolute path first
    file = os.path.abspath(file)
    input_ds = load_dataset(file)

    # open the output file - do this before the processing so an error in 
    # created before the (long) processing time if the exceptions are caught
    output = os.path.abspath(output)
    output_ds = open_output_dataset(output, deflate)

    # check the bit manipulation method
    if method not in ["bitshave", "bitgroom", "bitset", "bitmask"]:
        print(f"Unknown bit manipulation method: {method}")
        sys.exit(0)

    # check that we aren't going to overwrite the input with the output
    if file == output:
        print("Input and output file are the same")
        sys.exit(0)

    # create the compression object
    process = Compress()

    # Load the analysis file
    process.analysis = load_analysis(analysis_file, file, force)

    # process it, according to the analysis
    process.ci = ci
    process.deflate = deflate
    process.method = method
    process.conv_int = conv_int
    process.conv_float = conv_float
    process.debug = debug
    process.pchunk = pchunk

    process.compress_dataset(input_ds, output_ds)

    # close the files to finish
    input_ds.close()
    output_ds.close()

def main():
    compress()

if __name__ == "__main__":
    main()