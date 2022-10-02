from evalys.jobset import JobSet
import matplotlib.pyplot as plt

js = JobSet.from_csv("data/out_jobs.csv")
js.plot(with_details=True)
plt.savefig('gantt.png')