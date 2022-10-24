from evalys.jobset import JobSet
from evalys.visu.gantt import plot_gantt
import matplotlib.pyplot as plt

js = JobSet.from_csv("../data/inputmed.csv")
print(js.df.describe())

#js.df.hist()
plt = plot_gantt(js, ax="axe",title="Gantt chart")
#js.plot(with_details=False)
#plt.savefig('gantt.png')
plt.show()
