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
import scipy.interpolate as interpolate
import pickle


def plot_spectrum(time, signal):
    
    from scipy import fftpack
    
    n = len(time)
    
    time_new = np.linspace(min(time), max(time), n)
    
    # Sampling freq
    f_s = float(1)/(time_new[1]-time_new[0])
    
    # Subtract the DC component of the signal
    signal = signal - np.nanmean(signal)
    
    func_signal = interpolate.interp1d(time,signal, kind = 'linear')
    
    signal_new = func_signal(time_new)
    
    X = fftpack.fft(signal_new)
    freqs = fftpack.fftfreq(len(signal_new)) * f_s
    
    fig, (ax1,ax2) = plt.subplots(nrows=2, ncols=1)

    ax1.plot(time_new, signal_new)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Signal')
    
    ax2.plot(freqs, np.abs(X))
    ax2.set_xlabel('Frequency in Hertz [Hz]')
    ax2.set_ylabel('Spectrum')
    ax2.set_xlim(0, f_s / 4)
    
    

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

 

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'

# Marine snow

#path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2'

#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/NewBead_2Hz_150um'

#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/ObjectMoving_0_5mm'

#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/LiquidLensMoving_0_5mm_1Hz'

#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/LensMoving_0_2Hz_500um'

#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/InFocus'
#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/FocusMeasure_BetweenObjectandInfty'
#path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/FocusMeasure_BetweenCameraAndObject'
path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking/PhaseTest'

Tmin = 0
Tmax = 0
###
track = GravityMachineTrack.gravMachineTrack(path, Tmin, Tmax)


# Plot the spectrum of the Focus-measure and Phase Signals signal to extract the actual frequency
plot_spectrum(track.df['Time'], np.sin(track.df['Liquid Lens Phase']))
plot_spectrum(track.df['Time'], track.df['Focus Measure'])

lens_amplitude = track.df['Liquid Lens Ampl'][0]
lens_freq = track.df['Liquid Lens Freq'][0]

print('Lens amplitude : {} mm'.format(lens_amplitude))

print('Lens frequency : {} Hz'.format(lens_freq))

# Phase-lag vs amplitude for the liquid lens

freq=[0.2,8,9,10,13.92,12.001,13,13.99,15,0.4999,0.9976,2.0002,3.0000,4.0001,5,6,6.9995]
phase_lag=[0.067,0.9173,0.9738,1.0315,1.0766,1.1163,1.1367,1.1812,1.1957,0.1335,0.2188,0.3655,0.5047,0.6294,0.7103,0.7759,0.8456]
phase_lag_funct=interpolate.interp1d(freq,phase_lag)
        




#plt.figure()
#plt.scatter(freq, phase_lag,10,color='b')
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('Phase lag (radians)')
#plt.show()

phase_lag=phase_lag_funct(lens_freq)

print('Phase lag : {} rads'.format(phase_lag))


color_index = np.linspace(0,1, track.trackLen)


print(lens_amplitude)

lens_displacement_computed = lens_amplitude*np.sin(track.df['Liquid Lens Phase'] - 1.5*phase_lag)

lens_displacement = track.df['Lens position']

#lens_displacement = lens_amplitude*np.sin(track.df['Liquid Lens Phase'] - 1.5*phase_lag)
#-------------------------------
# Measured lens displacement vs computed lens displacement
#-------------------------------
plt.figure()
plt.plot(track.df['Time'], lens_displacement, 'r-')
plt.plot(track.df['Time'], lens_displacement_computed, 'bo--')
plt.title('Lens displacement vs Time')
plt.show()

#-------------------------------
# Focus measure vs Time
#-------------------------------
plt.figure()
plt.plot(track.df['Time'], track.df['Focus Measure'], 'r-')
plt.title('Focus measure vs Time')
plt.show()
#-------------------------------
# Lens displacement vs Time
#-------------------------------
plt.figure()
plt.plot(track.df['Time'],lens_displacement, color='b',alpha=0.5, label='Lens displacement')
#plt.plot(track.df['Time'],track.df['Xobj'], color= 'b',alpha=0.5, label='Stage displacement')

plt.xlabel('Time (s)')
plt.ylabel('Lens displacement')
plt.title('Lens displacement vs Time')
plt.show()
#-------------------------------
# Focus-measure vs Phase
#-------------------------------
plt.figure()
plt.scatter(track.df['Liquid Lens Phase'], track.df['Focus Measure'], 20, color='r',alpha=0.5)
plt.title('Focus measure vs Phase')
plt.show()

#plt.figure()
#plt.scatter(lens_displacement, track.df['Focus Measure'], 20, color='b',alpha=0.5)
#plt.xlabel('mm')
#plt.ylabel('Focus measure')
#plt.title('Focus measure vs focal plane displacement')
#plt.show()

#-------------------------------
# Plot the lens displacement and Focus measure time series on top of each other
#-------------------------------
fig, ax1 = plt.subplots()

ax1.plot(track.df['Time'],lens_displacement, color='b',alpha=0.5, label='Lens displacement', linewidth=2)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Lens displacement', color = 'b')

ax2 = ax1.twinx()

ax2.plot(track.df['Time'], track.df['Focus Measure'], 'r-', label='Focus Measure', linewidth=2)


ax2.set_ylabel('Focus measure', color = 'r')

ax1.set_xlim([0,10])

#------------------------------------------------------------------------------
# For experiments where the X-stage is used to obtain the focus stack
#------------------------------------------------------------------------------
#-------------------------------
# Focus-measure vs lens-displacement OR stage-displacement
#-------------------------------
plt.figure()
#plt.scatter(track.df['Xobj']-track.df['Xobj'][0], track.df['Focus Measure'], 20, c=color_index, alpha=0.5)
plt.scatter(lens_displacement , track.df['Focus Measure'], 20, c=color_index, alpha=0.5)

plt.xlabel('Distance from object (mm)')
plt.ylabel('Focus measure')
plt.title('Focus measure vs focal plane displacement')
plt.show()



index = np.argsort(lens_displacement)

lens_disp_ordered = lens_displacement[index]

FM_ordered = track.df['Focus Measure'][index]


FM_diff = np.diff(FM_ordered)
Y_diff = np.diff(lens_disp_ordered)

print('Difference of FM ordered: {} '.format(sum(FM_diff)))





#linear fit of the data

p = np.polyfit(lens_displacement, track.df['Focus Measure'], deg = 2)

error = p[1]/(2*p[0])

print('Y error: {} '.format(error))

print('Slope: {}'.format(p[0]))
#-------------------------------
# Focus-measure vs lens-displacement OR stage-displacement
#-------------------------------
plt.figure()
#plt.scatter(track.df['Xobj']-track.df['Xobj'][0], track.df['Focus Measure'], 20, c=color_index, alpha=0.5)
plt.scatter(lens_disp_ordered , FM_ordered, 20, c=color_index, alpha=0.5)
plt.plot(lens_disp_ordered, p[0]*lens_disp_ordered**2 + p[1]*lens_disp_ordered + p[2], 'r-',label='Linear fit')
plt.xlabel('Distance from object (mm)')
plt.ylabel('Focus measure')
plt.title('Focus measure vs focal plane displacement (sorted)')
plt.show()



# Pickle the raw data so it can be plotted later
# Raw data to pickle: lens_displacement, FocusMeasure

#displacement = track.df['Xobj']-track.df['Xobj'][0]
#displacement = lens_displacement
#focus_measure = track.df['Focus Measure']
#saveFolder, saveFile = os.path.split(path)
#
#saveFile = saveFile + '.pkl'
#
#with open(os.path.join(saveFolder, saveFile),'wb') as f:
#    pickle.dump((displacement, focus_measure), f)
    


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
    



