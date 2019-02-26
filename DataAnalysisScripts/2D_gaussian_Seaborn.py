# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 19:18:07 2018

@author: deepak90
"""

import seaborn as sns
df = sns.load_dataset('iris')
sns.jointplot(x=df["sepal_length"], y=df["sepal_width"], kind='kde', color="grey", space=0)
