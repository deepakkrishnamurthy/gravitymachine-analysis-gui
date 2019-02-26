#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 15:02:45 2018

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
import seaborn as sns
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
rcParams.update({'font.size': 18})
#==============================================================================
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

dataFolder ='/Volumes/GRAVMACH1/VolvoxPhotoresponse/vvx25'


file = "track.csv"

*rest,orgName = os.path.split(dataFolder)
saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'




print(50*'*')
print('Folder in which to save data: {}'.format(dataFolder))
print(50*'*')


#======================================================================
# Plots of Tracks
#======================================================================
Tmin = 0
Tmax = 0
OrgTrack1 = Track.GravMachineTrack(dataFolder,file,Tmin,Tmax)

ImageFolder = '/Volumes/GRAVMACH1/VolvoxPhotoresponse/vvx25/images00012'
saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/Figures/Figure6/Volvox_RisingEdge'

if (not os.path.exists(saveFolder)):
    os.makedirs(saveFolder)
    
#OrgTrack1.makeMovie(ImageFolder, saveFolder)



custom_line = [Line2D([0], [0], color='gold', lw=4), Line2D([0], [0], color='k', lw=4) ]


RisingEdge = []
FallingEdge = []
counter = 0
for ii in range(OrgTrack1.trackLen - 1):
    if(OrgTrack1.LED_intensity[ii]==0 and OrgTrack1.LED_intensity[ii+1]>0):
       
        RisingEdge.append(ii)
        counter += 1
            
    elif(OrgTrack1.LED_intensity[ii]>0 and OrgTrack1.LED_intensity[ii+1]==0):
        FallingEdge.append(ii)
        
RisingEdge = np.array(RisingEdge)
FallingEdge = np.array(FallingEdge)

Index = []
Index_falling  = []
for ii in range(len(RisingEdge)-1):
    
    if(RisingEdge[ii+1] - RisingEdge[ii] > 100):
        Index.append(ii+1)
        
        
RisingEdge = RisingEdge[Index]

for ii in range(len(FallingEdge)):
    
    nearestRisingEdge = find_nearest(RisingEdge, FallingEdge[ii])
    
    if(abs(FallingEdge[ii]-nearestRisingEdge) > 200):
        Index_falling.append(ii)

        
FallingEdge = FallingEdge[Index_falling]



OrgTrack1.ZobjWheel = OrgTrack1.ZobjWheel - OrgTrack1.ZobjWheel[0]



Z_movingAvg = OrgTrack1.smoothSignal(OrgTrack1.ZobjWheel,20)


## Moving avg of the vertical velocity
Tmin = 0
Tmax = 4030
mask = np.array(OrgTrack1.Time>=Tmin, dtype='bool') & np.array(OrgTrack1.Time<=Tmax, dtype = 'bool')

#------------------------------------------------------------------------------
# Volvox phototaxis plots
#------------------------------------------------------------------------------
# Plots of displacement vs time
#------------------------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(6,4))

ax1.fill_between(OrgTrack1.Time[mask],y1=np.max(OrgTrack1.ZobjWheel[mask])+0.1,y2 = np.min(OrgTrack1.ZobjWheel[mask])-0.1, where = OrgTrack1.LED_intensity[mask]>0,facecolor = 'gold', alpha = 0.4)
ax1.fill_between(OrgTrack1.Time[mask],y1=np.max(OrgTrack1.ZobjWheel[mask])+0.1,y2 = np.min(OrgTrack1.ZobjWheel[mask])-0.1,where = OrgTrack1.LED_intensity[mask]==0,facecolor = 'k', alpha = 0.4)
ax1.plot(OrgTrack1.Time[mask], OrgTrack1.ZobjWheel[mask] , 'b-', linewidth = 2)
#ax1.plot(OrgTrack1.Time[0:-1], OrgTrack1.Vz , 'b', linewidth = 1)



    
#ax1.set_xlabel('Time (s)')
#ax1.set_ylabel('Z (mm)', color='b')

#ax1.legend(custom_line, ['Light ON', 'Light OFF'])
ax1.set_aspect(2.5)
#ax1.set_xticks(range(Tmin, Tmax,5))
ax1.set_xlim([np.min(OrgTrack1.Time[mask]), np.max(OrgTrack1.Time[mask])])
ax1.set_ylim([np.min(OrgTrack1.ZobjWheel[mask])-0.1, np.max(OrgTrack1.ZobjWheel[mask])+0.1])
plt.show()
#    
#------------------------------------------------------------------------------
Z_fast = OrgTrack1.ZobjWheel - Z_movingAvg
#------------------------------------------------------------------------------
# Plot of the Signal - Moving average
#------------------------------------------------------------------------------
fig, ax1 = plt.subplots()

  
ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast), where = OrgTrack1.LED_intensity>0,facecolor = 'gold', alpha = 0.4)
ax1.fill_between(OrgTrack1.Time,y1=np.max(Z_fast),y2 =np.min(Z_fast),where = OrgTrack1.LED_intensity==0,facecolor = 'k', alpha = 0.4)
ax1.plot(OrgTrack1.Time, Z_fast , 'b-', linewidth = 2)
ax1.plot(OrgTrack1.Time[FallingEdge], Z_fast[FallingEdge], 'ro')


    
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Z - Z(avg) (mm)', color='b')

ax1.legend(custom_line, ['Light ON', 'Light OFF'])
ax1.set_xlim([0, np.max(OrgTrack1.Time)])
ax1.set_ylim([np.min(Z_fast), np.max(Z_fast)])
plt.show()
#
##------------------------------------------------------------------------------
## Plot of the Vertical velocity vs Time
##------------------------------------------------------------------------------

Vz_smooth = OrgTrack1.smoothSignal(OrgTrack1.Vz,OrgTrack1.window_time)

Vz_smooth = np.insert(Vz_smooth,0,np.nan)

fig, ax1 = plt.subplots(figsize=(6,4))


  
ax1.fill_between(OrgTrack1.Time[mask],y1=np.nanmax(Vz_smooth[mask])+0.1,y2 = np.nanmin(Vz_smooth[mask])-0.1, where = OrgTrack1.LED_intensity[mask]>0,facecolor = 'gold', alpha = 0.4)
ax1.fill_between(OrgTrack1.Time[mask],y1=np.nanmax(Vz_smooth[mask])+0.1,y2 = np.nanmin(Vz_smooth[mask])-0.1,where = OrgTrack1.LED_intensity[mask]==0,facecolor = 'k', alpha = 0.4)
ax1.plot(OrgTrack1.Time[mask], Vz_smooth[mask] , 'k', linewidth = 2)
#ax1.plot(OrgTrack1.Time[0:-1], OrgTrack1.Vz , 'b', linewidth = 1)



    
#ax1.set_xlabel('Time (s)')
#ax1.set_ylabel('Vz (mm)', color='b')

#ax1.legend(custom_line, ['Light ON', 'Light OFF'])
ax1.set_xlim([np.nanmin(OrgTrack1.Time[mask]), np.nanmax(OrgTrack1.Time[mask])])
ax1.set_ylim([np.nanmin(Vz_smooth[mask])-0.1, np.nanmax(Vz_smooth[mask])+0.1])
#ax1.set_xticks(range(Tmin, Tmax,5))
plt.show()

#------------------------------------------------------------------------------
# Create a dataframe with all the behavioral events aligned at the Rising Edge and Falling Edge
#------------------------------------------------------------------------------
#T_window = 20
#
#nWindow = math.ceil(int(T_window*OrgTrack1.samplingFreq)/2.)*2
#T_blink = np.zeros(nWindow)
#
#nBlinks = len(RisingEdge)
#
#print('No:of blinks: {}'.format(nBlinks))
#color = plt.cm.inferno(np.linspace(0, 1,nBlinks))
#    
##    color = cmocean.cm.algae(np.linspace(0, 1,nBlinks))
#
#plt.rcParams['axes.prop_cycle'] = cycler.cycler('color', color)
#
#Vz_blink = np.zeros((nBlinks,nWindow),dtype='float')
#plt.figure(3)
#for i,peakIndex in enumerate(RisingEdge):
#    
#    lower_index = peakIndex - int((1/2)*nWindow)
#    upper_index = peakIndex + int((1/2)*nWindow)
#    if(lower_index>=0 and upper_index<OrgTrack1.trackLen):
#        T_blink = OrgTrack1.Time[lower_index:upper_index] - OrgTrack1.Time[peakIndex]
##        Z_blink[i,:] = Z_fast[lower_index:upper_index] - Z_fast[peakIndex]
#        Vz_blink[i,:] = Vz_smooth[lower_index:upper_index] - Vz_smooth[peakIndex]
#
#
#df = pd.DataFrame({'Time': [], 'Vz':[]})
#        
#for ii in range(len(RisingEdge)):
#    df = df.append(pd.DataFrame({'Time':T_blink, 'Blink Number':np.repeat(ii, len(T_blink),axis=0),'Vz':np.transpose(Vz_blink[ii,:])}))
#    
#    
#palette = sns.color_palette("Blues", len(RisingEdge))
#
#
#print(df)
#
#plt.figure()
#
#
#ax = sns.lineplot(x = 'Time',y = 'Vz', ci=95,data = df, lw = 3, palette = palette, legend = False)
#
##ax.set_aspect(1)
#
#plt.show()
##
###------------------------------------------------------------------------------
### Create a dataframe with all the behavioral events aligned at the Falling Edge
###------------------------------------------------------------------------------
#nWindow = math.ceil(int(T_window*OrgTrack1.samplingFreq)/2.)*2
#T_blink = np.zeros(nWindow)
#
#nBlinks = len(FallingEdge)
#
#print('No:of blinks: {}'.format(nBlinks))
#color = plt.cm.inferno(np.linspace(0, 1,nBlinks))
#    
##    color = cmocean.cm.algae(np.linspace(0, 1,nBlinks))
#
#plt.rcParams['axes.prop_cycle'] = cycler.cycler('color', color)
#
#Vz_blink = np.zeros((nBlinks,nWindow),dtype='float')
#plt.figure(3)
#for i,peakIndex in enumerate(FallingEdge):
#    
#    lower_index = peakIndex - int((1/2)*nWindow)
#    upper_index = peakIndex + int((1/2)*nWindow)
#    if(lower_index>=0 and upper_index<OrgTrack1.trackLen):
#        T_blink = OrgTrack1.Time[lower_index:upper_index] - OrgTrack1.Time[peakIndex]
##        Z_blink[i,:] = Z_fast[lower_index:upper_index] - Z_fast[peakIndex]
##        Z_blink[i,:] = OrgTrack1.ZobjWheel[lower_index:upper_index] - OrgTrack1.ZobjWheel[peakIndex]
#        Vz_blink[i,:] = Vz_smooth[lower_index:upper_index] - Vz_smooth[peakIndex]
#
#
#df1 = pd.DataFrame({'Time': [], 'Blink Number': [], 'Vz':[]})
#        
#for ii in range(1,len(FallingEdge)-1):
#    df1 = df1.append(pd.DataFrame({'Time':T_blink, 'Blink Number':np.repeat(ii, len(T_blink),axis=0),'Vz':np.transpose(Vz_blink[ii,:])}))
#    
#    
#palette = sns.color_palette("Blues", len(FallingEdge)-2)
#
#plt.figure()
#
#
#ax = sns.lineplot(x = 'Time',y = 'Vz',ci=95,data = df1, lw = 3, palette = palette, legend = False)
#
##ax.set_aspect(1)
#
#plt.show()




    
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