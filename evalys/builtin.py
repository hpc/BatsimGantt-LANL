from evalys.jobset import JobSet
import matplotlib.pyplot as plt

js = JobSet.from_csv("../data/out_jobs.csv")
print(js.df.describe())

jf.df.hist()

#js.plot(with_details=True)
js.gantt()
plt.savefig('gantt.png')
