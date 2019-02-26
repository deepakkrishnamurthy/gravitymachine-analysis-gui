#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 14:05:36 2018

@author: deepak
"""

import numpy as np
import Track
import os
import imp
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
from cycler import cycler
import pickle
import matplotlib.cm as cm
import csv_tool as csv



def main():
    
    dataFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
    
    subFolder = 'Starfish_Blinks'
    
    saveFolder = dataFolder
    
    Files = os.listdir(os.path.join(dataFolder, subFolder))
    
#    Files = {0:'Dendraster1_Blink_Statistics.pkl',1:'Dendraster2_Blink_Statistics.pkl',2:'Dendraster3_Blink_Statistics.pkl'}

    
#    Files = {0:'Dendraster1_Blink_Statistics.pkl',1:'Dendraster2_Blink_Statistics.pkl',2:'Dendraster3_Blink_Statistics.pkl'}
    
#    Time = []
#    peak_indicator = []
#    peak_indicator_neg = []
#    TimeBetweenBlinks_array = []
#    BlinkDurations_array = []
    
    TimeBetweenBlinks_array = np.array([])
    BlinkDurations_array = np.array([])
    
    color1 = cm.inferno(64)
    color2 = cm.inferno(128)
    
    for fileNames in Files:
        
        print('Analyzing ... {}'.format(fileNames))
        with open(os.path.join(dataFolder,subFolder,fileNames),'rb') as f:
            
            Time, peak_indicator, peak_indicator_neg, TimeBetweenBlinks, BlinkDurations = pickle.load(f)
        
#        TimeBetweenBlinks_array.append(TimeBetweenBlinks)
a#        BlinkDurations_array.append(BlinkDurations)
            
        TimeBetweenBlinks_array = np.hstack((TimeBetweenBlinks_array, np.array(TimeBetweenBlinks)))
        
        BlinkDurations_array = np.hstack((BlinkDurations_array, np.array(BlinkDurations)))
        
    
    fig = plt.figure(figsize=(6,6), dpi = 150)
    
#    plt.subplot(121)
    n, bins, patches = plt.hist(TimeBetweenBlinks_array,bins = 'auto', density = True, facecolor = color1, edgecolor = 'k',alpha = 1.0, stacked= True, label ='Time between Blinks')  

    plt.xlabel('Time between blinks (s)')
    plt.ylabel('Probability density')

#    plt.ylim(0,max(n))
#    plt.xlim(xlim_low,xlim_high)
#    plt.legend()
    plt.savefig(os.path.join(saveFolder,'Starfish_blinkInterval_ensemble.svg'), dpi = 150)

    plt.show()

    fig = plt.figure(figsize=(6,6), dpi = 150)

#    plt.subplot(122)
    n, bins, patches = plt.hist(BlinkDurations_array, bins = 'auto', density = True, facecolor = color2, edgecolor = 'k', alpha = 1.0, stacked = True, label ='Blink durations')
    plt.xlabel('Blink duration (s)')
    plt.ylabel('Probability density')


    plt.savefig(os.path.join(saveFolder,'Stafish_blinkDuration_ensemble.svg'), dpi = 150)

    
#    plt.ylim(0,max(np.max(nZ),np.max(nX))+0.1)
#    plt.xlim(xlim_low,xlim_high)
#    plt.legend()    
    plt.show()
    
    print(len(TimeBetweenBlinks_array))
        
    orgName = 'Starfish'
    # Save the blink statistics in a CSV file
    saveFile = orgName+'_BlinkStatistics.csv'
    csv_register = csv.CSV_Register(header=[['Mean Time between blinks', 'Std of Time Between blinks','Mean Blink duration','Std Blink duration']])
    csv_register.file_directory = os.path.join(saveFolder, saveFile)
    csv_register.start_write()
    data = [np.nanmean(TimeBetweenBlinks_array), np.nanstd(TimeBetweenBlinks_array), np.nanmean(BlinkDurations_array), np.nanstd(BlinkDurations_array)] 
    csv_register.write_line([data])
    csv_register.close()
    
        
        
        
    
    
    
if __name__ == '__main__':
    main()