# coding: utf-8
"""
Usage:
    python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N]

Required Options:
    -i <inputpath>    The run directory of the experiment. Eventually this will be the experiment's root directory. Try to use absolute paths, for some reason this doesnt like ~ for homedirs

Optional options:
    -o <outputfile>    Prompts this program to output the gantt chart to a file instead of showing it to you via the matplotlib viewer. Be careful with this, as it can make large charts unusable
    -r <y/n>    Prompts this program to look for and utilize reservations when creating the output charts 
    -v <y/N>    verbose operation.
    -b <y/N>    Bin reservations by size

"""


import sys, getopt
import os
from utils import *
from gantt import *
from plots import *


def main(argv):
    inputpath = ""
    outputfile = ""
    reservation = False
    verbosity = False
    binned = False
    average = False

    # Parse the arguments passed in
    try:
        opts, args = getopt.getopt(
            argv,
            "hi:o:r:v:b:a:",
            ["ipath=", "ofile=", "resv=", "verbosity=", "binned=", "average="],
        )
    except getopt.GetoptError:
        print(
            "Option error! See usage below:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N>] [-a <y/N>]"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "Help menu:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>]"
            )
            sys.exit(2)
        elif opt in ("-i", "--ipath"):
            if arg == "":
                print(
                    "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>]\n Please supply an input path!"
                )
                sys.exit(2)
            else:
                inputpath = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--resv"):
            if arg.lower() == "y":
                reservation = True
        elif opt in ("-v", "--verbosity"):
            if arg.lower() == "y":
                verbosity = True
        elif opt in ("-b", "--binned"):
            if arg.lower() == "y":
                binned = True
        elif opt in ("-a", "--average"):
            if arg.lower() == "y":
                average = True

    # Parse the path of the required files.
    outJobsCSV = os.path.join(inputpath, "output", "expe-out", "out_jobs.csv")

    # If no reservations are specified, process the chart normally
    if not reservation:
        plotSimpleGantt(outJobsCSV, outputfile)

    elif reservation and not average:
        iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned)

    elif reservation and average:
        chartRunningAverage(inputpath, outputfile, outJobsCSV)

    else:
        print("Incompatible options entered! Please try again")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
