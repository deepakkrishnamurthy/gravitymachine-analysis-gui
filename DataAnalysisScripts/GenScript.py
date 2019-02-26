#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 11:55:48 2019

@author: deepak
"""
import imp
import GravityMachineTrack 
imp.reload(GravityMachineTrack)
import cv2
import sys
import pims
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'

Tmin = 232
Tmax = 239
###
track = GravityMachineTrack.gravMachineTrack(path, Tmin, Tmax)

Index = track.df.index

Frames =np.array(['IMG_2135.tif', 'IMG_2160.tif', 'IMG_2186.tif'])

indices = np.where(np.in1d(track.df['Image name'], Frames))[0]
#indices = 0

print(indices)


FM_smooth = track.smoothSignal(track.df['Focus Measure'],1)

plt.figure()
plt.plot(track.df['Time'],track.smoothSignal(track.df['Focus Measure'],1),'k-')
plt.show()

plt.figure()
plt.plot(Index, FM_smooth,'g-')
plt.scatter(Index[indices],FM_smooth[indices],50,color='r',alpha=0.5) 
plt.show()

for ii in range(track.trackLen):
    print(track.df['Time'][ii], track.df['Image name'][ii])
    

