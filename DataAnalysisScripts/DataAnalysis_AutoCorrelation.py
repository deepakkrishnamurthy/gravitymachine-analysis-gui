#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:25:27 2018

Autocorrelation and other analysis methods on the 3D_track datasets from Gravity Machine
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
from matplotlib.lines import Line2D
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
import imp
import Track
import FigureParameters
imp.reload(Track)
#plt.style.use(os.path.join(os.getcwd(),'gravmachinestyle.mplstyle'))
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
#                       General Analysis Functions
#======================================================================
def autocorrelation(data,minLag, maxLag):

    res = np.zeros_like(np.array([i for i in range(minLag,maxLag)]))
    n = len(data)
    for kk in range(minLag,maxLag):
        res[kk] = np.sum(data[:n-kk]*data[-(n-kk):])
    
    return res/np.sum(data**2)

def autocorrelation_window(data = None,minLag = None, maxLag= None, start = 0, stop = None, window = 1, stepSize = 1):
    
    LagArray = np.array([i for i in range(minLag,maxLag)])
    TimeArray = np.array([i for i in range(start,stop - window - maxLag,stepSize)])
    
    res = np.zeros((len(LagArray),len(TimeArray)))
    
#    print(np.shape(res))
    
    for ii, Time in enumerate(TimeArray):
        
#        print(ii)
        timeIndexMin = Time
        timeIndexMax = Time + window
        for kk,Lag in enumerate(LagArray):
            
#            print('Time, Lag : {},{}'.format(Time,Lag))
            
            res[kk,ii] = np.sum(data[timeIndexMin:timeIndexMax]*data[timeIndexMin + Lag : timeIndexMax + Lag])
    
        res[:,ii] = res[:,ii]/np.sum(data[timeIndexMin:timeIndexMax]**2)

        
    return res, LagArray, TimeArray

def GaussianPulse(time = None, samplingFreq = None, pulseWidth_time = 1, pulseInterval_time = 1):
    pulseWidth = int(pulseWidth_time*samplingFreq)
    pulseIntervalIndex = int(pulseInterval_time*samplingFreq)

    signalGaussPulse = np.zeros_like(time)
    
    
    for ii in range(0,len(time)):
       
        if(ii % pulseIntervalIndex == 0 and ii-int(pulseWidth/2)>0 and ii+int(pulseWidth/2) < len(time)):
            signalGaussPulse[ii-int(pulseWidth/2):ii+int(pulseWidth/2)] = signal.gaussian(pulseWidth,1)
 
    
    return signalGaussPulse

def randomGaussPulse(time = None, samplingFreq = None, pulseWidth_time = 1):
    pulseWidth = int(pulseWidth_time*samplingFreq)
    signalGaussPulse = np.zeros_like(time)
    
    random_points = np.random.randint(0,len(time),size=np.shape(time))
    
    for ii in random_points:
        if(ii-int(pulseWidth/2)>0 and ii+int(pulseWidth/2) < len(time)):
            signalGaussPulse[ii-int(pulseWidth/2):ii+int(pulseWidth/2)] = signal.gaussian(pulseWidth,1)
        
    
    return signalGaussPulse

def GaussianPulseAtPeaks(time = None, samplingFreq = None, pulseWidth_time = 1, Peaks = None):
    o
#    pulseWidth = roundToEven(array = np.array(pulseWidth_time*samplingFreq, dtype = 'int'))
    
    pulseWidth = math.ceil(pulseWidth_time*samplingFreq / 2.) * 2
    print(pulseWidth)
    
    signalGaussPulse = np.zeros_like(time)
    
    indexArray = np.array(range(len(time)))
    
    random_points = indexArray[Peaks]
    
   
    
    for ii, peak_locs in enumerate(random_points):
        if(peak_locs-int(pulseWidth/2)>0 and peak_locs+int(pulseWidth/2) < len(time)):
            signalGaussPulse[peak_locs-int(pulseWidth/2):peak_locs+int(pulseWidth/2)] = signal.gaussian(pulseWidth,10)
        
    
    return signalGaussPulse
    

def roundToEven(array = None):
    print(array)
    result = np.zeros_like(array)
    
    for ii in range(len(array)):
        result[ii] = math.ceil(array[ii] / 2.) * 2
        
    return result


    
def find_peaks(T,Z):
    peaks=signal.find_peaks(Z, distance=None,width=None,prominence=(4, 40))
    return peaks[0]

def find_peaks_dendraster(T,Z):
    peaks = signal.find_peaks(Z, distance=None,width=(0,3000),prominence=(0.4, 10))
    return peaks[0]



#==========================================================================
#def main():
#------------------------------------------------------------------------------
#       Choose the Track to analyze
#------------------------------------------------------------------------------
# Snail
#------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail1'

#------------------------------------------------------------------------------
# Dendraster
#------------------------------------------------------------------------------
#dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
#    TrackName = 'Dendraster3'
#------------------------------------------------------------------------------
# Starfish
#------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'
#dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish10'
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'
#    TrackName = 'StarFish10'
#    ------------------------------------------------------------------------------
# Acorn Worm
#------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm3'

#------------------------------------------------------------------------------
# Sea Cucumber
#------------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber/seacucmber9_Auto'
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'

#------------------------------------------------------------------------------
# Brittle Star
#------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar9_Long_Good_Ytracking'
#------------------------------------------------------------------------------
# Sea Urchin
#------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin/SeaUrchin7'

#    dataFolder = 'L:/VolvoxPhoptora/vvx6'
#    dataFolder ='/Users/deepak/Dropbox/GravityMachine/ExperimentResults/VolvoxPhotoresponse/vvx25'

#    dataFolder = '/Volumes/GRAVMACH1/VolvoxLight_ExponentialGradient/vvx10'

#------------------------------------------------------------------------------
# Pyro
#------------------------------------------------------------------------------
dataFolder = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/nnn1'
file = "track_cropped.csv"

#*rest,orgName = os.path.split(dataFolder)
#saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
#
#BlinkDataFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics/Dendraster_Blinks'
#
## Load the Blink data
#BlinkFile = 'Dendraster3_Blink_Statistics.pkl'
##BlinkFile = 'StarFish10_Blink_Statistics.pkl'
#
##dataFolder = '/Users/deepak/Dropbox/GravityMachine/Presentations/Figures/'
#
#print(50*'*')
#print('Folder in which to save data: {}'.format(dataFolder))
#print(50*'*')

#    print(50*'*')
#    print('Tail: {}'.format(TrackName))

#    resultFolder = os.path.join(dataFolder,'TrackResults')
#    fullPath = os.path.join(dataFolder,TrackName)
#    
#    saveFile = os.path.join(resultFolder,TrackName+'_Blink_Signals'+'.pkl')

#    if(not os.path.exists(resultFolder)):
#        os.makedirs(resultFolder)
#======================================================================
# Plots of Tracks
#======================================================================
Tmin = 0
Tmax = 0
OrgTrack1 = Track.GravMachineTrack(dataFolder,file,Tmin,Tmax)

#    OrgTrack1.smoothTrack(20)

#OrgTrack1.computeVelocity()
#
#BlinkFile = os.path.join(BlinkDataFolder, BlinkFile)
#with open(BlinkFile, 'rb') as f:
#
#    Time, peak_indicator, peak_indicator_neg, TimeBetweenBlinks, BlinkDurations = pickle.load(f)
    
    
#OrgTrack1.loadPeaks(peak_indicator, peak_indicator_neg)

OrgTrack1.plot3DComponents(signalZ = OrgTrack1.ZobjWheel,labels=1,save = 1)


#df = OrgTrack1.plotAlignedBlinks(labels=1)
    
   
    
#    peaks, peaks_neg, Z_fast = OrgTrack1.findBlinks(timeWindow=50)
    
#    OrgTrack1.plotTrackWalls(plotPeaks=0,labels=0, save = 0)
#    OrgTrack1.plotTrackWalls(plotPeaks=0,labels=1, save = 0)
    
#    RisingEdge = []
#    FallingEdge = []
#    for ii in range(OrgTrack1.trackLen - 1):
#        if(OrgTrack1.LED_intensity[ii]==0 and OrgTrack1.LED_intensity[ii+1]>0):
#            RisingEdge.append(ii)
#        elif(OrgTrack1.LED_intensity[ii]>0 and OrgTrack1.LED_intensity[ii+1]==0):
#            FallingEdge.append(ii)

    
    
#    custom_line = [Line2D([0], [0], color='gold', lw=4), Line2D([0], [0], color='k', lw=4) ]
#
#            
#    
#    OrgTrack1.ZobjWheel = OrgTrack1.ZobjWheel - OrgTrack1.ZobjWheel[0]
#
#    Z_movingAvg = OrgTrack1.smoothSignal(OrgTrack1.ZobjWheel,10)
#    #------------------------------------------------------------------------------
#    # Volvox phototaxis plots
#    #------------------------------------------------------------------------------
##    fig, ax1 = plt.subplots()
##
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(OrgTrack1.ZobjWheel),y2 =0,where = OrgTrack1.LED_intensity>0,facecolor = 'gold',alpha = 0.5)
##
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(OrgTrack1.ZobjWheel),y2 =0,where = OrgTrack1.LED_intensity==0,facecolor = 'k', alpha = 0.5)
##
###    for ii in range(len(RisingEdge)):
###        ax1.fill_between(OrgTrack1.Time[RisingEdge[ii]:FallingEdge[ii]],y1=np.max(OrgTrack1.ZobjWheel),y2 =0,color = 'gold',alpha = 0.5)
###        ax1.fill_between(OrgTrack1.Time,y1=np.max(OrgTrack1.ZobjWheel),y2 =0,where = OrgTrack1.LED_intensity>0,facecolor = 'gold',facealpha = 0.5)
###        ax1.fill_between(OrgTrack1.Time,y1=np.max(OrgTrack1.ZobjWheel),y2 =0,where = OrgTrack1.LED_intensity==0,facecolor = 'k', facealpha = 0.5)
##
##    ax1.plot(OrgTrack1.Time, OrgTrack1.ZobjWheel, 'b-', linewidth = 2)
##
##        
##    ax1.set_xlabel('Time (s)')
##    ax1.set_ylabel('Z displacement (mm)', color='b')
##    
##    ax1.set_xlim([0, np.max(OrgTrack1.Time)])
##    ax1.set_ylim([0, np.max(OrgTrack1.ZobjWheel)])
##    
##    ax1.legend(custom_line, ['Light ON', 'Light OFF'])
##
##    plt.show()
#    
#    #------------------------------------------------------------------------------
#    Z_fast = OrgTrack1.ZobjWheel - Z_movingAvg
#    #------------------------------------------------------------------------------
#    # Plot of the Signal - Moving average
#    #------------------------------------------------------------------------------
##    fig, ax1 = plt.subplots()
##
##  
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast), where = OrgTrack1.LED_intensity>0,facecolor = 'gold', alpha = 0.5)
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast),where = OrgTrack1.LED_intensity==0,facecolor = 'k', alpha = 0.2)
##    ax1.plot(OrgTrack1.Time, Z_fast , 'b-', linewidth = 2)
##
##    
##        
##    ax1.set_xlabel('Time (s)')
##    ax1.set_ylabel('Z - Z(avg) (mm)', color='b')
##    
##    ax1.legend(custom_line, ['Light ON', 'Light OFF'])
##    ax1.set_xlim([0, np.max(OrgTrack1.Time)])
##    ax1.set_ylim([np.min(Z_fast), np.max(Z_fast)])
##    plt.show()
#    
#    #------------------------------------------------------------------------------
#    # Align the responses for all Dark to Light transitions
#    #------------------------------------------------------------------------------
##    fig, ax = plt.figure()
##    
##    for ii in range(len(RisingEdge)):
##        
##        ax.scatter(OrgTrack1.T[RisingEdge[ii]-100])
#        
#    fig, ax1 = plt.subplots()
#
#  
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast), where = OrgTrack1.LED_intensity>0,facecolor = 'gold', alpha = 0.5)
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast),where = OrgTrack1.LED_intensity==0,facecolor = 'k', alpha = 0.2)
##    ax1.plot(OrgTrack1.Time, OrgTrack1.ZobjWheel , 'b-', linewidth = 2)
#    
#    ax1.plot(OrgTrack1.Time, OrgTrack1.ZobjWheel , 'b-', linewidth = 2)
#
#    ax2 = ax1.twinx()
#    
#    ax2.plot(OrgTrack1.Time, OrgTrack1.LED_intensity, color = 'gold')
#    
#        
#    ax1.set_xlabel('Time (s)')
#    ax1.set_ylabel('V_Z (mm/s)', color='b')
#    ax2.set_ylabel('LED intensity')
#    
##    ax1.legend(custom_line, ['Light ON', 'Light OFF'])
##    ax1.set_xlim([0, np.max(OrgTrack1.Time)])
##    ax1.set_ylim([np.min(Z_fast), np.max(Z_fast)])
#    plt.show()
#    
#    fig, ax1 = plt.subplots()
#
#  
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast), where = OrgTrack1.LED_intensity>0,facecolor = 'gold', alpha = 0.5)
##    ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast),where = OrgTrack1.LED_intensity==0,facecolor = 'k', alpha = 0.2)
##    ax1.plot(OrgTrack1.Time, OrgTrack1.Xobj , 'r-', linewidth = 2)
#    
#    ax1.plot(OrgTrack1.Time, OrgTrack1.Vx , 'b-', linewidth = 2)
#
#    ax2 = ax1.twinx()
#    
#    ax2.plot(OrgTrack1.Time, OrgTrack1.LED_intensity, color = 'gold')
#    
#        
#    ax1.set_xlabel('Time (s)')
#    ax1.set_ylabel('V_x (mm/s)', color='b')
#    ax2.set_ylabel('LED intensity')
#    
##    ax1.legend(custom_line, ['Light ON', 'Light OFF'])
##    ax1.set_xlim([0, np.max(OrgTrack1.Time)])
##    ax1.set_ylim([np.min(Z_fast), np.max(Z_fast)])
#    plt.show()
        
        
    
#    plt.figure()
#    plt.scatter (OrgTrack1.Time[OrgTrack1.LED_intensity>0], OrgTrack1.Z[OrgTrack1.LED_intensity>0],10, color='r')
#    plt.xlabel('Time (s)')
#    plt.ylabel('Focus measure')
#    plt.show()
    
#    OrgTrack1.plot3DComponents(OrgTrack1.X,OrgTrack1.Y,OrgTrack1.Z, plotPeaks=0,labels=1, save = 1)
#    OrgTrack1.plot3DComponents(OrgTrack1.X,OrgTrack1.Y,OrgTrack1.Z, plotPeaks=0,labels=0, save = 1)

    
    # Plot the focus measure as a function of time.
#    figure()
#    plt.scatter(OrgTrack1.Time, OrgTrack1.focusMeasure,s = 40, facecolors = 'none', edgecolors = 'r',linestyle='-')
#    plt.plot(OrgTrack1.Time, OrgTrack1.smoothSignal(OrgTrack1.focusMeasure,2),color='k',linewidth=2)
#    plt.xlabel('Time (s)')
#    plt.ylabel('Focus measure')
#    plt.show()
#    plt.
    
#    OrgTrack1.plotAlignedBlinks(labels=1)
#    OrgTrack1.plotAlignedBlinks(labels=0)
    
#    TimeBetweenBlinks = np.zeros(len(OrgTrack1.peaks)-1)
#    BlinkDurations= np.zeros_like(OrgTrack1.peaks)
#    
#    BlinkDurations = OrgTrack1.T[OrgTrack1.peak_indicator_neg] - OrgTrack1.T[OrgTrack1.peak_indicator]
#    
#    print(BlinkDurations)
#    
#    plt.figure()
#    plt.plot(OrgTrack1.T,Z_fast,'k-')
#    plt.scatter(OrgTrack1.T[OrgTrack1.peak_indicator],Z_fast[OrgTrack1.peak_indicator],10,color='r')
#    plt.scatter(OrgTrack1.T[OrgTrack1.peak_indicator_neg],Z_fast[OrgTrack1.peak_indicator_neg],20,color='g')
#
#    
#    for ii in range(len(OrgTrack1.peaks)-1):
#        TimeBetweenBlinks[ii] = OrgTrack1.T[OrgTrack1.peaks[ii+1]] - OrgTrack1.T[OrgTrack1.peaks[ii]]
#        
#    
#    print(len(OrgTrack1.T[OrgTrack1.peak_indicator]))
#    
#    
#    plt.figure()
#    plt.scatter(OrgTrack1.T[OrgTrack1.peak_indicator][:-1], TimeBetweenBlinks, color = 'r')
#    plt.scatter(OrgTrack1.T[OrgTrack1.peak_indicator], BlinkDurations, color = 'g')
#    plt.show()
#
#
#    saveFile = os.path.join(saveFolder, OrgTrack1.Organism+'_Blink_Statistics.pkl')
#    
#    with open(saveFile, 'wb') as f:
#        pickle.dump((OrgTrack1.T, OrgTrack1.peak_indicator, OrgTrack1.peak_indicator_neg, TimeBetweenBlinks, BlinkDurations),f)
    


    
#    Tmin = 0
#    Tmax = 3600
##    OrgTrack1_full = Track.GravMachineTrack(fullPath,file,0,0)
#    computeNew = 0
#    if(not os.path.exists(saveFile) or computeNew == 1):
#        OrgTrack1 = Track.GravMachineTrack(fullPath,file,Tmin,Tmax)
#        X_smooth, Y_smooth, Z_smooth = OrgTrack1.smoothTrack(10)
##        OrgTrack1.plotTrackWalls(walls=1)
##        
        ####--------------------------------------------------------------------------
        ####    Reset the smoothing window for the data to the original window
        ####--------------------------------------------------------------------------
#        OrgTrack1.smoothTrack(OrgTrack1.window_time)
#        Time = OrgTrack1.T
#        Z = OrgTrack1.Z
#        Z_fast = Z - Z_smooth
#        Z_fast_smooth = OrgTrack1.smoothSignal(Z_fast,10)
#        
#        with open(saveFile, 'wb') as f:  # Python 3: open(..., 'wb')
#            pickle.dump((OrgTrack1.T, OrgTrack1.Z, Z_fast, Z_fast_smooth), f)
#    else:
#        with open(saveFile,'rb') as f:
#            Time, Z, Z_fast, Z_fast_smooth = pickle.load(f)
#        
#    samplingFreq = 1/(Time[1]-Time[0])
    
    
#    OrgTrack1.plot3DComponents(OrgTrack1.X_smooth,OrgTrack1.Y_smooth,OrgTrack1.Z_smooth)
#    OrgTrack1.plotTrackWalls(walls=1)
#    
##    OrgTrack1.plot3DComponents(self.X_smooth, self.Y_smooth, self.Z_smooth,)
#    
#    plt.figure()
##    plt.plot(Time,Z_fast)
#    plt.plot(Time,Z,'k-')
#    plt.plot(Time,Z_smooth,'r-')
#    
#    plt.figure()
##    plt.plot(Time,Z_fast)
#    plt.plot(Time,Z_fast,'k-')
#    
#    
#    peaks = find_peaks_dendraster(Time,Z_fast)
#
#    print(len(peaks))
#    peaks_neg = find_peaks_dendraster(Time,-Z_fast)
#    
#    
#    
#    peak_indicator=[0 for i in range(len(Time))]
#    
#    for j in peaks:
#        peak_indicator[j]= 1
#        
#    peak_indicator_neg=[0 for i in range(len(Time))]
#    
#    for j in peaks_neg:
#        peak_indicator_neg[j] = 1
#
#    peak_indicator = np.array(peak_indicator, dtype='bool')
#    peak_indicator_neg = np.array(peak_indicator_neg, dtype='bool')
#    indexArray = np.array([i for i in range(len(Time))],dtype='int')
#
#    print('Number of Positive Peaks: {}'.format(len(peaks)))
#    print('Number of Negative Peaks: {}'.format(len(peaks_neg)))
#    
#    TimeBetweenBlinks = np.zeros(len(peaks)-1)
#    BlinkIntervals = np.zeros_like(peaks)
#    
#    BlinkIntervals = Time[peak_indicator_neg] - Time[peak_indicator]
#    
#    print(BlinkIntervals)
#    
#    plt.figure()
#    plt.plot(Time,Z_fast,'k-')
#    plt.scatter(Time[peak_indicator],Z_fast[peak_indicator],10,color='r')
#    plt.scatter(Time[peak_indicator_neg],Z_fast[peak_indicator_neg],20,color='g')
#
#    
#    for ii in range(len(peaks)-1):
#        TimeBetweenBlinks[ii] = Time[peaks[ii+1]] - Time[peaks[ii]]
#        
#    
##    plt.figure()
###    plt.plot(Time,10*Z_fast,'r-')
###    plt.scatter(Time[peak_indicator],Z_fast_smooth[peak_indicator],10,color='r')
##
##    plt.plot(OrgTrack1.T, OrgTrack1.Z,'k-')
##    plt.scatter(OrgTrack1.T[peak_indicator],OrgTrack1.Z[peak_indicator],10,color='r')
##    
##    for ii in indexArray[peak_indicator]:
##        plt.vlines(Time[ii],np.floor(Z.min())-1,Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='g')
###    
##    for ii in indexArray[peak_indicator_neg]:
##        plt.vlines(Time[ii],np.floor(Z.min())-1,Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='r')
##    
##    plt.xlim( Time[0],Time[-1])
##    plt.ylim( 0,np.ceil(Z.max()+1))
##    plt.savefig(os.path.join(OrgTrack1.savePath,TrackName+'_Blink_Detection.svg'))
#
#    
#    OrgTrack1.plot3DComponents(OrgTrack1.X, OrgTrack1.Y, OrgTrack1.Z, peaks= peaks)
#
#    
#    
##    
##    
##    print(TimeBetweenBlinks)
##    
#    plt.figure()
#    plt.plot(Time[peaks[:-1]],TimeBetweenBlinks,color = 'r',Marker = 'o')
#    plt.show()
##    
##    
#    plt.figure()
#    plt.hist(TimeBetweenBlinks,bins = 20,density = True)
#    plt.xlabel('Time between blinks (s)')
#    plt.ylabel('Probability density')
#    plt.show()
###    
###    plt.figure()
###    plt.hist(BlinkIntervals,bins = 20,density = True)
###    plt.xlabel('Blink duration (s)')
###    plt.ylabel('Probability density')
###    plt.show()
##
##    for ii in indexArray[peak_indicator]:
##        plt.vlines(Time[ii],np.floor(Z.min())-1,Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='g')
##    
##    for ii in indexArray[peak_indicator_neg]:
##        plt.vlines(Time[ii],np.floor(Z.min())-1,Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='r')
#        
#
#    plt.figure()
#    
#    plt.plot(Time, Z , color = 'k', linewidth = 2)
#    for ii in range(len(peaks)):
#        plt.fill_between(Time[peaks[ii]:peaks_neg[ii]],Z[peaks[ii]:peaks_neg[ii]],y2 =0,color = 'r',alpha = 0.5)
#        
#    #plt.plot(Time, Z_movAvg, color='r')
##    plt.scatter(Time[peak_indicator],Z[peak_indicator], 50, color='r',label='blink')
#    plt.title('"Blink" detection')
##    plt.legend()
#    plt.xlim( Time[0],Time[-1])
#    plt.ylim(0,np.ceil(Z.max()+1))
#    plt.savefig(os.path.join(OrgTrack1.savePath,TrackName+'_Blink_Detection.svg'))
#    
#    plt.show()
#    
#    
#    # Save the data to get the ensemble statistics
#    saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
#    saveFile = os.path.join(saveFolder, OrgTrack1.Organism+'_Blink_Statistics.pkl')
#    
#    with open(saveFile, 'wb') as f:
#        pickle.dump((Time, peak_indicator, peak_indicator_neg, TimeBetweenBlinks, BlinkIntervals),f)
    
##    ##--------------------------------------------------------------------------
#    
#    # Create a signal with Gaussian pulses at the peaks
#    PulseAtPeaks = GaussianPulseAtPeaks(time = Time, samplingFreq = samplingFreq, pulseWidth_time = BlinkIntervals, Peaks = peaks)
#
##    PulseAtPeaks = PulseAtPeaks + 0.01*np.random.randn(len(Time))
##    ##--------------------------------------------------------------------------
 
##    plt.scatter(Time[peak_indicator],Z_fast_smooth[peak_indicator],10,color='r')
##    plt.scatter(Time[peak_indicator_neg],Z_fast_smooth[peak_indicator_neg],50,color='g',alpha = 0.5)
#    
#    plt.plot(Time,Z,'k-')
#    plt.scatter(Time[peak_indicator],Z[peak_indicator],10,color='r')
#    plt.scatter(Time[peak_indicator_neg],Z[peak_indicator_neg],10,color='g',alpha = 0.5)
#
#    plt.show()
##    ##--------------------------------------------------------------------------
#   
#    plt.figure()
#    plt.plot(Time, PulseAtPeaks)
#    plt.show()
    
    ##--------------------------------------------------------------------------
    # Correlogram analysis of the blinks
    ##--------------------------------------------------------------------------
     #======================================================================
#    # Autocorrelation
#    #======================================================================
#    ##--------------------------------------------------------------------------
#    # Create a fw test functions to check the autocorrelation methods
#    ##--------------------------------------------------------------------------
#    # A signal with Gaussian pulses at specific intervals:
#    Tmax = 100
#    pulseInterval_time = 10 # Pulse interval in seconds
#    pulseWidth_time = 2    # Width of the pulse in seconds
#
#    samplingFreq = 20
#    
#    TimeTest = np.linspace(0,Tmax, samplingFreq*Tmax)
#    
#    Flag1 = int(Tmax/3)
#    Flag2= int(2*Tmax/3)
#    pulseInterval_time1 = 5
#    pulseInterval_time2 = 2 
#    
#    Peaks = np.zeros_like(TimeTest,dtype='bool')
#    
#    for ii, time in enumerate(TimeTest):
#        
#        if(time<Flag1 and ii%int(samplingFreq*pulseInterval_time1)==0):
#            Peaks[ii] = 1
#        elif(time>Flag1 and time<Flag2 and ii%int(samplingFreq*pulseInterval_time2)==0):
#            Peaks[ii] = 1
#        elif(time>Flag2 and ii%int(samplingFreq*pulseInterval_time1)==0):
#            Peaks[ii] = 1
#            
#    
#            
#    plt.figure()
#    plt.plot(TimeTest, Peaks)
            
                
                
        
    
    
#    GaussianPulse1 = GaussianPulse(time = TimeTest, samplingFreq = samplingFreq, pulseInterval_time = pulseInterval_time, pulseWidth_time = pulseWidth_time)
    
#    pulseInterval_time = 2 # Pulse interval in seconds
#    pulseWidth_time = 2    # Width of the pulse in seconds
    
#    GaussianPulse2 = GaussianPulse(time = TimeTest, samplingFreq = samplingFreq, pulseInterval_time = pulseInterval_time, pulseWidth_time = pulseWidth_time)
    
#    signalGaussPulse = GaussianPulse1 +  GaussianPulse2
    
#    signalGaussPulse = randomGaussPulse(time = TimeTest, samplingFreq = samplingFreq, pulseWidth_time = pulseWidth_time)
    
    # Gaussian Pulses at the location specified by Peaks
    
#    signalGaussPulse = GaussianPulseAtPeaks(time = TimeTest, samplingFreq = samplingFreq, pulseWidth_time= 0.1, Peaks = Peaks)
    
    
    
#    Amp1 = 1
#    Amp2 = 0
#    signalGaussPulse = Amp1*signalGaussPulse + Amp2*np.random.randn(len(TimeTest))
#    # Frequency of the underlying Sine wave in Hz
#    signalFreq = 0.1
#    Amp1 = 0.1
#    Amp2 = 1
#    signalHiddenSin = Amp1*np.random.randn(len(TimeTest)) + Amp2*np.sin(2*np.pi*signalFreq*TimeTest)
    
    # PLOT the test signal
    
#    signalGaussPulse = GaussianPulseAtPeaks(time = Time, samplingFreq = samplingFreq)
    
#    plt.figure()
#    plt.plot(TimeTest, signalGaussPulse, color = 'r')
##    plt.plot(TimeTest, signalHiddenSin, color = 'k')
#    plt.show()
    
    
    
#    ##--------------------------------------------------------------------------
   
    

    
    
    
#    Time = TimeTest
#    dataSignal = signalGaussPulse
#    
   

#    
#    R = autocorrelation( dataSignal, minLag, maxLag)
#    
#    print(R, maxLag)
#    
#    
#    
#    f = plt.figure()
#    ax0 = plt.subplot(121)
#    plt.plot(Time, dataSignal,color='r')
#    plt.title('test Signal')
#    
#    ax1 = plt.subplot(122)
#    plt.scatter(LagArray,R,20)
#    plt.xlabel('lag')
#    plt.ylabel('Autocorrelation R(t)')
#    plt.title('Auto-correlation of signal')
#    
#    ###============================================================================
###               Windowed auto-correlation or Rhythmogram:
####============================================================================
#    dataSignal = Z_fast_smooth
#    print(50*'*')
#    print('Sampling Frequency (Hz): {}'.format(samplingFreq))
#    print(50*'*')
#    
#    start_Time = np.min(Time)
#    stop_Time = np.max(Time)
#    
#    start = int(start_Time*samplingFreq)
#    stop = int(stop_Time*samplingFreq)
#    
#    minLagTime = 0
#    maxLagTime = 400  # Max lag time in seconds
#    minLag = int(minLagTime*samplingFreq)
#    maxLag = int(maxLagTime*samplingFreq)
#    
#    LagArray = np.array([i for i in range(minLag,maxLag)])*(1/samplingFreq)
#
#    
#    window_time = 150 # Window size in seconds. 
#    window = int(window_time*samplingFreq) # Window size in indices
#    
#    stepSize_time = 30 # Step size or time resolution of the Rhytmogram
#    stepSize = int(stepSize_time*samplingFreq)
#    
#    Rhythmogram, LagArray, TimeArray = autocorrelation_window(data = dataSignal, minLag = minLag, maxLag = maxLag, start = start, stop = stop, window = window, stepSize = stepSize)
#    
# 
#    
#    TimeIndices = np.array([i for i in range(start,stop - window - maxLag,stepSize)])
#    TimeArray_time = TimeArray *(1/samplingFreq)
#    LagArray_time = LagArray*(1/samplingFreq)
#    #======================================================================
#    # Plot the Rhytmogram
#    #======================================================================
#    
#    f = plt.figure(figsize =(12,6),dpi=150)
#    ax0 = plt.subplot(121)
##    plt.plot(T[:max(TimeIndices)+maxLag],signal[:max(TimeIndices)+maxLag],color='r')
#    plt.plot(Time,dataSignal,color='r')
#    plt.title('Signal')
#    
#    ax1 = plt.subplot(122)
#    #plt.contourf(TimeGrid,LagGrid,Rhythmogram)
##    plt1 = plt.imshow(Rhythmogram, aspect = 'auto', cmap = plt.get_cmap('inferno'),origin='lower')
#
##    plt.plot(Time[peaks[:-1]],TimeBetweenBlinks,color = 'k',Marker = 'o')
#    plt1 = plt.imshow(Rhythmogram, extent = (min(TimeArray_time), max(TimeArray_time), min(LagArray_time), max(LagArray_time)), aspect = 'auto', cmap = plt.get_cmap('inferno',16),origin='lower')
#    
#    cbar = plt.colorbar(plt1)
#    cbar.ax.set_ylabel('Auto-Correlation')
#    plt.ylabel('Lag')
#    plt.xlabel('Time (s)')
#    plt.savefig(os.path.join(resultFolder,TrackName+'_Signal_Rhythmogram.svg'))
#
#    plt.title('Rhythmogram of signal')
#    
#    
#    
#    f = plt.figure(figsize =(8,6),dpi=150)
#
#    plt1 = plt.imshow(Rhythmogram, extent = (min(TimeArray_time), max(TimeArray_time), min(LagArray_time), max(LagArray_time)), aspect = 'auto', cmap = plt.get_cmap('inferno',16),origin='lower')
#    
#    cbar = plt.colorbar(plt1)
#    cbar.ax.set_ylabel('Auto-Correlation')
#    plt.ylabel('Lag')
#    plt.xlabel('Time (s)')
#    plt.savefig(os.path.join(resultFolder,TrackName+'_Rhythmogram.svg'))
#
#    plt.title('Rhythmogram of signal')
#    plt.show()
        
    
    
    
    
 
#    
#    freq,peaks=OrgTrack1.find_freq(Z_fast)
#    
#    print(peaks)
    
    
    
#    OrgTrack1.plotTrackWalls(peaks)
#    OrgTrack1.plot3DComponents(OrgTrack1.X,OrgTrack1.Y,OrgTrack1.Z,peaks)
   
        
        
        
        
        

    
    
    

#if __name__ == '__main__':
#    main()
    
    
    

#
#

#   

###--------------------------------------------------------------------------
###                           Correlogram of the Tracks
###--------------------------------------------------------------------------
#
###--------------------------------------------------------------------------
#
#


#
###-----------------------------------------------------------------------------
#        # Choose the signal to analyze
###---------------------------------------------------------------------
#signal = Z
#
###--------------------------------------------------------------------------
#minLagTime = 0
#maxLagTime = 50    # Max lag time in seconds
#minLag = int(minLagTime*samplingFreq)
#maxLag = int(maxLagTime*samplingFreq)
#
#start_time = 0
#stop_time = 200
#
#start = int(start_time*samplingFreq)
#stop = int(stop_time*samplingFreq)
#
#
#
#R = autocorrelation(signal, minLag, maxLag)
#
#print(R, maxLag)
#
#
#LagArray = np.array([i for i in range(minLag,maxLag)])*(1/samplingFreq)
#
#f = plt.figure()
#ax0 = plt.subplot(121)
#plt.plot(T,signal,color='r')
#plt.title('test Signal')
#
#ax1 = plt.subplot(122)
#plt.scatter(LagArray,R,20)
#plt.xlabel('lag')
#plt.ylabel('Autocorrelation R(t)')
#plt.title('Auto-correlation of signal')
#
###============================================================================
##               Windowed auto-correlation or Rhythmogram:
###============================================================================
#
##window_time = 10 # Window size in seconds. 
##window = int(window_time*samplingFreq)
##
##stepSize_time = 1 # Step size or time resolution of the Rhytmogram
##stepSize = int(stepSize_time*samplingFreq)
##
##Rhythmogram = autocorrelation_window(signal, minLag, maxLag, start, stop, window, 1)
##
##TimeIndices = np.array([i for i in range(start,stop - window - maxLag,stepSize)])
##TimeArray = TimeIndices*(1/samplingFreq)
##
##  
##
##
### Plot the Rhytmogram
##
##f = plt.figure()
##ax0 = plt.subplot(121)
##plt.plot(T[:max(TimeIndices)+maxLag],signal[:max(TimeIndices)+maxLag],color='r')
##plt.title('Signal')
##
##ax1 = plt.subplot(122)
###plt.contourf(TimeGrid,LagGrid,Rhythmogram)
##plt1 = plt.imshow(Rhythmogram, extent = (min(TimeArray), max(TimeArray), min(LagArray), max(LagArray)), aspect = 'auto', cmap = plt.get_cmap('inferno'),origin='lower')
##
##cbar = plt.colorbar(plt1)
##cbar.ax.set_ylabel('Flow velocity magnitude (mm/s)')
##plt.ylabel('lag')
##plt.xlabel('Time (s)')
##plt.title('Rhythmogram of signal')
# 