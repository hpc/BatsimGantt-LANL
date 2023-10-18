from utils import *
from gantt import *
import matplotlib
import seaborn as sns
from evalys.jobset import JobSet

matplotlib.use("MacOSX")  # Comment this line if you're not using macos


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

    smallDf = pd.DataFrame()
    longDf = pd.DataFrame()
    largeDf = pd.DataFrame()
    allResvDf = [smallDf, longDf, largeDf]

    n = 0
    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            tempResvDf, empty, n = prepDf(row, totaldf, maxJobLen, allResvDf, n)
            if empty == False:
                allResvDf = tempResvDf
    smallJs = JobSet.from_df(allResvDf[0])
    longJs = JobSet.from_df(allResvDf[1])
    largeJs = JobSet.from_df(allResvDf[2])
    smallJs.plot(
        with_gantt=False,
        longJs=longJs,
        largeJs=largeJs,
        average=True,
        divisor=n,
        xAxisTermination=2 * windowSize + reservationSize,
        reservationStart=windowSize,
        reservationExec=reservationSize,
    )
    outFileLoc = os.path.join(
        outDir,
        "runningAverage-"
        + InConfig["batsched-policy"]
        + datetime.now().strftime("%H:%M:%S"),
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
    # for index, row in totalDf.iterrows():
    #     if row["purpose"] == "reservation":
    #         totalDf.drop(labels=index, axis=0, inplace=True)
    #         print("Dropped reservation at index: " + str(index))
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
