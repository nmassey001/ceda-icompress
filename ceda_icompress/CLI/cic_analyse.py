#! /usr/bin/env python
import click
from netCDF4 import Dataset
import sys
from datetime import datetime
import json
import time
from ceda_icompress.InfoMeasures.bitentropy import bitentropy
from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp

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

def get_groups(dataset, group):
    if group is not None:
        try:
            grps = [dataset.groups[g] for g in group]
        except KeyError as e:
            print(f"Group(s) not found: {group}")
            sys.exit(0)
    else:
        # get the groups
        grps = [dataset.groups[g] for g in dataset.groups]
        # append the dataset (which is derived from a group)
        grps.append(dataset)
    return grps

def get_vars(grp, var):
    if var is not None:
        try:
            vars = [grp.variables[v] for v in var]
        except KeyError as e:
            print(f"Variable(s) not found: {var} in group: {grp.name}")
            sys.exit(0)
    else:
        vars = [grp.variables[v] for v in grp.variables]
    return vars

def analyse_var(var, tstart, tend):
    """Analyse the variable to get the bitcount and the bitinformation"""
    # form the index / slice
    s = []
    var_dict = {}

    for d in var.dimensions:
        if d == "time" or d == "t":
            if tstart is not None:
                ts = tstart
            else:
                ts = 0
            if tend is not None:
                te = tend
            else:
                te = -1
            s.append(slice(ts,te,1))
        else:
            s.append(slice(0,-1,1))
    # get the data from the slice
    data = var[s]
    print(f"Analysing variable with shape: {data.shape}")
    # get the bit entropy
    # be = bitentropy(data)
    # print(be)
    # get the bit information
    st = time.time()
    bi = bitinformation(data)
    ed = time.time()
    print("TIME: ", ed-st)
    # get the sign, exponent and mantissa bits
    sig, man, exp = getsigmanexp(data.dtype)
    var_dict["type"] = data.dtype.name
    var_dict["itemsize"] = data.dtype.itemsize          # bits
    var_dict["byteorder"] = data.dtype.byteorder
    var_dict["signbit"] = sig
    var_dict["manbit"] = man
    var_dict["expbit"] = exp
    var_dict["bitinfo"] = bi.tolist()
    return var_dict


@click.command(
    help="Analyse the netCDF file to determine compression settings."
)
@click.option("-v", "--var", default=None, type=str,
              help="Variable in netCDF file to analyse")
@click.option("-g", "--group", default=None, type=str,
              help="Group in netCDF file to analyse")
@click.option("-t", "--tstart", default=None, type=int,
              help="Timestep to start analysis at")
@click.option("-e", "--tend", default=None, type=int,
              help="Timestep to end analysis at")
@click.option("-o", "--output", default=None, type=str,
              help="Output file name")
@click.argument("file", type=str)
def analyse(file, var, group, tstart, tend, output):
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
    if group is not None:
        group = group.split(",")
    if var is not None:
        var = var.split(",")
    grps = get_groups(ds, group)

    analysis_dict = {"Analysis" : "BitInformation",
                     "date" : datetime.now().isoformat(),
                     "file" : file,
                     "groups" : {}}
    for g in grps:
        grp_dict = {"vars" : {}}
        vars = get_vars(g, var)
        for v in vars:
            var_dict = analyse_var(v, tstart, tend)
            grp_dict["vars"][v.name] = var_dict
        analysis_dict["groups"][g.name] = grp_dict
    
    # write to file
    if output:
        json.dump(analysis_dict, fh)
        fh.close()
        print(f"Output analysis file written {output}")
    else:
        print(analysis_dict)

def main():
    analyse()

if __name__ == "__main__":
    main()