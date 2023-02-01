# from batvis.utils import *
# from batvis.plots import *
from utils import *
from plots import *

from evalys.visu.gantt import plot_gantt_df
import matplotlib

# matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def iterateReservations(
    inputpath,
    outputfile,
    outJobsCSV,
    verbosity,
    binned,
    bubble,
    reservation,
    window,
):
    """
    Iterates over reservations and plots them based on certain parameters
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
    n = 0
    reservationSet = []
    # Iterate over the experiment's total dataframe, and when a reservation is found, plot it using one (or several) of the plotting functions.
    for index, row in totaldf.iterrows():
        if row["purpose"] == "reservation":
            if n == 0:
                t0 = row["starting_time"]
            n += 1
            reservationSet.append(row)
            with yaspin().line as sp:
                sp.text = (
                    "Plotting chart for reservation from:"
                    + str(row["starting_time"])
                    + " to "
                    + str(row["finish_time"])
                )
                # try:

                # Handle individual cases first
                if reservation and not (binned or bubble):
                    print("Plotting gantt charts for reservations! ")
                    plotReservationGantt(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif binned and not (reservation or bubble):
                    print("Plotting binned gantt charts with utilization plots")
                    plotBinnedGanttReservations(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                elif bubble and not (reservation or binned):
                    print("Plotting bubble charts for reservations")
                    plotBubbleChart(
                        row,
                        totaldf,
                        outDir,
                        totaljs.res_bounds,
                        verbosity,
                        maxJobLen,
                    )
                # Handle group cases all at once
                else:
                    if reservation:
                        print("Plotting gantt charts for reservations")
                        plotReservationGantt(
                            row,
                            totaldf,
                            outDir,
                            totaljs.res_bounds,
                            verbosity,
                            maxJobLen,
                        )
                    if binned:
                        print("Plotting binned gantt charts with utilization plots")
                        plotBinnedGanttReservations(
                            row,
                            totaldf,
                            outDir,
                            totaljs.res_bounds,
                            verbosity,
                            maxJobLen,
                        )
                    if bubble:
                        print("Plotting bubble charts for reservations")
                        plotBubbleChart(
                            row,
                            totaldf,
                            outDir,
                            totaljs.res_bounds,
                            verbosity,
                            maxJobLen,
                        )
                # except Exception as e:
            if window == True:
                if n == 4:
                    n = 0
                    tf = row["finish_time"]
                    with yaspin().line as sp:
                        sp.text = (
                            "Plotting chart for window from:"
                            + str(t0)
                            + " to "
                            + str(tf)
                        )
                        chartWindow(
                            row,
                            t0,
                            tf,
                            totaldf,
                            outDir,
                            totaljs.res_bounds,
                            verbosity,
                            maxJobLen,
                            reservationSet,
                        )
                        reservationSet = []


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
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    if checkForJobs(totalDf):
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
                str("RES-") + str(windowStartTime) + "-" + str(windowFinishTime),
            ),
            dpi=1000,
        )
        # matplotlib.pyplot.show()
        matplotlib.pyplot.close()
        print(
            "\nSaved figure to: "
            + os.path.join(
                outDir,
                str("RES-") + str(windowStartTime) + "-" + str(windowFinishTime),
            )
        )
    else:
        print(
            "Your dataset includes reservations surrounded by no jobs! Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
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
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    for index, row in totalDf.iterrows():
        if row["purpose"] == "reservation":
            totalDf.drop(labels=index, axis=0, inplace=True)
    if verbosity == True:
        print(cut_js)
    if checkForJobs(totalDf):
        smallJs, longJs, largeJs = binDfToJs(totalDf)
        print("testing")
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
    else:
        print(
            "Your dataset includes reservations surrounded by no jobs! Skipping reservation from "
            + str(reservationStartTime)
            + "-"
            + str(reservationFinishTime)
        )


def plotSimpleGantt(outJobsCSV, outfile):
    """
    Plots a simple, single gantt chart for the CSV.
    """
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


def chartWindow(
    row, t0, tf, totaldf, outDir, res_bounds, verbosity, maxJobLen, reservationSet
):
    """
    Plots a window including several reservations. In this case, that number is 4.
    """
    reservationInterval = row["allocated_resources"]
    reservationExecTime = int(row["execution_time"])
    windowSize = 169200

    windowStartTime = t0 - windowSize
    if windowStartTime < 0:
        windowStartTime = 0
    windowFinishTime = tf + windowSize
    if windowFinishTime > float(totaldf["finish_time"].max()):
        windowFinishTime = float(totaldf["finish_time"].max())
    cut_js = cut_workload(
        totaldf, windowStartTime - maxJobLen, windowFinishTime + maxJobLen
    )
    totalDf = pd.concat([cut_js["workload"], cut_js["running"], cut_js["queue"]])
    if not cut_js["workload"].empty:
        fig, ax = matplotlib.pyplot.subplots(figsize=(24, 16))
        plot_gantt_df(
            totalDf,
            res_bounds,
            windowStartTime,
            windowFinishTime,
            title=str(
                "Window from  " + str(t0) + "-" + str(tf) + "+-" + str(windowSize) + "S"
            ),
            resvStart=t0,
            resvExecTime=reservationExecTime,
            resvNodes=reservationInterval,
            resvSet=reservationSet,
        )
        matplotlib.pyplot.savefig(
            os.path.join(
                outDir,
                str("WIN-")
                + str(windowStartTime)
                + "-"
                + str(windowFinishTime)
                + ".png",
            ),
            dpi=1000,
        )
        matplotlib.pyplot.close()
        print(
            "\nSaved figure to: "
            + os.path.join(
                outDir,
                str("WIN-") + str(windowStartTime) + "-" + str(windowFinishTime),
            )
        )
    else:
        print("Empty dataframe! Skipping window from: " + str(t0) + "-" + str(tf))


def chartTimeline(inputpath, outfile, outjobscsv):
    with open(outjobscsv) as f:
        fig, ax = matplotlib.pyplot.subplots(figsize=(16, 30))

        js = JobSet.from_csv(outjobscsv)
        js.plot(timeline=True)
        matplotlib.pyplot.savefig(
            outfile,
            dpi=300,
        )
        matplotlib.pyplot.show()
        matplotlib.pyplot.close()
        print("\nSaved figure to: " + outfile)
