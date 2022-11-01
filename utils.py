from yaspin import yaspin
import sys, getopt, os, json
from datetime import datetime
from evalys.jobset import JobSet
from evalys.utils import cut_workload
import pandas as pd


# def dictHasKey(myDict, key):
#     """
#     Used to check whether key 'key' exists in dict 'mydict'

#     :returns: a boolean value representing whether or not the key exists.
#     """
#     if key in myDict.keys():
#         return True
#     else:
#         return False


def getMaxJobLen(totaldf):
    """
    Gets the length of the longest job in a dataframe

    :returns: the length of the longest job in the df
    """
    maxJobLen = totaldf["execution_time"].max()
    print("Maximum job length parsed as: " + str(maxJobLen))
    return maxJobLen


def dfFromCsv(outJobsCSV):
    """
    Generates a dataframe and jobset from the provided CSV file

    :returns: a dataframe from the jobset, and the jobset itself
    """
    with yaspin().line as sp:
        sp.text = "Creating jobset from out_jobs.csv"
        try:
            totaljs = JobSet.from_csv(outJobsCSV)
        except:
            print("Error! CSV File is empty!")
            sys.exit(2)
    return totaljs.df, totaljs


def binDfToJs(df):
    """
    Used to sort jobs within a DF into 3 types based on runtime and requested resources,
    then convert those dfs into jobsets.

    :returns: 3 jobsets, sorted by the resource parameters
    """
    smallDf = df.loc[
        (df["requested_number_of_resources"] <= 32) & (df["execution_time"] <= 28800)
    ]
    smallJs = JobSet.from_df(smallDf)
    longDf = df.loc[
        (df["requested_number_of_resources"] <= 32) & (df["execution_time"] > 28800)
    ]
    longJs = JobSet.from_df(longDf)
    largeDf = df.loc[(df["requested_number_of_resources"] > 32)]
    largeJs = JobSet.from_df(largeDf)
    return smallJs, longJs, largeJs


def binDf(df):
    """
    Used to sort jobs within a DF into 3 types based on runtime and requested resources and output those dataframes.
    """
    smallDf = df.loc[
        (df["requested_number_of_resources"] <= 32) & (df["execution_time"] <= 28800)
    ]
    longDf = df.loc[
        (df["requested_number_of_resources"] <= 32) & (df["execution_time"] > 28800)
    ]
    largeDf = df.loc[(df["requested_number_of_resources"] > 32)]
    return smallDf, longDf, largeDf


def getFileName(name, outPath):
    """
    Returns a filename to be used based on the provided name and output path

    :returns: the output path as a string
    """
    return os.path.join(outPath, name)


def loadConfigs(inputpath):
    """
    Parses the provided configuration files as JSON and loads them

    :returns: the two config files loaded into JSON objects
    """
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
    """
    Parses the output folder or file from the config file

    :returns: a path to be used as the output path, or a path for the output file
    """
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


def prepDf(row, totaldf, maxJobLen, allResvDf):
    """
    Using the given row, parses the jobs in a window, bins those jobs based on size,
    and concatenates them with the dataframes stored in allResvDf.

    :returns: a list of the three types of jobs, containing 3 dataframes, one for each size,
    with the details from this row appended.
    """
    # Defining reservation and window bounds
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
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
    cut_js = resetDfTimescale(cut_js, windowStartTime)
    smallDf, longDf, largeDf = binDf(cut_js["workload"])
    # smallDf = resetDfTimescale(smallDf)
    # longDf = resetDfTimescale(longDf)
    # largeDf = resetDfTimescale(largeDf)
    # print(allResvDf[0])
    if len(allResvDf[0]) == 0:
        allResvDf[0] = smallDf
        allResvDf[1] = longDf
        allResvDf[2] = largeDf
    else:
        allResvDf[0] = pd.concat([allResvDf[0], smallDf])
        allResvDf[1] = pd.concat([allResvDf[1], longDf])
        allResvDf[2] = pd.concat([allResvDf[2], longDf])

    return allResvDf


def resetDfTimescale(df, windowStartTime):
    """
    Iterates over records in a df, and sets their starting and finish times based on a zero of the windowStartTime

    :returns: The df with time data reset
    """
    for index, row in df["workload"].iterrows():
        row["starting_time"] = row["starting_time"] - windowStartTime
        row["finish_time"] = row["finish_time"] - windowStartTime
        print(row)
    return df
