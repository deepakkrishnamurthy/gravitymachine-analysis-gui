#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 15:55:56 2018
Plot to collate the aligned blink tracks
@author: deepak
"""

import csv as csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate as interpolate
import scipy.signal as signal
import scipy.ndimage as ndimage
import matplotlib.patches as patches
from numpy.polynomial import polynomial as Poly
import cmocean
import pickle
import math
import os
import pandas as pd
import math
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import cycler
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
rcParams.update({'font.size': 16})
#==============================================================================
Tracks = {0:'Seacucumber9',1:'Dendraster3',2:'BrittleStar9',3:'AcornWorm3',4:'SeaUrchin7',5:'StarFish7',6:'Snail1'}
#dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/TrackResults'
dataFolder = '/Users/deepak/Dropbox/GravityMachine/DataAnalysis/TrackingErrorAnalysisData_New'
nData = len(Tracks.keys())
#color = cmocean.cm.dense(np.linspace(0, 1,nBlinks))
color = plt.cm.plasma(np.linspace(0, 1, nData))

plt.rcParams['axes.prop_cycle'] = cycler.cycler('color', color)

TimeStamp = {}
TrackingError = {}   
RMSerror_x = []
RMSerror_z = []
STDerror_x = []
STDerror_z = []
#plt.figure()
count = 0
for key, value in Tracks.items():
    print(value)
    file = os.path.join(dataFolder,value+'_trackingError'+'.pkl')
    with(open(file,'rb')) as f:
        TimeStamp[key], TrackingError[key] =  pickle.load(f)
        
    TrackingError[key] = 1000*TrackingError[key]    # Convert to um
    RMSerror_x.append((np.mean(np.abs(TrackingError[key][:,0]))))
    RMSerror_z.append((np.mean(np.abs(TrackingError[key][:,1]))))
        
    STDerror_x.append((np.std(np.abs(TrackingError[key][:,0]))))
    STDerror_z.append((np.std(np.abs(TrackingError[key][:,1]))))
    
    
print('RMS errors X',RMSerror_x)
print('RMS errors Z',RMSerror_z)

print('STD errors X',STDerror_x)
print('STD errors Z',STDerror_z)
#==============================================================================
# Plots
#==============================================================================
# Bar plot showing the RMS and Std in the tracking error
#==============================================================================
key = 3
plt.figure()
plt.plot(TimeStamp[key],TrackingError[key][:,0],color='r')
plt.plot(TimeStamp[key],TrackingError[key][:,1],color='b')
plt.xlabel('Time')
plt.ylabel('Tracking error (um)')
plt.title(Tracks[key])

plt.show()

ind = np.arange(nData)
widths = 0.35

fig, ax = plt.subplots(figsize=(16,9),dpi=150)
rect1 = ax.bar(ind, RMSerror_x, widths, color = 'r', alpha = 0.5, yerr = STDerror_x)
rect2 = ax.bar(ind+widths, RMSerror_z, widths, color = 'b', alpha = 0.5, yerr = STDerror_z)
ax.set_ylabel('Tracking error (um)')
ax.set_xticks(ind +widths/2)
ax.set_xticklabels((Tracks.values()))
ax.set_ylim((-40,500))
ax.legend((rect1[0], rect2[0]),('X error', 'Z error'))
saveFileName = os.path.join(dataFolder,'RMSerror_STD.svg')
plt.savefig(saveFileName,dpi=300)
plt.show()
f = []
for key, value in Tracks.items():
    
    f,ax = plt.subplots(figsize=(6,8),dpi=150)
    plt.hist((TrackingError[key][:,0]**2)**(1/2),density=True, cumulative =True, facecolor = 'r', edgecolor = 'k', alpha = 0.5)
    plt.hist((TrackingError[key][:,1]**2)**(1/2),density=True, cumulative = True, facecolor = 'b', edgecolor = 'k', alpha= 0.5)
    plt.xlabel('Tracking error (um)')
    plt.ylabel('Cumulative probability')
    plt.yticks(np.arange(0,1.1,0.1))
    plt.title(Tracks[key])
    saveFileName = os.path.join(dataFolder,Tracks[key]+'_'+'cumulative_prob_error.svg')
    plt.savefig(saveFileName,dpi=300)
    plt.show(block=False)