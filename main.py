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
matplotlib.use('MacOSX') # Comment this line if you're not using macos
from evalys.jobset import JobSet
from evalys.utils import cut_workload
from evalys.visu.legacy import plot_gantt # TODO I should probably pull in plot_gantt from the below instead
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


def plotReservationGantt(row, totaldf, outDir, res_bounds):
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    windowSize = 169200 # TODO Make this not hardcoded. This value is the time in seconds of the windows before and after the reservation.
    windowStartTime = reservationStartTime-windowSize
    if windowStartTime<0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime>int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())
    cut_js = cut_workload(totaldf,windowStartTime, windowFinishTime) # This is what results in the final crop of the images, it does some cropping of jobs IIRC
    plot_gantt_df(cut_js['workload'], res_bounds, title=str("Reservation from  "+str(reservationStartTime)+"-"+str(reservationFinishTime)+"+-"+str(windowSize)+"S"), resvStart=reservationStartTime,resvExecTime=reservationExecTime,resvNodes=reservationInterval)
    matplotlib.pyplot.savefig(os.path.join(outDir, str("reservation")+str(windowStartTime)+"-"+str(windowFinishTime)), dpi=1000)
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + os.path.join(outDir, str("reservation")+str(windowStartTime)+"-"+str(windowFinishTime)))

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
        plot_gantt(js, title='Gantt chart')
        if outputfile == "":
            matplotlib.pyplot.show()
        else:
            matplotlib.pyplot.savefig(outputfile)

    elif reservation == "y" or reservation == "Y":
        with yaspin().line as sp:
            sp.text = "Loading config files as JSON"
            try:
                with open(configIn, "r") as InFile:
                    InConfig = json.load(InFile)
                with open(configOut, "r") as Infile:
                    OutConfig = json.load(Infile)
            except:
                print("Error! Config files not found! Make sure you're starting from the Run_1 directory.")
                sys.exit(2)
        with yaspin().line as sp:
            sp.text = "Determining output folder"
            folderNameOut = str(InConfig["batsched-policy"])+"-"+str(InConfig["nodes"])+datetime.now().strftime("%H:%M:%S")
            if (outputfile == ""):
                outDir = folderNameOut
            else:
                outDir = os.path.join (outputfile, folderNameOut)
        with yaspin().line as sp:
            sp.text = "Creating jobset from out_jobs.csv"
            try:
                totaljs = JobSet.from_csv(outJobsCSV)
            except:
                print("Error! CSV File is empty!")
                sys.exit(2)
            totaldf = totaljs.df
        os.mkdir(outDir)
        for index, row in totaldf.iterrows():
            if (row["purpose"] == "reservation"):
                with yaspin().line as sp:
                    sp.text = "Plotting gantt chart for reservation from:"+str(row["starting_time"])+" to "+str(row["finish_time"])
                    plotReservationGantt(row, totaldf, outDir, totaljs.res_bounds)


if __name__ == "__main__":
    main(sys.argv[1:])
