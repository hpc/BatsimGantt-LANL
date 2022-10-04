from evalys.jobset import JobSet
import matplotlib.pyplot as plt

js = JobSet.from_csv("../data/inputmed.csv")
print(js.df.describe())

#js.df.hist()

js.plot(with_details=True)
#js.gantt()
#plt.savefig('gantt.png')
plt.show()
