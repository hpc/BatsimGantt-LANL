from utils import *
import matplotlib

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
