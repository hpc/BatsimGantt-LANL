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

# import matplotlib.matplotlib.pyplot as matplotlib.pyplot
from tkinter import S
import matplotlib
matplotlib.use('MacOSX') # Uncomment this line if you're not using macos
from evalys.jobset import JobSet
from evalys.utils import cut_workload
from evalys.visu.legacy import plot_gantt_general_shape, plot_gantt # TODO I should probably pull in plot_gantt from the below instead
from evalys.visu.gantt import plot_gantt_df
import sys, getopt
import json
import os
import pandas as pd
from datetime import datetime
import time

def dictHasKey(myDict, key):
    if key in myDict.keys():
        return True
    else:
        return False


def makeReservationGantt(row, totaldf, outDir, res_bounds):
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    windowSize = 86400 # TODO Make this not hardcoded. This value is the time in seconds of the windows before and after the reservation.
    windowStartTime = reservationStartTime-windowSize
    if windowStartTime<0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime>int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())
    # reservationDf = totaldf[(totaldf["starting_time"] >= windowStartTime) & (totaldf["finish_time"] <= windowFinishTime)]
    cut_js = cut_workload(totaldf,windowStartTime, windowFinishTime)
    # TODO Extract the reservation bounds from the jobset here and insert
    plot_gantt_df(cut_js['workload'], res_bounds, title=str("Gantt for reservation starting at time "+str(reservationStartTime)+" and ending at time "+str(reservationFinishTime)+" with "+str(windowSize)+" seconds before and after the reservation"))
    if outDir == "":
        matplotlib.pyplot.show()
    else:
        matplotlib.pyplot.savefig(os.path.join(outDir))
        # matplotlib.pyplot.savefig(os.path.join(outDir, str("reservation",str(windowStartTime),"-",str(windowFinishTime))))
    sys.exit(2) # TODO Remove

def main(argv):
    inputpath = ""
    outputfile = ""
    reservation = ""

    # Parse the arguments passed in
    try:
        opts, args = getopt.getopt(argv, "hi:o:r:c:", ["ipath=", "ofile=", "resv="])
    except getopt.GetoptError:
        print("python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/n>]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/n>]")
            sys.exit(2)
        elif opt in ("-i", "--ipath"):
            inputpath = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--resv"):
            reservation = arg

    # Validate the inputs and confirm that all necessary variables have been provided before proceeding
    if inputpath == "":
        print("python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/n>]")
        sys.exit(2)

    # Parse the path of the required files.
    # TODO Eventually make this able to operate out of the root directory.
    # TODO This should be try/excepted
    # TODO I should also make an option so that this can just go to files in the local directory
    outJobsCSV = os.path.join(inputpath, "output", "expe-out", "out_jobs.csv")
    configIn = os.path.join(inputpath, "input", "config.ini")
    configOut = os.path.join(inputpath, "output", "config.ini")

    # If no reservations are specified, process the chart normally
    if reservation == "" or reservation == "n":
        with open(outJobsCSV) as f:
            if sum(1 for line in f) > 50000:
                print(
                    "Creating gantt charts can be unreliable with files larger than 20k jobs. Are you use you want to continue? (Y/n)"
                )
                cont = input()
                if cont == "Y" or cont == "y":
                    pass
                elif cont == "n":
                    sys.exit(2)
        
        js = JobSet.from_csv(outJobsCSV)
        plot_gantt(js, title='Gantt chart')
        if outputfile == "":
            matplotlib.pyplot.show()
        else:
            matplotlib.pyplot.savefig(outputfile)
    elif reservation == "y" or reservation == "Y":

        # Load the config files as a json
        with open(configIn, "r") as InFile:
            InConfig = json.load(InFile)
        with open(configOut, "r") as Infile:
            OutConfig = json.load(Infile)

        # Load reservation information from jsons
        reservationsResv1 = (
            InConfig["reservations-resv1"]
            if dictHasKey(InConfig, "reservations-resv1")
            else False
        )
        reservationsArray = reservationsResv1["reservations-array"]

        # Generate a jobset from the input CSV
        totaljs = JobSet.from_csv(outJobsCSV)
        totaldf = totaljs.df

        # make a directory to dump the output files into
        if outputfile != "":
            outDir = str(InConfig["batsched-policy"])+"-"+str(InConfig["nodes"])+datetime.now().strftime("%H:%M:%S")
            os.mkdir(outDir)
        else:
            outDir=""
        for index, row in totaldf.iterrows():
            if (row["purpose"] == "reservation"):
                makeReservationGantt(row, totaldf, outDir, totaljs.res_bounds)


if __name__ == "__main__":
    main(sys.argv[1:])
