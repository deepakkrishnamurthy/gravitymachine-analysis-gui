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
Tracks = {0:'StarFish6highfreq',1:'StarFish7',2:'StarFish9'}
dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/TrackResults'
nBlinks = 7
#color = cmocean.cm.dense(np.linspace(0, 1,nBlinks))
color = plt.cm.plasma(np.linspace(0, 1,nBlinks))

plt.rcParams['axes.prop_cycle'] = cycler.cycler('color', color)
    
#plt.figure()
count = 0
for value in Tracks.values():
    print(value)
    print(os.path.join(dataFolder,value+'_aligned_blinks'+'.pkl'))
    with(open(os.path.join(dataFolder,value+'_aligned_blinks'+'.pkl'),'rb')) as f:
        T_blink, Z_blink = pickle.load(f)
    print(np.shape(Z_blink))
    print(np.shape(T_blink))
    for ii in range(len(Z_blink[:,])):
        ax1 = plt.plot(T_blink, Z_blink[ii,:], alpha = 0.8, linewidth = 4)
        count += 1


plt.xlabel('Time (s)')
plt.ylabel('Z (mm)')
plt.savefig(os.path.join('Starfish_6_7_9_AlignedBlinks'+'.svg'),dpi=300)

plt.show()
        

print(count)