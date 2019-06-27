#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 11:55:48 2019

@author: deepak
"""
print(100)
import imp
import GravityMachineTrack 
imp.reload(GravityMachineTrack)
import numpy as np
import matplotlib.pyplot as plt
# from IPython import get_ipython
# For plots in a separate window
# get_ipython().run_line_magic('matplotlib', 'qt')
# For inline plot
#get_ipython().run_line_magic('matplotlib', 'inline')




print(1)

Tmin = 0
Tmax = 10

File = '/Users/deepak/Dropbox/GravityMachine/DiatomTestDataset/track000.csv'
###

# orgDim in mm
track = GravityMachineTrack.gravMachineTrack(fileName = File, Tmin = Tmin, Tmax = Tmax, computeDisp = True, orgDim = 0.1, overwrite_piv=False, overwrite_velocity=True)
##
#mean_vel_z = np.nanmean(track.Vz)
#std_vel_z = np.nanstd(track.Vz)
#
#
##Index = track.df.index
##
##Frames =np.array(['IMG_2135.tif', 'IMG_2160.tif', 'IMG_2186.tif'])
##
##indices = np.where(np.in1d(track.df['Image name'], Frames))[0]
###indices = 0
##
##print(indices)
##
##
##FM_smooth = track.smoothSignal(track.df['Focus Measure'],1)
##
##plt.figure()
##plt.plot(track.df['Time'],track.smoothSignal(track.df['Focus Measure'],1),'k-')
##plt.show()
##
##plt.figure()
##plt.plot(Index, FM_smooth,'g-')
##plt.scatter(Index[indices],FM_smooth[indices],50,color='r',alpha=0.5) 
##plt.show()
##
##for ii in range(track.trackLen):
##    print(track.df['Time'][ii], track.df['Image name'][ii])
#    
#
# Plot the original velocity and the corrected velocity
plt.figure()

plt.plot(track.df['Time'], track.df['ZobjWheel'], 'ro')
plt.plot(track.df['Time'][track.imageIndex_array], track.Z_objFluid, 'bs')

plt.xlabel('Time (s)')
plt.ylabel('Z displacement (mm)')

plt.show()

# Plot the original velocity and the corrected velocity
plt.figure()

plt.plot(track.df['Time'], track.Vz, 'ro')
plt.plot(track.df['Time'][track.imageIndex_array], track.Vz_objFluid, 'bs')

plt.xlabel('Time (s)')
plt.ylabel('Z velocity (mm /s)')

plt.show()


track.saveAnalysisData(overwrite = True)

plt.figure()

plt.plot(track.df_analysis['Time'], track.df_analysis['Zpos_raw'], 'ro')
plt.plot(track.df_analysis['Time'], track.df_analysis['Zpos'], 'bs')

plt.xlabel('Time (s)')
plt.ylabel('Z displacement (mm)')

plt.show()

# Plot the original velocity and the corrected velocity
plt.figure()

plt.plot(track.df_analysis['Time'], track.df_analysis['Zvel'], 'bs')
plt.plot(track.df['Time'], track.Vz, 'ro')

plt.xlabel('Time (s)')
plt.ylabel('Z velocity (mm /s)')

plt.show()


