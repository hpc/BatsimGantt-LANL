import matplotlib.pyplot as plt
import pandas as pd
import re
import random


# test
# Plot colors
def get_cmap(n, name='Greys'):
    # Returns a function that maps each index in 0-n-1 to a distinct color
    return plt.cm.get_cmap(name, n)

# def gnt_factory (numplot, row, gnt, cmap):
#     setcolor = cmap(row['job_id'])
#     i=0
#     resource_range = row['allocated_resources'].split(" ")
#     while i<numplot:
#         gnt.broken_barh([row['starting_time'], row['finish_time']],(resource_range[i].split("-")[0], resource_range[i].split("-")[1]), facecolors=setcolor)
#         i+=1

def main():
    # Initializing the plot
    fig, gnt = plt.subplots()
    # plt.figure(figsize(6553, 4915), dpi=100)

    df = pd.read_csv('input.csv', usecols=['job_id','workload_num_machines','final_state','starting_time','finish_time','allocated_resources', 'requested_number_of_resources'])
    starting_time = df.starting_time.min()
    finish_time = df.finish_time.max()
    workload_num_machines = df.workload_num_machines.max()
    num_jobs = df.job_id.max()
    cmap = get_cmap(1492)

    # Configuring the plot's bounds and axis labels
    gnt.set_ylim(0,1490)

    gnt.set_xlim(starting_time,finish_time)
    gnt.set_xlabel('time')
    gnt.set_ylabel('allocated resources by job')

    # Fills in the chart

    #====== EXAMPLE =========
    # gnt.broken_barh([(0,21600)],(768, 1023), color=cmap(1))
    # gnt.broken_barh([(0,28800)],(256, 767), color=cmap(25))
    # gnt.broken_barh([(28800,50400)],(768, 1279), color=cmap(36))
    # gnt.broken_barh([(21600,72000)],(1024, 1087), color=cmap(210))
    # gnt.broken_barh([(0,300000)],(1087, 1489), color=cmap(64))


    for index, row in df.iterrows():
        # ranges = len(re.findall("\b([0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9])\b\-\b([0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9])\b", row['allocated_resources']))
        ranges = len(row['allocated_resources'].split(" "))
        if ranges == 1:
            # print("Starting time: " + str(row['starting_time']) + " Finish time: " + str(row['finish_time']) + " Resource block start: " + str(row['allocated_resources'].split("-")[0]) + " Resource block end: " + str(row['allocated_resources'].split("-")[1]))
            gnt.broken_barh([(int(row['starting_time']), int(row['finish_time']))],(int(row['allocated_resources'].split("-")[0]), int(row['allocated_resources'].split("-")[1])), color=cmap(int(row['requested_number_of_resources']))) #
        else:
            # gnt_factory(ranges, row, gnt, cmap)
            setcolor = int(row['requested_number_of_resources'])
            i=0
            resource_range = row['allocated_resources'].split(" ")
            while i<ranges:
                gnt.broken_barh([(int(row['starting_time']), int(row['finish_time']))],(int(resource_range[i].split("-")[0]), int(resource_range[i].split("-")[1])), color=cmap(setcolor))
                i+=1


    # Exports the plot
    plt.savefig("ganttSizeGray.svg", dpi=1200)

if __name__ == "__main__":
    main()
