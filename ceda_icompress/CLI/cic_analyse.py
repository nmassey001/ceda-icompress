#! /usr/bin/env python
import click
from netCDF4 import Dataset
import sys
import json

from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp
from ceda_icompress.analyse import Analyse

def load_dataset(file):
    try:
        ds = Dataset(file)
    except FileNotFoundError as e:
        print(e)
        sys.exit(0)
    except OSError as e:
        print(e)
        sys.exit(0)
    return ds

@click.command(
    help="Analyse the netCDF file to determine compression settings."
)
@click.option("-v", "--var", default=None, type=str,
              help="Variable in netCDF file to analyse")
@click.option("-g", "--group", default=None, type=str,
              help="Group in netCDF file to analyse")
@click.option("-s", "--tstart", default=None, type=int,
              help="Timestep to start analysis at")
@click.option("-e", "--tend", default=None, type=int,
              help="Timestep to end analysis at")
@click.option("-l", "--level", default=None, type=int,
              help="Level number to analyse")
@click.option("-x", "--axis", default=0, type=int,
              help="Axis number to analyse")
@click.option("-o", "--output", default=None, type=str,
              help="Output file name")
@click.option("-t", "--threads", default=1, type=int,
               help="Number of threads to use in computing the analysis")
@click.option("-D", "--debug", default=False, is_flag=True,
              help="Provide debug info")
@click.argument("file", type=str)
def analyse(file, var, group, tstart, tend, level, axis, output, threads, debug):
    # open the output file - do this before the processing so an error in 
    # created before the (long) processing time if the exceptions are caught
    if output:
        try:
            fh = open(output, "w")
        except FileExistsError:
            print(f"Output file already exists: {output}")
            sys.exit(0)
        except FileNotFoundError:
            print(f"Could not write output file: {output}")
            sys.exit(0)

    # Load the netCDF4 file from the file argument
    ds = load_dataset(file)

    # Get the groups and vars to analyse from the command line arguments
    if group is not None:
        group = group.split(",")
    if var is not None:
        var = var.split(",")

    # create the analysis object and set the operating parameters
    analysis = Analyse()
    analysis.time_start = tstart
    analysis.time_end = tend
    analysis.axis = axis
    analysis.level = level

    # number of threads to use
    analysis.threads = threads

    # debug level
    analysis.debug = debug

    # perform the analysis, on the selected groups and variables
    analysis_dict = analysis.from_dataset(ds, group, var)

    # write to file if output chosen
    if output:
        json.dump(analysis_dict, fh)
        fh.close()
        if analysis.debug:
            print(f"Output analysis file written: {output}")
    else:
        print(analysis_dict)

def main():
    analyse()

if __name__ == "__main__":
    main()