# coding: utf-8
"""
Usage:
    python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>] [-s <y/N>] [-w <y/N>]

Required Options:
    -i <inputpath>    The run directory of the experiment. Eventually this will be the experiment's root directory. Try to use absolute paths, for some reason this doesnt like ~ for homedirs

Optional options:
    -o <outputfile>    Prompts this program to output the gantt chart to a file instead of showing it to you via the matplotlib viewer. Be careful with this, as it can make large charts unusable
    -r <y/n>    Prompts this program to look for and utilize reservations when creating the output charts 
    -v <y/N>    verbose operation.
    -b <y/N>    Bin reservations by size
    -a <y/N>    Plot average utilization plot
    -s <y/N>    Plot bubble chart
    -w <y/N>    Windowed Gantt Chart

"""


import sys, getopt, os

# from batvis.utils import *
# from batvis.gantt import *
# from batvis.plots import *

# FIXME Stubbed imports for debugging
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
    bubble = False
    window = False
    timeline = False

    # Parse the arguments passed in
    try:
        opts, args = getopt.getopt(
            argv,
<<<<<<< HEAD:main.py
            "hi:o:r:v:b:a:s:w:t:",
=======
            "hi:o:r:v:b:a:s:w:",
>>>>>>> 170cecaea1134ed29cd9aee6b7ba19966194059a:src/batvis/main.py
            [
                "ipath=",
                "ofile=",
                "resv=",
                "verbosity=",
                "binned=",
                "average=",
                "bubble=",
                "window=",
            ],
        )
    except getopt.GetoptError:
        print(
            "Option error! See usage below:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N>] [-a <y/N>] [-s <y/N>] [-n <y/N>] [-w <y/N>] [-t <y/N>]"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "Help menu:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>] [-s <y/N>] [-n <y/N>] [-w <y/N>] [-t <y/N>]"
            )
            sys.exit(2)
        elif opt in ("-i", "--ipath"):
            if arg == "":
                print(
                    "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>] [-s <y/N>] [-n <y/N>] [-w <y/N>] [-t <y/N>]\n Please supply an input path!"
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
        elif opt in ("-s", "--bubble"):
            if arg.lower() == "y":
                bubble = True
        elif opt in ("-w", "--window"):
            if arg.lower() == "y":
                window = True
        elif opt in ("-t", "--timeline"):
            if arg.lower() == "y":
                timeline = True

    # Parse the path of the required files.
    outJobsCSV = os.path.join(inputpath, "output", "expe-out", "out_jobs.csv")

    # If no reservations are specified, process the chart normally
    if (
        not reservation
        and not binned
        and not average
        and not bubble
        and not window
        and not timeline
    ):
        with yaspin().line as sp:
            sp.text = "Plotting gantt for entire outputfile"
            plotSimpleGantt(outJobsCSV, outputfile)

    # If you're doing any combination of resv,bin, and bubble but not average
    elif (reservation or binned or bubble or window) and not average:
        iterateReservations(
            inputpath,
            outputfile,
            outJobsCSV,
            verbosity,
            binned,
            bubble,
            reservation,
            window,
        )

    # #  If you're doing any combo of resv, bin, and bubble and also average
    # elif (reservation or binned or bubble or window) and average:
    #     chartRunningAverage(inputpath, outputfile, outJobsCSV)

    #     iterateReservations(
    #         inputpath,
    #         outputfile,
    #         outJobsCSV,
    #         verbosity,
    #         binned,
    #         bubble,
    #         reservation,
    #         window,
    #     )

    # # If you only want average
    # elif average and not (reservation or binned or bubble or window):
    #     chartRunningAverage(inputpath, outputfile, outJobsCSV)

    elif timeline:
        chartTimeline(
            inputpath,
            outputfile,
            outJobsCSV,
<<<<<<< HEAD:main.py
=======
            verbosity,
            binned,
            bubble,
            reservation,
            window,
>>>>>>> 170cecaea1134ed29cd9aee6b7ba19966194059a:src/batvis/main.py
        )

    # If your options are bad
    else:
        print("Incompatible options entered! Please try again")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
