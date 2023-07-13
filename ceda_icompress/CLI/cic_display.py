#! /usr/bin/env python
import click
import sys
import json
from ceda_icompress.InfoMeasures.display import (displayBitCount,
    displayBitCountVertical, displayBitInformation, displayBitPosition,
    displayColorBar, displayBitCountLegend)
import numpy as np

def display_variable(variable, vertical, info, count, reverse):
    try:
        typ = variable['type']
        bc = np.array(variable['bitcount'])
        bi = np.array(variable['bitinfo'])
        siz = variable['itemsize']
        sig = variable['signbit']
        man = variable['manbit']
        exp = variable['expbit']

        print(f"    var name: {variable['var_name']}")
        print(f"        type: {typ}")
        # display the count
        if count:
            print("------------- Bit count -------------")
            # get the max size to inform the width
            X = np.max(bc)
            W = int(np.log10(X)+2)
            L = bc.size
            if vertical:
                displayBitCountVertical(bc, sig, man, exp, siz, W, reverse)
            else:
                displayBitPosition(L, W, reverse)
                displayBitCount(bc, sig, man, exp, siz, W, reverse)
            displayBitCountLegend()

        if info:
            print("---------- Bit Information ----------")
            L = bi.size
            displayBitPosition(L, 3, reverse)
            displayBitInformation(bi, reverse)
            displayColorBar()

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
        variables = group["variables"]
    except KeyError:
        print(f"Could not find variables in group {group_name}")
    # display each individual variable
    displayed = False
    for v in variables:
        try:
            if var is None or v['var_name'] == var:
                display_variable(v, vertical, info, count, reverse)
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
        display_group(g, var, vertical, info, count, reverse)

def main():
    display()

if __name__ == "__main__":
    main()