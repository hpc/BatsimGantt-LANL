# coding: utf-8
"""
Usage:
    python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/n>]

Required Options:
    -i <inputpath>    The run directory of the experiment. Eventually this will be the experiment's root directory. Try to use absolute paths, for some reason this doesnt like ~ for homedirs

Optional options:
    -o <outputfile>    Prompts this program to output the gantt chart to a file instead of showing it to you via the matplotlib viewer. Be careful with this, as it can make large charts unusable
    -r <y/n>    Prompts this program to look for and utilize reservations when creating the output charts 

"""

import matplotlib

matplotlib.use("MacOSX")  # Comment this line if you're not using macos
from evalys.jobset import JobSet
from evalys.utils import cut_workload
from evalys.visu.legacy import (
    plot_gantt,
)  # TODO I should probably pull in plot_gantt from the below instead
from evalys.visu.gantt import plot_gantt_df
import sys, getopt
import json
import os
from datetime import datetime
from yaspin import yaspin


def dictHasKey(myDict, key):
    if key in myDict.keys():
        return True
    else:
        return False


def plotReservationGantt(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
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

    smallDf, longDf, largeDf = binDf(cut_js)
    outPath = os.path.join(
        outDir, str("BIN-" + str(windowStartTime) + str(windowFinishTime))
    )
    os.mkdir(outPath)
    saveDfPlot(smallDf, getFileName("smallDf", outPath))
    saveDfPlot(longDf, getFileName("longDf", outPath))
    saveDfPlot(largeDf, getFileName("largeDf", outPath))


def binDf(df):
    smallDf = df.loc[
        (df["requested_resources"] <= 32) & (df["execution_time"] <= 28800)
    ]
    longDf = df.loc[(df["requested_resources"] <= 32) & (df["execution_time"] > 28800)]
    largeDf = df.loc[(df["requested_resources"] > 32)]
    return smallDf, longDf, largeDf


def saveDfPlot(df, outfile):
    df.plot(with_details=True)
    matplotlib.pyplot.savefig(
        outfile,
        dpi=1000,
    )
    matplotlib.pyplot.close()


def getFileName(name, outPath):
    return os.path.join(outPath, name)


def loadConfigs(inputpath):
    configIn = os.path.join(inputpath, "input", "config.ini")
    configOut = os.path.join(inputpath, "output", "config.ini")
    with yaspin().line as sp:
        sp.text = "Loading config files as JSON"
        try:
            with open(configIn, "r") as InFile:
                InConfig = json.load(InFile)
            with open(configOut, "r") as Infile:
                OutConfig = json.load(Infile)
        except:
            print(
                "Error! Config files not found! Make sure you're starting from the Run_1 directory."
            )
            sys.exit(2)
        return InConfig, OutConfig


def getOutputDir(InConfig, outputfile):
    with yaspin().line as sp:
        sp.text = "Determining output folder"
        folderNameOut = (
            str(InConfig["batsched-policy"])
            + "-"
            + str(InConfig["nodes"])
            + datetime.now().strftime("%H:%M:%S")
        )
        if outputfile == "":
            outDir = folderNameOut
        else:
            outDir = os.path.join(outputfile, folderNameOut)
    os.mkdir(outDir)
    return outDir


def dfFromCsv(outJobsCSV):
    with yaspin().line as sp:
        sp.text = "Creating jobset from out_jobs.csv"
        try:
            totaljs = JobSet.from_csv(outJobsCSV)
        except:
            print("Error! CSV File is empty!")
            sys.exit(2)
    return totaljs.df, totaljs


def getMaxJobLen(totaldf):
    maxJobLen = totaldf["execution_time"].max()
    print("Maximum job length parsed as: " + str(maxJobLen))
    return maxJobLen


def iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned=False):
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
                try:
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
                except Exception as e:
                    print(e)


def main(argv):
    inputpath = ""
    outputfile = ""
    reservation = False
    verbosity = False
    binned = False

    # Parse the arguments passed in
    try:
        opts, args = getopt.getopt(
            argv, "hi:o:r:v:", ["ipath=", "ofile=", "resv=", "verbosity=", "binned="]
        )
    except getopt.GetoptError:
        print(
            "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N]"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N]"
            )
            sys.exit(2)
        elif opt in ("-i", "--ipath"):
            if arg == "":
                print(
                    "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N]"
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

    # Parse the path of the required files.
    # TODO Eventually make this able to operate out of the root directory.
    # TODO This should be try/excepted
    # TODO I should also make an option so that this can just go to files in the local directory
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

    elif reservation:
        iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned)

    else:
        print("Incompatible options entered! Please try again")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
