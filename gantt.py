from utils import *
from plots import *
from evalys.visu.gantt import plot_gantt_df
from evalys.visu.legacy import (
    plot_gantt,
)
import matplotlib

matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def iterateReservations(
    inputpath, outputfile, outJobsCSV, verbosity, binned, bubble, area
):
    """
    Iterates over reservations and plots them based on whether or not they're binned
    """
    InConfig, OutConfig = loadConfigs(inputpath)
    try:
        outDir = getOutputDir(InConfig, outputfile)
    except KeyError:
        print(
            "ERROR! You're trying to plot reservations from a run output generated using a legacy version of batsim."
        )
        sys.exit(2)
    totaldf, totaljs = dfFromCsv(outJobsCSV)
    maxJobLen = getMaxJobLen(totaldf)

    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            with yaspin().line as sp:
                sp.text = (
                    "Plotting chart for reservation from:"
                    + str(row["starting_time"])
                    + " to "
                    + str(row["finish_time"])
                )
                # try:
                if not binned and not bubble and not area:
                    plotReservationGantt(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif binned:
                    plotBinnedGanttReservations(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif bubble:
                    plotBubbleChart(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif area:
                    plotStackedArea(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                # except Exception as e:
                #     print(e)


def saveDfPlot(
    js,
    outfile,
    reservationStartTime,
    reservationExecTime,
    reservationInterval,
    longJs=None,
    largeJs=None,
    windowStartTime=None,
    windowFinishtime=None,
    binned=False,
):
    """
    Saves a plot from a jobset based on the given parameters.
    """
    js.plot(
        with_gantt=True,
        longJs=longJs,
        largeJs=largeJs,
        reservationStart=reservationStartTime,
        reservationExec=reservationExecTime,
        reservationNodes=reservationInterval,
        windowStartTime=windowStartTime,
        windowFinishTime=windowFinishtime,
        binned=binned,
    )
    matplotlib.pyplot.savefig(
        outfile,
        dpi=300,
    )
    matplotlib.pyplot.close()
    print("\nSaved figure to: " + outfile)


def plotReservationGantt(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots a standard gantt reservation, without binning by job size.
    This produces an output folder containing one image for each reservation.
    """
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    if verbosity == True:
        print(
            "\nReservation start: "
            + str(reservationStartTime)
            + "\nReservation finish: "
            + str(reservationFinishTime)
            + "\nReservationExecTime: "
            + str(reservationExecTime)
            + "\nReservationInterval: "
            + str(reservationInterval)
        )
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
    if verbosity == True:
        print(cut_js)
    # FIXME This could use saveDfPlot
    totalDf = pd.concat([cut_js["workload"], cut_js["running"]])
    plot_gantt_df(
        totalDf,
        res_bounds,
        windowStartTime,
        windowFinishTime,
        title=str(
            "Reservation from  "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
            + "+-"
            + str(windowSize)
            + "S"
        ),
        resvStart=reservationStartTime,
        resvExecTime=reservationExecTime,
        resvNodes=reservationInterval,
    )
    matplotlib.pyplot.savefig(
        os.path.join(
            outDir,
            str("reservation") + str(windowStartTime) + "-" + str(windowFinishTime),
        ),
        dpi=1000,
    )
    matplotlib.pyplot.close()
    print(
        "\nSaved figure to: "
        + os.path.join(
            outDir,
            str("reservation") + str(windowStartTime) + "-" + str(windowFinishTime),
        )
    )


def plotBinnedGanttReservations(row, totaldf, outDir, res_bounds, verbosity, maxJobLen):
    """
    Plots gantt charts for reservations, binning into 3 different job types based on runtime and requested resources.
    """
    reservationStartTime = int(row["starting_time"])
    reservationFinishTime = int(row["finish_time"])
    reservationExecTime = int(row["execution_time"])
    reservationInterval = row["allocated_resources"]
    if verbosity == True:
        print(
            "\nReservation start: "
            + str(reservationStartTime)
            + "\nReservation finish: "
            + str(reservationFinishTime)
            + "\nReservationExecTime: "
            + str(reservationExecTime)
            + "\nReservationInterval: "
            + str(reservationInterval)
        )
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
    if verbosity == True:
        print(cut_js)
    try:
        smallJs, longJs, largeJs = binDfToJs(cut_js["workload"])
        saveDfPlot(
            smallJs,
            getFileName(
                str("BIN-" + str(windowStartTime) + "-" + str(windowFinishTime)), outDir
            ),
            reservationStartTime,
            reservationExecTime,
            reservationInterval,
            longJs=longJs,
            largeJs=largeJs,
            windowStartTime=windowStartTime,
            windowFinishtime=windowFinishTime,
            binned=True,
        )
    except ValueError:
        print(
            "WARNING: Your dataset contains reservations that are not surrounded by any jobs. Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )


def plotSimpleGantt(outJobsCSV, outfile):
    """
    Plots a simple, single gantt chart for the CSV.
    """
    # FIXME Rescale this chart so its bigger
    with open(outJobsCSV) as f:
        if sum(1 for line in f) > 70000:
            print(
                "Creating gantt charts can be unreliable with files larger than 70k jobs. Are you use you want to continue? (Y/n)"
            )
            cont = input()
            if cont == "Y" or cont == "y":
                pass
            elif cont == "n":
                sys.exit(2)
        js = JobSet.from_csv(outJobsCSV)
        js.plot(with_gantt=True)
        matplotlib.pyplot.savefig(
            outfile,
            dpi=300,
        )
        matplotlib.pyplot.close()
        print("\nSaved figure to: " + outfile)
