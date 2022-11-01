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

import matplotlib

matplotlib.use("MacOSX")  # Comment this line if you're not using macos
from evalys.jobset import JobSet
from evalys.utils import cut_workload
from evalys.visu.legacy import (
    plot_gantt,
)
from evalys.visu.gantt import plot_gantt_df
import sys, getopt
import json
import os
from utils import *
from datetime import datetime
from yaspin import yaspin
import pandas as pd


def plotReservationGantt(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots a standard gantt reservation, without binning by job size.
    This produces an output folder containing one image for each reservation.
    """
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    if verbosity == True:
        print(
            "\nReservation start: "
            + str(reservationStartTime)
            + "\nReservation finish: "
            + str(reservationFinishTime)
            + "\nReservationExecTime: "
            + str(reservationExecTime)
            + "\nReservationInterval: "
            + str(reservationInterval)
        )
    windowSize = 169200
    windowStartTime = reservationStartTime - windowSize
    if windowStartTime < 0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime > int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())
    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )
    if verbosity == True:
        print(cut_js)
    # FIXME This could use saveDfPlot
    plot_gantt_df(
        cut_js["workload"],
        res_bounds,
        windowStartTime,
        windowFinishTime,
        title=str(
            "Reservation from  "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
            + "+-"
            + str(windowSize)
            + "S"
        ),
        resvStart=reservationStartTime,
        resvExecTime=reservationExecTime,
        resvNodes=reservationInterval,
    )
    matplotlib.pyplot.savefig(
        os.path.join(
            outDir,
            str("reservation") + str(windowStartTime) + "-" + str(windowFinishTime),
        ),
        dpi=1000,
    )
    matplotlib.pyplot.close()
    print(
        "\nSaved figure to: "
        + os.path.join(
            outDir,
            str("reservation") + str(windowStartTime) + "-" + str(windowFinishTime),
        )
    )


def plotBinnedGanttReservations(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots gantt charts for reservations, binning into 3 different job types based on runtime and requested resources.
    """
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    if verbosity == True:
        print(
            "\nReservation start: "
            + str(reservationStartTime)
            + "\nReservation finish: "
            + str(reservationFinishTime)
            + "\nReservationExecTime: "
            + str(reservationExecTime)
            + "\nReservationInterval: "
            + str(reservationInterval)
        )
    windowSize = 169200
    windowStartTime = reservationStartTime - windowSize
    if windowStartTime < 0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime > int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())
    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )
    if verbosity == True:
        print(cut_js)
    try:
        smallJs, longJs, largeJs = binDfToJs(cut_js["workload"])
        saveDfPlot(
            smallJs,
            getFileName(
                str("BIN-" + str(windowStartTime) + "-" + str(windowFinishTime)), outDir
            ),
            reservationStartTime,
            reservationExecTime,
            reservationInterval,
            longJs=longJs,
            largeJs=largeJs,
            windowStartTime=windowStartTime,
            windowFinishtime=windowFinishTime,
            binned=True,
        )
    except ValueError:
        print(
            "WARNING: Your dataset contains reservations that are not surrounded by any jobs. Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )


def saveDfPlot(
    js,
    outfile,
    reservationStartTime,
    reservationExecTime,
    reservationInterval,
    longJs=None,
    largeJs=None,
    windowStartTime=None,
    windowFinishtime=None,
    binned=False,
):
    """
    Saves a plot from a jobset based on the given parameters.
    """
    js.plot(
        with_gantt=True,
        longJs=longJs,
        largeJs=largeJs,
        reservationStart=reservationStartTime,
        reservationExec=reservationExecTime,
        reservationNodes=reservationInterval,
        windowStartTime=windowStartTime,
        windowFinishTime=windowFinishtime,
        binned=binned,
    )
    matplotlib.pyplot.savefig(
        outfile,
        dpi=300,
    )
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + outfile)


def iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned=False):
    """
    Iterates over reservations and plots them based on whether or not they're binned
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            with yaspin().line as sp:
                sp.text = (
                    "Plotting gantt chart for reservation from:"
                    + str(row["starting_time"])
                    + " to "
                    + str(row["finish_time"])
                )
                # try:
                if not binned:
                    plotReservationGantt(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif binned:
                    plotBinnedGanttReservations(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                # except Exception as e:
                #     print(e)


def chartRunningAverage(
    inputpath,
    outputfile,
    outJobsCSV,
):
    """
    Charts the running average of utilization
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    smallDf = []
    longDf = []
    largeDf = []
    allResvDf = [smallDf, longDf, largeDf]

    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            with yaspin().line as sp:
                sp.text = (
                    "Plotting gantt chart for reservation from:"
                    + str(row["starting_time"])
                    + " to "
                    + str(row["finish_time"])
                )
                #! Catch empty DFs here
                allresvDf = prepDf(row, totaldf, maxJobLen, allResvDf)
                print(
                    "Reservation from: "
                    + str(row["starting_time"])
                    + "-"
                    + str(row["finish_time"])
                    + " added to df."
                )
    smallJs = JobSet.from_df(allResvDf[0])
    longJs = JobSet.from_df(allResvDf[1])
    largeJs = JobSet.from_df(allResvDf[2])
    # TODO Unhardcode the window start and finish times
    # ! THIS IS WRONG AND DOES NOT PLOT AVERAGE RIGHT NOW. THIS IS ONLY AN OUTLINE
    smallJs.plot(
        with_gantt=False,
        longJs=longJs,
        largeJs=largeJs,
        average=True,
    )
    outfile = getFileName(str("testing"), outDir)
    matplotlib.pyplot.savefig(
        outfile,
        dpi=300,
    )
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + outfile)


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
        with open(outJobsCSV) as f:
            if sum(1 for line in f) > 70000:
                print(
                    "Creating gantt charts can be unreliable with files larger than 70k jobs. Are you use you want to continue? (Y/n)"
                )
                cont = input()
                if cont == "Y" or cont == "y":
                    pass
                elif cont == "n":
                    sys.exit(2)

        js = JobSet.from_csv(outJobsCSV)
        plot_gantt(js, title="Gantt chart")
        if outputfile == "":
            matplotlib.pyplot.show()
        else:
            matplotlib.pyplot.savefig(outputfile)

    elif reservation and not average:
        iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned)

    elif reservation and average:
        chartRunningAverage(inputpath, outputfile, outJobsCSV)

    else:
        print("Incompatible options entered! Please try again")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
