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
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os




Tmin = 0
Tmax = 0
###

track = GravityMachineTrack.gravMachineTrack(Tmin = Tmin, Tmax = Tmax)

mean_vel_z = np.nanmean(track.Vz)
std_vel_z = np.nanstd(track.Vz)

plt.figure()
plt.plot(track.df['Time'], track.Vz, 'ro')
plt.show()

#Index = track.df.index
#
#Frames =np.array(['IMG_2135.tif', 'IMG_2160.tif', 'IMG_2186.tif'])
#
#indices = np.where(np.in1d(track.df['Image name'], Frames))[0]
##indices = 0
#
#print(indices)
#
#
#FM_smooth = track.smoothSignal(track.df['Focus Measure'],1)
#
#plt.figure()
#plt.plot(track.df['Time'],track.smoothSignal(track.df['Focus Measure'],1),'k-')
#plt.show()
#
#plt.figure()
#plt.plot(Index, FM_smooth,'g-')
#plt.scatter(Index[indices],FM_smooth[indices],50,color='r',alpha=0.5) 
#plt.show()
#
#for ii in range(track.trackLen):
#    print(track.df['Time'][ii], track.df['Image name'][ii])
    

