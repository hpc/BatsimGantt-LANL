# from batvis.utils import *
# from batvis.gantt import *

from utils import *
from gantt import *

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import seaborn as sns
from evalys.jobset import JobSet

# matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def chartRunningAverage(inputpath, outputfile, outJobsCSV):
    """
    Charts the running average of cluster utilization over the entire experimen t
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    windowSize = 169200
    h, m, s = InConfig["reservations-resv1"]["reservations-array"][0]["time"].split(":")
    reservationSize = int(h) * 3600 + int(m) * 60 + int(s)
    utilPercentages = []
    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            dfBefore, dfAfter = getPercentageUtilization(
                row, totaldf, maxJobLen, windowSize
            )
            utilPercentages.append([dfBefore, dfAfter])
    dfBeforeMaster = pd.DataFrame(
        columns=[
            "section",
            "small",
            # "smallResources",
            "long",
            # "longResources",
            "large",
            # "largeResources",
            "total",
            # "totalResources",
        ]
    )
    dfAfterMaster = pd.DataFrame(
        columns=[
            "section",
            "small",
            # "smallResources",
            "long",
            # "longResources",
            "large",
            # "largeResources",
            "total",
            # "totalResources",
        ]
    )
    # For each reservation that we have utilization percentages for
    # TODO Extract data, average it, and insert it into the master dataframe

    # Iterate over each section (before/after)
    for section in range(0, 8):
        # Create lists to hold the values of each section type at each this in time
        beforeSmallList = []
        afterSmallList = []
        beforeLongList = []
        afterLongList = []
        beforeLargeList = []
        afterLargeList = []
        beforeTotalList = []
        afterTotalList = []
        for resv in range(len(utilPercentages)):
            beforeSmallList.append(utilPercentages[resv][0].loc[section]["small"])
            afterSmallList.append(utilPercentages[resv][1].loc[section]["small"])
            beforeLongList.append(utilPercentages[resv][0].loc[section]["long"])
            afterLongList.append(utilPercentages[resv][1].loc[section]["long"])
            beforeLargeList.append(utilPercentages[resv][0].loc[section]["large"])
            afterLargeList.append(utilPercentages[resv][1].loc[section]["large"])
            beforeTotalList.append(utilPercentages[resv][0].loc[section]["total"])
            afterTotalList.append(utilPercentages[resv][1].loc[section]["total"])
        # Calculate the average of each section type at each time
        beforeSmall = sum(beforeSmallList) / len(beforeSmallList)
        afterSmall = sum(afterSmallList) / len(afterSmallList)
        beforeLong = sum(beforeLongList) / len(beforeLongList)
        afterLong = sum(afterLongList) / len(afterLongList)
        beforeLarge = sum(beforeLargeList) / len(beforeLargeList)
        afterLarge = sum(afterLargeList) / len(afterLargeList)
        beforeTotal = sum(beforeTotalList) / len(beforeTotalList)
        afterTotal = sum(afterTotalList) / len(afterTotalList)
        # Convert each number into a percentage
        beforeSmall = (beforeSmall / beforeTotal) * 100
        afterSmall = (afterSmall / afterTotal) * 100
        beforeLong = (beforeLong / beforeTotal) * 100
        afterLong = (afterLong / afterTotal) * 100
        beforeLarge = (beforeLarge / beforeTotal) * 100
        afterLarge = (afterLarge / afterTotal) * 100

        # Insert the average into the master dataframe
        dfBeforeMaster.loc[section] = [
            section,
            beforeSmall,
            # beforeSmall * reservationSize,
            beforeLong,
            # beforeLong * reservationSize,
            beforeLarge,
            # beforeLarge * reservationSize,
            beforeTotal,
            # beforeTotal * reservationSize,
        ]
        dfAfterMaster.loc[section] = [
            section,
            afterSmall,
            # afterSmall * reservationSize,
            afterLong,
            # afterLong * reservationSize,
            afterLarge,
            # afterLarge * reservationSize,
            afterTotal,
            # afterTotal * reservationSize,
        ]
    overallSmallCount, overallLongCount, overallLargeCount = getTotalUtilizations(
        totaldf
    )
    totalCount = overallSmallCount + overallLongCount + overallLargeCount
    overallSmall = (overallSmallCount / totalCount) * 100
    overallLong = (overallLongCount / totalCount) * 100
    overallLarge = (overallLargeCount / totalCount) * 100
    print("Overall small: " + str(overallSmall))
    print("Overall long: " + str(overallLong))
    print("Overall large: " + str(overallLarge))
    print("Job counts by type per section before reservation")
    print(dfBeforeMaster)
    print("Job counts by type per section after reservation")
    print(dfAfterMaster)

    # TODO Chart the needful
    barWidth = 1
    names = ("0", "1", "2", "3", "4", "5", "6", "7")
    plt.bar(
        dfBeforeMaster["section"],
        dfBeforeMaster["small"],
        color="b",
        width=barWidth,
        edgecolor="white",
        label="small",
    )
    plt.bar(
        dfBeforeMaster["section"],
        dfBeforeMaster["long"],
        bottom=dfBeforeMaster["small"],
        color="g",
        width=barWidth,
        edgecolor="white",
        label="long",
    )
    plt.bar(
        dfBeforeMaster["section"],
        dfBeforeMaster["large"],
        bottom=dfBeforeMaster["small"] + dfBeforeMaster["long"],
        color="r",
        width=barWidth,
        edgecolor="white",
        label="large",
    )
    plt.xticks(dfBeforeMaster["section"], names)
    plt.xlabel("Section")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), ncol=1)

    plt.show()

    # outFileLoc = os.path.join(
    #     outDir,
    #     "runningAverage-"
    #     + InConfig["batsched-policy"]
    #     + datetime.now().strftime("%H:%M:%S"),
    # )
    # matplotlib.pyplot.savefig(
    #     outFileLoc,
    #     dpi=300,
    # )
    # matplotlib.pyplot.close()
    # print("\nSaved figure to: " + outFileLoc)


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
