from utils import *
from gantt import *
import matplotlib
import seaborn as sns

matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def chartRunningAverage(inputpath, outputfile, outJobsCSV):
    """
    Charts the running average of utilization
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    outDir = getOutputDir(InConfig, outputfile)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    smallDf = []
    longDf = []
    largeDf = []
    allResvDf = [smallDf, longDf, largeDf]

    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            with yaspin().line as sp:
                sp.text = (
                    "Plotting gantt chart for reservation from:"
                    + str(row["starting_time"])
                    + " to "
                    + str(row["finish_time"])
                )
                #! Catch empty DFs here
                allresvDf = prepDf(row, totaldf, maxJobLen, allResvDf)
                print(
                    "Reservation from: "
                    + str(row["starting_time"])
                    + "-"
                    + str(row["finish_time"])
                    + " added to df."
                )
    smallJs = JobSet.from_df(allResvDf[0])
    longJs = JobSet.from_df(allResvDf[1])
    largeJs = JobSet.from_df(allResvDf[2])
    # TODO Unhardcode the window start and finish times
    # ! THIS IS WRONG AND DOES NOT PLOT AVERAGE RIGHT NOW. THIS IS ONLY AN OUTLINE
    smallJs.plot(
        with_gantt=False,
        longJs=longJs,
        largeJs=largeJs,
        average=True,
    )
    outfile = getFileName(str("testing"), outDir)
    matplotlib.pyplot.savefig(
        outfile,
        dpi=300,
    )
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + outfile)


def plotBubbleChart(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots a bubble chart for each reservation based on the given parameters
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
        sns.scatterplot(
            data=cut_js["workload"],
            x="starting_time",
            y="execution_time",
            size="requested_number_of_resources",
            legend=False,
            sizes=(20, 2000),
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
        matplotlib.pyplot.savefig(
            outFile,
            dpi=300,
        )
        matplotlib.pyplot.close()
        print("\nSaved figure to: " + outFile)
