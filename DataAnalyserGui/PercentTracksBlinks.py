# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:12:20 2019

@author: DK
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.patches as patches
from matplotlib.lines import Line2D
plt.close("all")
from matplotlib import animation
import matplotlib.ticker as ticker
from IPython import get_ipython
# For plots in a separate window
get_ipython().run_line_magic('matplotlib', 'qt')
import seaborn as sns


Conditions = ['Controls', '5uM', '20uM', '50uM']
Conc = [0, 5, 20, 50]
totalHealthyTracks = np.array( [11, 6, 14, 13])
txt_array = ['n=11', 'n=6','n=14', 'n=13']

nTracksBlinks = np.array([9, 6, 5, 2])

percent_blinks = 100*nTracksBlinks/totalHealthyTracks

fig, ax = plt.subplots(figsize = (8,6), dpi = 175)

sns.scatterplot(x = Conc, y = percent_blinks, ax = ax)
sns.lineplot(x = Conc, y = percent_blinks, ax = ax)
for i, txt in enumerate(txt_array):
    ax.annotate(txt, (Conc[i], percent_blinks[i]))
ax.set_ylabel('Percent of tracks with blinks (%)')
#ax.set_xscale('log')
ax.set_xticks(Conc)
ax.set_xticklabels(Conditions)
ax.set_xlabel('Cd Concentration (uM)')

