from utils import *
from plots import *

totaldf, totaljs = dfFromCsv(
    "/Users/vhafener/experiments/102722/Steve_reservations_300exp_2/output/expe-out/out_jobs.csv"
)
smallJobList = []
for index, row in totaldf.iterrows():
    if (int(row["requested_number_of_resources"]) < 32) and (
        int(row["execution_time"]) <= 28800
    ):
        smallJobList.append(row["waiting_time"])
print("Waiting time: " + str(sum(smallJobList) / len(smallJobList)))
