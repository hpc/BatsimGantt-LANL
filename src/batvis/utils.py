from yaspin import yaspin
import sys, os, json
from datetime import datetime
from evalys.jobset import JobSet
from evalys.utils import cut_workload
import pandas as pd


def getMaxJobLen(totaldf):
    """
    Gets the length of the longest job in a dataframe

    :returns: the length of the longest job in the df
    """
    maxJobLen = totaldf["execution_time"].max()
    # print("Maximum job length parsed as: " + str(maxJobLen))
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


def getUtil(row, totaldf, outDir, res_bounds, maxJobLen):
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
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
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    totalDf = resetDfTimescale(totalDf, windowStartTime)
    for index, row in totalDf.iterrows():
        if row["purpose"] == "reservation":
            totalDf.drop(labels=index, axis=0, inplace=True)
    smallJs, longJs, largeJs = binDfToJs(totalDf)
    return smallJs.utilisation, longJs.utilisation, largeJs.utilisation


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
            + "-"
            + datetime.now().strftime("%H:%M:%S")
        )
        if outputfile == "":
            outDir = folderNameOut
        else:
            outDir = os.path.join(outputfile, folderNameOut)
    os.mkdir(outDir)
    return outDir


def prepDf(row, totaldf, maxJobLen, allResvDf, n):
    """
    Using the given row, parses the jobs in a window, bins those jobs based on size,
    and concatenates them with the dataframes stored in allResvDf.

    :returns: a list of the three types of jobs, containing 3 dataframes, one for each size,
    with the details from this row appended.
    """
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
    cut_js = cut_workload(totaldf, windowStartTime, windowFinishTime)
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    for index, row in totalDf.iterrows():
        if row["purpose"] == "reservation":
            totalDf.drop(labels=index, axis=0, inplace=True)
    if not checkForJobs(totalDf):
        print(
            "Your dataset includes reservations surrounded by no jobs! Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )
        return None, True, n
    smallDf, longDf, largeDf = binDf(totalDf)
    smallDf = resetDfTimescale(smallDf, windowStartTime)
    longDf = resetDfTimescale(longDf, windowStartTime)
    largeDf = resetDfTimescale(largeDf, windowStartTime)

    if allResvDf[0].empty and allResvDf[1].empty and allResvDf[2].empty:
        allResvDf[0] = smallDf
        allResvDf[1] = longDf
        allResvDf[2] = largeDf
    else:
        allResvDf[0] = pd.concat([allResvDf[0], smallDf])
        allResvDf[1] = pd.concat([allResvDf[1], longDf])
        allResvDf[2] = pd.concat([allResvDf[2], longDf])
    print(
        "Window surrounding reservation from: "
        + str(row["starting_time"])
        + "-"
        + str(row["finish_time"])
        + " added to df."
    )
    n += 1
    # The windowstart and finish times below assume a consistent reservation size
    return allResvDf, False, n


def resetDfTimescale(df, windowStartTime):
    """
    Iterates over records in a df, and sets their starting and finish times based on a zero of the windowStartTime

    :returns: The df with time data reset
    """
    for index in df.index:
        df.loc[index, "starting_time"] = (
            df.loc[index, "starting_time"] - windowStartTime
        )
        df.loc[index, "finish_time"] = df.loc[index, "finish_time"] - windowStartTime
        df.loc[index, "submission_time"] = (
            df.loc[index, "submission_time"] - windowStartTime
        )
    return df


def checkForJobs(df):
    """
    Checks for jobs aside from reservations within a dataframe
    """
    for index, row in df.iterrows():
        if row["purpose"] == "job":
            return True


# TODO The resources problem needs to be solved better
def getPercentageUtilization(row, totaldf, maxJobLen, windowSize):
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    windowStartTime = reservationStartTime - windowSize
    if windowStartTime < 0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime > int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())
    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])

    sectionSize = windowSize / 8
    dfBefore = pd.DataFrame(
        columns=[
            "section",
            "small",
            "smallResources",
            "long",
            "longResources",
            "large",
            "largeResources",
            "total",
            "totalResources",
        ]
    )
    dfBefore.set_index("section")
    for i in range(0, 8):
        smallCount = 0
        smallResources = 0
        longCount = 0
        longResources = 0
        largeCount = 0
        largeResources = 0
        start = windowStartTime + sectionSize * i
        end = start + sectionSize
        for index, row in totalDf.iterrows():
            if row["purpose"] == "job":
                if (
                    (start <= row["starting_time"] <= end)
                    or (start <= row["finish_time"] <= end)
                    or ((row["starting_time"] <= start) and (end <= row["finish_time"]))
                ):
                    if (row["requested_number_of_resources"] <= 32) and (
                        row["execution_time"] <= 28800
                    ):
                        smallCount += 1
                        smallResources += row["requested_number_of_resources"]
                    elif (row["requested_number_of_resources"] <= 32) and (
                        row["execution_time"] > 28800
                    ):
                        longCount += 1
                        longResources += row["requested_number_of_resources"]
                    elif row["requested_number_of_resources"] > 32:
                        largeCount += 1
                        largeResources += row["requested_number_of_resources"]
        dfBefore.loc[i] = [
            i,
            smallCount,
            smallResources,
            longCount,
            longResources,
            largeCount,
            largeResources,
            smallCount + longCount + largeCount,
            smallResources + longResources + largeResources,
        ]
    dfAfter = pd.DataFrame(
        columns=[
            "section",
            "small",
            "smallResources",
            "long",
            "longResources",
            "large",
            "largeResources",
            "total",
            "totalResources",
        ]
    )
    dfAfter.set_index("section")
    for i in range(0, 8):
        smallCount = 0
        smallResources = 0
        longCount = 0
        longResources = 0
        largeCount = 0
        largeResources = 0
        start = reservationFinishTime + sectionSize * i
        end = start + sectionSize
        for index, row in totalDf.iterrows():
            if row["purpose"] == "job":
                if (
                    (start <= row["starting_time"] <= end)
                    or (start <= row["finish_time"] <= end)
                    or ((row["starting_time"] <= start) and (end <= row["finish_time"]))
                ):
                    if (row["requested_number_of_resources"] <= 32) and (
                        row["execution_time"] <= 28800
                    ):
                        smallCount += 1
                        smallResources += row["requested_number_of_resources"]
                    elif (row["requested_number_of_resources"] <= 32) and (
                        row["execution_time"] > 28800
                    ):
                        longCount += 1
                        longResources += row["requested_number_of_resources"]
                    elif row["requested_number_of_resources"] > 32:
                        largeCount += 1
                        largeResources += row["requested_number_of_resources"]
        dfAfter.loc[i] = [
            i,
            smallCount,
            smallResources,
            longCount,
            longResources,
            largeCount,
            largeResources,
            smallCount + longCount + largeCount,
            smallResources + longResources + largeResources,
        ]
    return dfBefore, dfAfter


def getTotalUtilizations(totaldf):
    overallSmallCount = 0
    overallSmallResources = 0
    overallLongCount = 0
    overallLongResources = 0
    overallLargeCount = 0
    overallLargeResources = 0
    for index, row in totaldf.iterrows():
        if row["purpose"] == "job":
            if (row["requested_number_of_resources"] <= 32) and (
                row["execution_time"] <= 28800
            ):
                overallSmallCount += 1
                overallSmallResources += row["requested_number_of_resources"]
            elif (row["requested_number_of_resources"] <= 32) and (
                row["execution_time"] > 28800
            ):
                overallLongCount += 1
                overallLongResources += row["requested_number_of_resources"]
            elif row["requested_number_of_resources"] > 32:
                overallLargeCount += 1
                overallLargeResources += row["requested_number_of_resources"]
    return overallSmallCount, overallLongCount, overallLargeCount
