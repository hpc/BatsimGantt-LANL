# coding: utf-8
import matplotlib.pyplot as plt
from evalys.jobset import JobSet

#matplotlib.use('WX')

js = JobSet.from_csv('../data/wl1-30k.csv')
print(js.df.describe())

#js.df.hist()

axe = plt.subplots()
js.gantt(axe)
#plt.show()
plt.savefig('testgantt.png', dpi='1200')
