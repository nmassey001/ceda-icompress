#! /usr/bin/env python
import click
import sys
import json
from ceda_icompress.InfoMeasures.display import (displayBitCount,
    displayBitCountVertical, displayBitInformation, displayBitPosition,
    displayColorBar, displayBitCountLegend, displayBitInfoLegend)
from ceda_icompress.InfoMeasures.keepbits import free_entropy, keepbits
import numpy as np
from ceda_icompress.CLI import CIC_FILE_FORMAT_VERSION

def display_variable(var_name, variable, vertical, info, count, reverse):
    try:
        typ = variable['type']
        bi = np.array(variable['bitinfo'])
        siz = variable['itemsize']
        sig = variable['signbit']
        man = variable['manbit']
        exp = variable['expbit']
        elements = variable['elements']

        # calculate the free entropy at 99% confidence limit
        #fe = free_entropy(elements, 0.99) * 100
        kb = keepbits(bi, man, elements, 0.99)

        print(f"    var name: {var_name}")
        print(f"        type: {typ}")

        if info:
            print("---------- Bit Information ----------")
            L = bi.size
            displayBitPosition(L, 4, sig, man, exp, reverse)
            displayBitInformation(bi, sig, man, exp, reverse)
            displayColorBar()
            displayBitInfoLegend()
        #print(f"    free entropy: {fe}")
        print(f"       keep bits: {kb}")

    except KeyError as e:
        print(f"Incomplete information in analysis file {e}")


def display_group(group, var, vertical, info, count, reverse):
    """Display a single group"""
    # get the variables from the group
    try:
        group_name = group["group_name"]
    except KeyError:
        group_name = ""

    print(f"  group name: {group_name}")

    try:
        variables = group["vars"]
    except KeyError:
        print(f"Could not find variables in group {group_name}")
    # display each individual variable
    displayed = False
    for v in variables:
        try:
            if var is None or v == var:
                display_variable(
                    v, variables[v], vertical, info, count, reverse
                )
                displayed = True
        except KeyError as e:
            print(f"Incomplete information in analysis file {e}")
            sys.exit(0)

    if not displayed:
        print(f"Variable {var} not found")

@click.command(
    help="Display the analysis output of cic_analyse.py"
)
@click.option("-v", "--var", default=None, type=str,
              help="Variable to display from analysis file")
@click.option("-g", "--group", default=None, type=str,
              help="Group to display from analysis file")
@click.option("-V", "--vertical", is_flag=True, default=False,
              help="Display analysis output vertically")
@click.option("-i", "--info", is_flag=True, default=False,
              help="Display bit information")
@click.option("-c", "--count", is_flag=True, default=False,
              help="Display bit count")
@click.option("-r", "--reverse", is_flag=True, default=False,
              help="Reverse bit positions in display")
@click.argument("analysis_file", type=str)
def display(analysis_file, var, group, vertical, info, count, reverse):
    # Load the analysis file
    try:
        fh = open(analysis_file, "r")
    except FileNotFoundError:
        print(f"Analysis file cannot be found: {analysis_file}")
        sys.exit(0)
    # Parse the analysis file
    try:
        analysis = json.load(fh)
    except Exception as e:
        print(f"Analysis file cannot be parsed: {analysis_file}, reason: {e}")
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

    # get the file name and display
    try:
        fname = analysis["file"]
        print(f"file name: {fname}")
    except KeyError:
        print(f"{analysis_file}")
    # get the groups and display
    try:
        groups = analysis["groups"]
    except KeyError:
        print(f"Could not find groups in analysis_file: {analysis_file}")
        sys.exit(0)
    
    for g in groups:
        display_group(groups[g], var, vertical, info, count, reverse)

def main():
    display()

if __name__ == "__main__":
    main()