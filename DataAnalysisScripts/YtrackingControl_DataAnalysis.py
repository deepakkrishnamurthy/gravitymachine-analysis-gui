# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 15:35:52 2018
Script to analyze the Y-tracking control data
@author: deepak90
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
import scipy.ndimage as ndimage
from roipoly import roipoly
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import pickle
plt.close("all")
from PIL import Image
import imp
import Track
imp.reload(Track)
import numpy as np
import csv_tool as csv
import pandas as pd
from matplotlib.ticker import FormatStrFormatter


def computeRelativeError(track):
   
    #YstageMoving = -(ThetaWheel - ThetaWheel[0])
    #YstageTracking = Yobjet - Yobjet[0]
    Time = track.Time - track.Time[0]
    YstageMoving = track.ThetaWheel - track.ThetaWheel[0]
    YstageTracking = track.Yobj - track.Yobj[0]
    SquaredError = (YstageMoving - YstageTracking)**2

    RMS_error = (np.mean(SquaredError))**(1/2)
    maxError = (np.mean(YstageMoving**2))**(1/2)
    
    plt.figure()

    plt.plot(Time, YstageMoving,color = 'k',label='Target stage')
    plt.scatter(Time, YstageTracking, 10,color='r',label = 'Tracking stage')
    
    plt.title('Lens amplitude {} mm, Lens gain: {}, Rel error: {} %'.format(track.liqLensAmp[0], track.liqLensGain[0],RMS_error))
    plt.xlabel('Elapsed Time (s)')
    plt.ylabel('Stage Displacement (mm)') 
    plt.legend()
    
    # Changed the error to just the RMS  error
    return RMS_error

#def main():
    
AmplitudeList = [0.05, 0.1, 0.15, 0.2]      # Rows
GainsList = [5, 10, 20, 50]           # Columns
df = pd.DataFrame(data = [], dtype='float')


print(df) 

rootFolder = '/Volumes/GRAVMACH1/GravityMachine/YTrackingControls_2018_10_24/Speed_250um_s'
#    rootFolder = 'Y:\Projects\GravityMachine\YTrackingControls_2018_10_24\Speed_250um_s's

trackFile = 'track.csv'

Folders = os.listdir(os.path.join(rootFolder))

for currFolder in Folders:
    
    currTrack = Track.GravMachineTrack(path = os.path.join(rootFolder, currFolder), file = trackFile )
    
    liqLensAmp = 2*currTrack.liqLensAmp[0]
    
    liqLensFreq = currTrack.liqLensFreq[0]
    
    liqLensGain = currTrack.liqLensGain[0]
    
    
    relError = computeRelativeError(currTrack)
    
    # Print the liquid lens parameters
    print('Liquid Lens Amplitude: {}'.format(liqLensAmp))
    print('Liquid Lens Frequency: {}'.format(liqLensFreq))
    print('Liquid Lens Max Gain: {}'.format(liqLensGain))
    print('Relative Tracking Error (%): {}'.format(100*relError))

    
    if(liqLensAmp in AmplitudeList and liqLensGain in GainsList):
#            df[liqLensGain][liqLensAmp] = []
        currDf = pd.DataFrame(data = relError,columns = [liqLensGain],index=[liqLensAmp])
        print(currDf)
        df = df.append(currDf)
        
        
  


df_mean = df.groupby(level=0).mean()
df_std = df.groupby(level=0).std()

print(type(df_mean))

print(df_mean)


RelErrors = np.array(df_mean.as_matrix())



Amplitudes = np.array(df_mean.index.values)
Gains = np.array(df_mean.columns.values)

Gains_matrix, Amp_matrix = np.meshgrid(Gains, Amplitudes)

fig, ax = plt.subplots()
im = ax.scatter(Gains_matrix, Amp_matrix, c = RelErrors, s = 250*RelErrors,vmin=np.min(RelErrors), vmax=np.max(RelErrors), cmap = plt.get_cmap('RdYlGn_r'))
#im = ax.contourf(Gains, Amplitudes, RelErrors, cmap = plt.cm.BuPu)
ax.set_xlabel('Liquid lens gain')
ax.set_label('Liquid lens amplitude (mm)')
cbar = fig.colorbar(im, ax=ax)
cbar.ax.set_ylabel('RMS Error')
ax.set_xscale('log')
ax.set_yscale('log')
#ax.set_ylim([0.04, 0.21])
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))

ax.set_xticks(ticks = [5, 10, 20, 50])
ax.set_yticks(ticks = [0.05, 0.1, 0.15, 0.5])
#plt.savefig('LiquidLens_TrackingError_logscale.svg',dpi=150)

    
        
        

    
    
    
    
    
    
#if __name__ == '__main__':
#    main()
