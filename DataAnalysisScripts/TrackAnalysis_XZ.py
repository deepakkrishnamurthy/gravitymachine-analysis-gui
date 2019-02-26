#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 10:27:47 2018
Plot XZ Tracks for gravity machine
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
import imp
import Track

imp.reload(Track)



def main():
    #--------------------------------------------------------------------------
    # Sea Cucumber
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber'
#    TrackNames = {0:'seacucmber4_auto_verylong_goodtrack'}
#    TimePoint = 200
    #--------------------------------------------------------------------------
    # Dendraster
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood'
#    TrackNames = {0:'Dendraster3'}
#    TimePoint = 85
    
#    --------------------------------------------------------------------------
    # Brittle Star
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar'
#    
#    TrackNames = {0:'BrittleStar9_Long_Good_Ytracking'}
#    
#    TimePoint = 53
  
    #--------------------------------------------------------------------------
    # Sea Urchin
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin'
#
#    TrackNames = {0: 'SeaUrchin7'}
#    TimePoint = 66
    
    #--------------------------------------------------------------------------
    # Starfish
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'
#    TrackNames = {0:'StarFish7'}
#    TimePoint = 159
  
    #--------------------------------------------------------------------------
    # Acorn Worm
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight'
#    TrackNames = {0: 'AcornWorm3'}
#    TimePoint = 119
    
    #--------------------------------------------------------------------------
    # Snail
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail'
##    
#    TrackNames = {0:'snail1'}
#    TimePoint = 119

#    --------------------------------------------------------------------------
#     Polychaetes
    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D'
    TrackNames = {0:'Polychaete6'}
    TimePoint = 128

    
    *rest,orgName = os.path.split(dataFolder)
    saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
    
    TimeDuration = 4

    TrackFile = 'track_mod.csv'
    
    for ii, currFolder in TrackNames.items():
        path = os.path.join(dataFolder, TrackNames[ii])
        Track_curr = Track.GravMachineTrack(path, TrackFile)
        
        Track_curr.plot_XZ_fixedWindow(TimePoint = TimePoint, TimeDuration= TimeDuration)
        
        
        
        
        


if __name__ == '__main__':
    main()
