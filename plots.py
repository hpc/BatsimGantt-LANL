from utils import *
from gantt import *
import matplotlib
import seaborn as sns
from evalys.jobset import JobSet

matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def chartRunningAverage(inputpath, outputfile, outJobsCSV):
    """
    Charts the running average of utilization
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    # FIXME Unhardcode this
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
    # TODO Unhardcode the window start and finish times
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
    # outfile = getFileName(
    #     str(InConfig["batsched-policy"])
    #     + "-"
    #     + str(InConfig["nodes"])
    #     + "-"
    #     + datetime.now().strftime("%H:%M:%S"),
    #     outDir,
    # )
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

    if totalDf.empty:
        print(
            "Empty dataframe! Skipping reservation from: "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )
    else:
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


def plotStackedArea(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots a stacked area chart for each reservation in totaldf based on the given parameters
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
        str("reservation") + str(windowStartTime) + "-" + str(windowFinishTime),
    )

    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )

    if cut_js["workload"].empty:
        print(
            "Empty dataframe! Skipping reservation from: "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )
    else:
        # FIXME I should do a standard timescale for this and the bubbles
        smallJs, longJs, largeJs = binDfToJs(cut_js["workload"])
        print(
            max(
                [
                    len(smallJs.utilisation.load),
                    len(longJs.utilisation.load),
                    len(largeJs.utilisation.load),
                ]
            )
        )
        # smallJs.utilisation.load.sort_index(inplace=True)
        # longJs.utilisation.load.sort_index(inplace=True)
        # largeJs.utilisation.load.sort_index(inplace=True)

        # print(
        #     max(
        #         [
        #             smallJs.utilisation.load,
        #             longJs.utilisation.load,
        #             largeJs.utilisation.load,
        #         ]
        #     )
        # )
        # sys.exit(2)
        matplotlib.pyplot.stackplot(
            "time", smallJs.utilisation.load, longJs.utilisation.load
        )
        # matplotlib.pyplot.legend(loc="upper left")
        matplotlib.pyplot.show()
