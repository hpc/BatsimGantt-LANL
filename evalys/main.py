# coding: utf-8
import matplotlib.pyplot as plt
from evalys.jobset import JobSet
import sys, getopt


def main(argv):
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("test.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("test.py -i <inputfile> -o <outputfile>")
            sys.exit(2)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    if inputfile == "":
        print("test.py -i <inputfile> -o <outputfile>")
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


if __name__ == "__main__":
    main(sys.argv[1:])
