#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 19:58:44 2018
Focus Tracking Control Experiment Data Analysis
@author: deepak
"""

import csv as csv
import numpy as np
import matplotlib.pyplot as plt
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
plt.close("all")
#==============================================================================
#                              Plot Parameters   
#==============================================================================
from matplotlib import rcParams
from matplotlib import rc
rcParams['axes.titlepad'] = 20 
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)
plt.rc('font', family='serif')

#==============================================================================
#                               Data Import     
#==============================================================================
#path = '/Volumes/prakash-lab/Projects/GravityMachine/YTracking_2018_07_12/First_set/YTracking_MS16_amp0_15_freq4_gain4_sampl100'
#path= '/Volumes/prakash-lab/Projects/GravityMachine/YTracking_2018_07_12/First_set/YTracking_MS16_amp0_15_freq2_gain8_sampl100'
#path = '/Volumes/prakash-lab/Projects/GravityMachine/YTrackingControls_2018_10_22/Speed_500_1600steps_v3'
#path = '/Volumes/prakash-lab/Projects/GravityMachine/YTrackingControls_2018_10_23/Test1'
#path = '/Volumes/prakash-lab/Projects/GravityMachine/YTracking_2018_07_12/speed500_v3'
#path = '/Volumes/prakash-lab-1/Projects/GravityMachine/YTracking_2018_07_12/speed500_v3'
#path = 'smb://soe-nas/prakash-lab/Projects/GravityMachine/YTracking_2018_07_12/speed500_v3'
#path = '/Volumes/prakash-lab-1/Projects/GravityMachine/YTrackingControls_2018_10_23/Freq_2_Gain_10_Amp_0_15_T_4_3mm'
#path = '/Volumes/prakash-lab-1/Projects/GravityMachine/YTrackingControls_2018_10_24/MotionSpeed_250um_s_Test'
path = '/Volumes/prakash-lab-1/Projects/GravityMachine/YTrackingControls_2018_10_24/Speed_250um_s/Freq_2_Gain_5_Amp_0_15_trial_3'
#path  = 'Y:/Projects/GravityMachine/YTracking_2018_07_12/speed500_v3'


# Windows Path
#path  = 'Y:/Projects/GravityMachine/YTrackingControls_2018_10_23/Freq_2_Gain_1_Amp_0_1_A_1'
file="track.csv"
dataFolder, TrackName = os.path.split(path)

#dataFolder = '/Users/deepak/Dropbox/GravityMachine/Presentations/Figures/'

print(50*'*')
print('Folder in which to save data: {}'.format(dataFolder))
print(50*'*')

print(50*'*')
print('Tail: {}'.format(TrackName))

#resultFolder = os.path.join(dataFolder,'TrackResults')
#
#if(not os.path.exists(resultFolder)):
#    os.makedirs(resultFolder)
    
    
Data=[]
reader = csv.reader(open(os.path.join(path,file),newline=''))
for row in reader:
    Data.append(row)
n=len(Data)

Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])             # Time stored is in milliseconds
Xobjet=np.array([float(Data[i][1]) for i in range(1,n)])             # Xpos in motor full-steps
Yobjet=np.array([float(Data[i][2]) for i in range(1,n)])             # Ypos in motor full-steps
Zobjet=np.array([float(Data[i][3]) for i in range(1,n)])             # Zpos is in encoder units
ThetaWheel=np.array([float(Data[i][4]) for i in range(1,n)])
ZobjWheel=np.array([float(Data[i][5]) for i in range(1,n)])
ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])   # 0 for auto, 1 for manual
ImageName=np.array([Data[i][7] for i in range(1,n)])
focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
liqLensFreq = np.array([float(Data[i][10]) for i in range(1,n)])
liqLensAmp = np.array([float(Data[i][11]) for i in range(1,n)])
liqLensGain = np.array([float(Data[i][12]) for i in range(1,n)])



# Print the liquid lens parameters
print('Liquid Lens Amplitude: {}'.format(liqLensAmp[0]))
print('Liquid Lens Frequency: {}'.format(liqLensFreq[0]))
print('Liquid Lens Max Gain: {}'.format(liqLensGain[0]))

# ThetaWheel actually contains the information on the moving Y-stage.
# Yobjet contains the position of the tracking Y-stage


# Find the Time point for the start of stage movement


Time = Time - Time[0]
#YstageMoving = -(ThetaWheel - ThetaWheel[0])
#YstageTracking = Yobjet - Yobjet[0]

YstageMoving = ThetaWheel 
YstageTracking = Yobjet


# PLOTS
plt.figure()

plt.plot(Time, YstageMoving,color = 'k')
plt.scatter(Time, YstageTracking, 10,color='r')

plt.title('Focus Tracking Controls' )
plt.xlabel('Elapsed Time (s)')
plt.legend()
plt.ylabel('Stage Displacement (mm)')  
#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MovingVsTracking.png'),dpi=300) 
#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MovingVsTracking.svg'),dpi=300) 

#plt.show(block=False)

plt.figure(figsize=(8,4))

#plt.subplot(121)
plt.scatter(Time, focusMeasure,10,color='b')
plt.xlabel('Elapsed Time (s)')
plt.legend()
plt.ylabel('Focus measure')  

#plt.subplot(122)
#plt.scatter(Time, MaxfocusMeasure,10,color='r')
#plt.xlabel('Elapsed Time (s)')
#plt.legend()
#plt.ylabel('Max of focus measure')  

#plt.title('Focus Tracking Controls' )

#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'FocusMeasure.png'),dpi=300) 
#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'FocusMeasure.svg'),dpi=300) 

#plt.show(block=False)


# Calculate the Error in Tracking:
SquaredError = (YstageMoving - YstageTracking)**2



RMS_error = (np.mean(SquaredError))**(1/2)
maxError = (np.mean(YstageMoving**2))**(1/2)

print(50*'*')
print('RMS Tracking Error (um): {}'.format(RMS_error*1000))
print('RMS Error with no tracking (um): {}'.format(maxError*1000))
print('Relative Tracking Error (%): {}'.format(100*RMS_error/maxError))


print(50*'*')

normFocusMeasure = (focusMeasure - np.mean(focusMeasure))

normFocusMeasure = normFocusMeasure/np.abs((np.max(normFocusMeasure) - np.min(normFocusMeasure)))


plt.figure(figsize=(8,4))

#plt.subplot(121)
plt.plot(Time, 2*normFocusMeasure,'r--')
plt.plot(Time, focusPhase)

plt.xlabel('Elapsed Time (s)')
plt.title('Focus Measure vs Focus Phase')

plt.figure(figsize=(8,4))

#plt.subplot(121)
#plt.plot(Time, 2*normFocusMeasure,'r--')
plt.scatter(focusPhase, 2*normFocusMeasure)

plt.xlabel('Focus Phase')
plt.ylabel('Focus Measure (normalized)')
plt.title('Focus Measure vs Focus Phase')
