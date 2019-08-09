#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 00:10:17 2019
Gravity Machine Diatoms data analysis pipeline
Raw Data -> PIV correction -> Corrected data -> Blink detection -> Velocity distributions
@author: deepak
"""

import imp
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython import get_ipython
#For plots in a separate window
get_ipython().run_line_magic('matplotlib', 'qt')
# For inline plot
#get_ipython().run_line_magic('matplotlib', 'inline')
# Analysis file path
sns.set(context='paper', style='white', palette='deep', font='sans-serif', font_scale=2, color_codes=True, rc=None)

path = '/Users/deepak/Dropbox/GravityMachine/Diatom_Blinks/track000_0_0_analysis.csv'

df = pd.read_csv(path)


# Plot of Z-displacement
plt.figure()
#sns.lineplot(df['Time'], df['Zpos_raw'],color = 'r', label='Raw position data', linewidth = 2)
sns.lineplot(df['Time'], df['Zpos'],color = 'b', label='Corrected position data', linewidth = 2)


# Plot of Z-velocity
plt.figure()
sns.lineplot(df['Time'], df['Zvel'],color = 'k', label='Corrected velocity')


# Velocity distribution
plt.figure()
ax0 = sns.distplot(df["Zvel"],  kde = True , color = 'b', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})



# Blink detection

Z_disp_smooth = 