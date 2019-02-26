# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 19:00:43 2018

@author: deepak90
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import gaussian_kde
import seaborn as sns

mean = np.array([0,0])

cov = np.ndarray((2,2), dtype = 'float')

cov[0,0] = 2
cov[1,1] = 1

cov = [[1,0],[0,100]]

print(cov)

RandomData = np.random.multivariate_normal(mean, cov, size=10000)
X = RandomData[:,0]
Y = RandomData[:,1]
xy = np.vstack([X,Y])
Z = gaussian_kde(xy)(xy)


print(np.shape(RandomData))

plt.figure(figsize=(4,12))
fig = plt.scatter(X, Y,c=Z,s = 10)
plt.xlim(-10,10)
plt.axis('equal')
fig.axes.get_xaxis().set_visible(False)
fig.axes.get_yaxis().set_visible(False)
plt.savefig('verticalScatter.png',dpi=150)


sns.jointplot(x=X, y=Y, kind='kde', space=0)
sns.plt.gca().set_aspect('equal', adjustable='box')




