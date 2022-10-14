# coding: utf-8
import matplotlib.pyplot as plt
from evalys.jobset import JobSet
import sys, getopt
import json


def main(argv):
    inputfile = ""
    outputfile = ""
    reservation = ""
    config = ""
    try:
        opts, args = getopt.getopt(
            argv, "hi:o:r:c:", ["ifile=", "ofile=", "resv=", "conf="]
        )
        #TODO I can totally parse the locations of both the job file and the input file from the root experiment directory. Do this.
    except getopt.GetoptError:
        print("main.py -i <inputfile> -o <outputfile> -r <y/n> -c <config.ini>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("main.py -i <inputfile> -o <outputfile> -r <y/n> -c <config.ini>")
            sys.exit(2)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--resv"):
            reservation = arg
        elif opt in ("-c", "--conf"):
            config = arg

    # Validate the inputs and confirm that all necessary variables have been provided before proceeding
    if inputfile == "":
        print("main.py -i <inputfile> -o <outputfile> -r <y/n> -c <config.ini>")
        sys.exit(2)
    if (reservation == "y" or reservation == "Y") and config == "":
        print("A value of -c must be provided when using -r!")
        sys.exit(2)

    # If no reservations are specified, process the chart normally
    if reservation == "" or reservation == "n":
        with open(inputfile) as f:
            if sum(1 for line in f) > 20000:
                print(
                    "Creating gantt charts can be unreliable with files larger than 20k jobs. Are you use you want to continue? (Y/n)"
                )
                cont = input()
                if cont == "Y" or cont == "y":
                    pass
                elif cont == "n":
                    sys.exit(2)
        js = JobSet.from_csv(inputfile)
        print(js.df.describe())
        # js.df.hist()
        axe = plt.subplots()
        js.gantt(axe)
        if outputfile == "":
            plt.show()
        else:
            plt.savefig(outputfile)
    elif reservation == "y" or reservation == "Y":
        #TODO I should probably run a check here to make sure that config is an .ini
        OutConfig = json.load(config)
        totaljs = JobSet.from_csv(inputfile)
        print("Reservations initialized")


if __name__ == "__main__":
    main(sys.argv[1:])
