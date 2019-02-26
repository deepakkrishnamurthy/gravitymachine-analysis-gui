#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 23:31:25 2018

@author: deepak
"""

import numpy as np
import Track
import os
import imp
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
from cycler import cycler
import pickle
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
from scipy import stats
plt.close("all")


#==============================================================================
#                              Plot Parameters and Functions 
#==============================================================================
from matplotlib import rcParams
from matplotlib import rc
#rcParams['axes.titlepad'] = 20 
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
### for Palatino and other serif fonts use:
##rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=False)
#plt.rc('font', family='serif')

rc('font', family='sans-serif') 
rc('font', serif='Helvetica') 
rc('text', usetex='false') 
rcParams.update({'font.size': 22})


dataFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics/Starfish_Blinks'

fileList = os.listdir(dataFolder)

df_intervals = pd.DataFrame({'Organism':[], 'Blink interval': []})
df_durations = pd.DataFrame({'Organism':[], 'Blink duration': []})


for ii, file in enumerate(fileList):
    
    print(file)
    
    with open(os.path.join(dataFolder, file), 'rb') as f:

        Time, peak_indicator, peak_indicator_neg, BlinkIntervals, BlinkDurations = pickle.load(f)
        
        
        
        df_intervals = df_intervals.append(pd.DataFrame({'Organism':np.repeat(file, len(BlinkIntervals),axis=0),'Blink interval': BlinkIntervals}))
        
        df_durations = df_durations.append(pd.DataFrame({'Organism':np.repeat(file, len(BlinkDurations),axis=0),'Blink duration':BlinkDurations}))
        
            
#n, bins1 , *rest = plt.hist(df_intervals["Blink interval"])
#n, bins2 , *rest = plt.hist(df_durations["Blink duration"])
#
#bins1 = np.concatenate(([0], bins1))
#bins2 = np.concatenate(([0], bins2))


#Colors = sns.cubehelix_palette(8, start=0, rot=0, dark=1, light=0, reverse=True)
Colors = sns.dark_palette("purple", 8)
#
#sns.palplot(Colors)
color1 = cm.inferno(64)
color2 = cm.inferno(128)

plt.figure(1)

ax1 = sns.distplot(df_intervals["Blink interval"], kde = True, color = color1 , norm_hist = True, hist_kws={"histtype": "bar", "edgecolor":'w',"linewidth": 0.2,"alpha": 0.5}, kde_kws={"color": "k", "lw": 2, "cut":0})

#ax1.set_xlim([0, 45])

#plt.title('Blink intervals')

#ax1.set_aspect(350)

plt.show()



plt.figure(2)

ax2 = sns.distplot(df_durations["Blink duration"],  kde = True , color = color2, norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5},kde_kws={"color": "k", "lw": 2, "cut":0})

#ax2.set_xlim([0, 25])
#plt.title('Blink durations')
#ax2.set_aspect(45)
plt.show()

#=============

#plt.figure()
#
#ax1 = sns.kdeplot(df_intervals["Blink interval"], shade = True, cut = 0, color = 'r')
#
#ax1.set_xlim([0, 45])
#
#plt.title('Blink intervals')
#plt.show()
#
#
#
#plt.figure()
#
#ax1 = sns.kdeplot(df_durations["Blink duration"], shade = True, cut = 0, color = 'b')
#
#ax2.set_xlim([0, 25])
#plt.title('Blink durations')
#plt.show()

