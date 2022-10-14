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

import matplotlib.pyplot as plt
from evalys.jobset import JobSet
import sys, getopt
import json
import os


def dictHasKey(myDict, key):
    if key in myDict.keys():
        return True
    else:
        return False


def main(argv):
    inputpath = ""
    outputfile = ""
    reservation = ""
    config = ""

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
    outJobsCSV = os.path.join(inputpath, "output", "expe-out", "out_jobs.csv")
    configIn = os.path.join(inputpath, "input", "config.ini")
    configOut = os.path.join(inputpath, "output", "config.ini")

    # If no reservations are specified, process the chart normally
    if reservation == "" or reservation == "n":
        with open(outJobsCSV) as f:
            if sum(1 for line in f) > 20000:
                print(
                    "Creating gantt charts can be unreliable with files larger than 20k jobs. Are you use you want to continue? (Y/n)"
                )
                cont = input()
                if cont == "Y" or cont == "y":
                    pass
                elif cont == "n":
                    sys.exit(2)
        js = JobSet.from_csv(outJobsCSV)
        print(js.df.describe())
        axe = plt.subplots()
        js.gantt(axe)
        if outputfile == "":
            plt.show()
        else:
            plt.savefig(outputfile)
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
        """for reservation in reservationsArray:
            time = reservation["time"]
            start = reservation["start"]"""

        # Generate a jobset from the input CSV
        

        totaljs = JobSet.from_csv(inputpath)

        # TODO Should I parse the CSV before or after the above? What if I use js.df to pull stuff from the dataframe directly?


if __name__ == "__main__":
    main(sys.argv[1:])
