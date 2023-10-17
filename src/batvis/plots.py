from batvis.utils import *
from batvis.gantt import *

# from utils import *
# from gantt import *

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import seaborn as sns
from evalys.jobset import JobSet

# matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def chartRunningAverage(inputpath, outputfile, outJobsCSV):
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    # TODO Unhardcode this
    clusterSize = 1490
    numberSections = 8
    windowSize = 169200

    h, m, s = InConfig["reservations-resv1"]["reservations-array"][0]["time"].split(":")
    reservationSize = int(h) * 3600 + int(m) * 60 + int(s)
    nodeHours = []
    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            dfBefore, dfAfter = getNodeHours(row, totaldf, maxJobLen, windowSize)
            if not dfBefore.empty and not dfAfter.empty:
                nodeHours.append([dfBefore, dfAfter])
    dfBeforeMaster = pd.DataFrame(
        columns=[
            "section",
            "small",
            "long",
            "large",
            "total",
        ]
    )
    dfAfterMaster = pd.DataFrame(
        columns=[
            "section",
            "small",
            "long",
            "large",
            "total",
        ]
    )
    # For each reservation that we have utilization percentages for
    # TODO Extract data, average it, and insert it into the master dataframe

    # Iterate over each section (before/after)
    for section in range(0, numberSections):

        # Create lists to hold the values of each section type at each this in time
        beforeSmallList = []
        afterSmallList = []
        beforeLongList = []
        afterLongList = []
        beforeLargeList = []
        afterLargeList = []
        beforeTotalList = []
        afterTotalList = []
        for resv in range(len(nodeHours)):
            beforeSmallList.append(nodeHours[resv][0].loc[section]["smallNodeHours"])
            afterSmallList.append(nodeHours[resv][1].loc[section]["smallNodeHours"])
            beforeLongList.append(nodeHours[resv][0].loc[section]["longNodeHours"])
            afterLongList.append(nodeHours[resv][1].loc[section]["longNodeHours"])
            beforeLargeList.append(nodeHours[resv][0].loc[section]["largeNodeHours"])
            afterLargeList.append(nodeHours[resv][1].loc[section]["largeNodeHours"])
            beforeTotalList.append(nodeHours[resv][0].loc[section]["totalNodeHours"])
            afterTotalList.append(nodeHours[resv][1].loc[section]["totalNodeHours"])
        # Calculate the average of each section type at each time
        beforeSmall = sum(beforeSmallList) / len(beforeSmallList)
        afterSmall = sum(afterSmallList) / len(afterSmallList)
        beforeLong = sum(beforeLongList) / len(beforeLongList)
        afterLong = sum(afterLongList) / len(afterLongList)
        beforeLarge = sum(beforeLargeList) / len(beforeLargeList)
        afterLarge = sum(afterLargeList) / len(afterLargeList)
        beforeTotal = sum(beforeTotalList) / len(beforeTotalList)
        afterTotal = sum(afterTotalList) / len(afterTotalList)

        # Insert the average into the master dataframe
        dfBeforeMaster.loc[section] = [
            section,
            beforeSmall / 3600,
            beforeLong / 3600,
            beforeLarge / 3600,
            beforeTotal / 3600,
        ]
        dfAfterMaster.loc[section] = [
            section,
            afterSmall / 3600,
            afterLong / 3600,
            afterLarge / 3600,
            afterTotal / 3600,
        ]
    maxNodeHours = clusterSize * ((windowSize / 3600) / numberSections)
    print("Max node hours per section: " + str(maxNodeHours))
    print(dfBeforeMaster)
    print(dfAfterMaster)
    makePercentageGraph(
        dfBeforeMaster, outDir, InConfig, maxNodeHours, "nodeHoursChartBefore"
    )
    makePercentageGraph(
        dfAfterMaster, outDir, InConfig, maxNodeHours, "nodeHoursChartAfter"
    )


def makePercentageGraph(masterDf, outDir, InConfig, maxNodeHours, name):
    """
    Charts the running average of cluster utilization over the entire experimen t
    """

    # TODO Chart the needful
    barWidth = 1

    # TODO Unhardcode this
    names = ("0", "1", "2", "3", "4", "5", "6", "7")
    plt.bar(
        masterDf["section"],
        (masterDf["small"] / maxNodeHours) * 100,
        color="b",
        width=barWidth,
        edgecolor="white",
        label="small",
    )
    plt.bar(
        masterDf["section"],
        (masterDf["long"] / maxNodeHours) * 100,
        bottom=((masterDf["small"] / maxNodeHours) * 100),
        color="g",
        width=barWidth,
        edgecolor="white",
        label="long",
    )
    plt.bar(
        masterDf["section"],
        (masterDf["large"] / maxNodeHours) * 100,
        bottom=((masterDf["small"] / maxNodeHours) * 100)
        + ((masterDf["long"] / maxNodeHours) * 100),
        color="r",
        width=barWidth,
        edgecolor="white",
        label="large",
    )
    plt.xticks(masterDf["section"], names)
    plt.xlabel("Section")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), ncol=1)

    # plt.show()

    masterDf.to_csv(
        os.path.join(
            outDir,
            "runningAverage-"
            + InConfig["batsched-policy"]
            + datetime.now().strftime("%H:%M:%S")
            + name
            + ".csv",
        )
    )

    outFileLoc = os.path.join(
        outDir,
        "runningAverage-"
        + InConfig["batsched-policy"]
        + datetime.now().strftime("%H:%M:%S")
        + name,
    )
    matplotlib.pyplot.savefig(
        outFileLoc,
        dpi=300,
    )
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + outFileLoc)


def plotBubbleChart(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots a bubble chart for each reservation based on the given parameters
    """
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    windowSize = 169200
    windowStartTime = reservationStartTime - windowSize
    if windowStartTime < 0:
        windowStartTime = 0
    windowFinishTime = reservationFinishTime + windowSize
    if windowFinishTime > int(totaldf["finish_time"].max()):
        windowFinishTime = int(totaldf["finish_time"].max())

    outFile = os.path.join(
        outDir,
        str("BUB-") + str(windowStartTime) + "-" + str(windowFinishTime),
    )

    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    # TODO Remove the bubble representing the reservation
    for index, row in totalDf.iterrows():
        if row["purpose"] == "reservation":
            totalDf.drop(labels=index, axis=0, inplace=True)
            # print("Dropped reservation at index: " + str(index))
    if checkForJobs(totalDf):
        sns.set_style("whitegrid")
        sns.set_palette("flare")
        fig, ax = matplotlib.pyplot.subplots(figsize=(12, 8))
        sns.scatterplot(
            ax=ax,
            data=totalDf,
            x="starting_time",
            y="execution_time",
            size="requested_number_of_resources",
            legend=True,
            sizes=(20, 2000),
            hue="requested_number_of_resources",
        ).set(
            title=str(
                "Reservation from  "
                + str(reservationStartTime)
                + "-"
                + str(reservationFinishTime)
                + "+-"
                + str(windowSize)
                + "S"
            ),
        )
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        ax.set_xlim(windowStartTime, windowFinishTime)

        matplotlib.pyplot.savefig(outFile, dpi=300, bbox_inches="tight")
        matplotlib.pyplot.close()
        print("\nSaved figure to: " + outFile)
        sns.set_palette("tab10")
    else:
        print(
            "Your dataset includes reservations surrounded by no jobs! Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )
