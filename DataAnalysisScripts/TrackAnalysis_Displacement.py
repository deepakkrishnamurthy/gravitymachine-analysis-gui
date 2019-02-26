#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:37:43 2018
Track analysis for gravity machine
1. Calculates Velocity distributions of an ensemble of tracks
@author: deepak
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
import scipy.ndimage as ndimage
import smoothn
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

def squared_displacement(data,i,n):
    # n is the track len over which an ensemble is calculated
    return (data[i:i+n]-data[i])**2

def squared_vector_3d(X,Y,Z,i,n):
    
    return (X[i:i+n] - X[i])**2 + (Y[i:i+n] - Y[i])**2 + (Z[i:i+n] - Z[i])**2 



    

def main():
    
    
    
#    rootFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/'
    
    

    
#    subFolders = {0:'Dendraster_starved_11Days_nofood',1:'Dendraster_starved_11Days_withfood',2:'Dendraster_well_fed_11Days_nofood'}
    
    #--------------------------------------------------------------------------
    # Starfish
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'
#    TrackNames = {0:['StarFish1', 0,162],1:['StarFish6', 0,600],2:['StarFish7', 60,0],3:['StarFish9', 0,290]}
    #--------------------------------------------------------------------------
    # Dendraster
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood'
#    TrackNames = {0:['Dendraster1', 87,417], 1:['Dendraster2', 0,0], 2:['Dendraster3', 0,0]}
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_withfood'
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_well_fed_11Days_nofood'
    
    #--------------------------------------------------------------------------
    # Sea cucumber
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber'
    
#    TrackNames = {0:['seacucmber4_auto_verylong_goodtrack', 0,0], 1:['seacucmber9_Auto', 0,0]}
    
#    TrackNames = {0:['seacucmber4_auto_verylong_goodtrack', 0,0]}
    
    
    #--------------------------------------------------------------------------
    # Sea Urchin
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin'

#    TrackNames = {0: ['SeaUrchin5',0,0],1: ['SeaUrchin7',0,500],2: ['SeaUrchin8',0,0]}

    #--------------------------------------------------------------------------
    # Acorn Worm
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight'
#    TrackNames = {0: ['AcornWorm2',0,0],1: ['AcornWorm3',0,0],2: ['AcornWorm4',0,0],3: ['AcornWorm7',50,140]}
#    --------------------------------------------------------------------------
    # Brittle Star
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar'
    
#    TrackNames = {0:['BrittleStar1',0,0],1:['BrittleStar9_Long_Good_Ytracking',0,0],2:['BrittleStar10_Ytracking_Good',0,0],3:['BrittleStar12_Ytracking_Good',0,0]}
    #--------------------------------------------------------------------------
    # Snail
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail'
    
#    TrackNames = {0:['snail1',0,575],1:['snail2',0,0],2:['snail4',0,0],3:['snail6',0,0],4:['snail8',0,0],5:['snail10',0,0],6:['snail13',0,0]}
    
    
    # Noctilica
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca'
#    TrackNames = {0:['Noctilica6',50,0],1:['Noctilica7',0,1000]}

#     Polychaetes
    dataFolder = ['/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D', '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Polychaete']
#    TrackNames = {0:['Polychaete1',0,112],1:['Polychaete2',0,113], 2:['Polychaete3',0,37], 3:['Polychaete4',0,55], 4:['Polychaete6',0,113]}
    TrackNames = [{0:['Polychaete1',0,112],1:['Polychaete2',0,113], 2:['Polychaete3',0,37], 3:['Polychaete4',0,55], 4:['Polychaete6',0,113]},{0:['Poly1',20,80],1:['Poly2',0,116], 2:['Poly3',0,0], 3:['Poly4',0,93], 4:['Poly5',0,34]}]
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Polychaete'
#    TrackNames = {0:['Poly1',20,80],1:['Poly2',0,116], 2:['Poly3',0,0], 3:['Poly4',0,93], 4:['Poly5',0,34]}
    
#    *rest,orgName = os.path.split(dataFolder)
#    saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
    
    # Load the set of tracks we want to analyze
#    TrackNames = {0:['Dendraster1', 87,417],1:['Dendraster2', 0,0],2:['Dendraster3',0,0]}

#    TrackNames = {0:['Dendraster1', 0,600],1:['Dendraster2', 0,200],2:['Dendraster3',0,0]}
#    TrackNames = {0:['StarFish1', 0,162],1:['StarFish6', 0,600],2:['StarFish7', 60,0],3:['StarFish9', 0,290]}

    
    TrackFile = 'track_mod.csv'

    
#    colors = colors[128:]
    
    
    
    Velocities_X = np.array([])
    Velocities_Y = np.array([])
    Velocities_Z = np.array([])
    
    Velocities_X_notWall = np.array([])
    Velocities_Y_notWall = np.array([])
    Velocities_Z_notWall = np.array([])
    
    totalTrackLen = 0
    
    TrackArray = []
    
    plt.figure(1)
    
    print(dataFolder[1])
    for kk in range(len(TrackNames)):
        if(kk == 0):
                cmap = plt.cm.YlOrRd
                colors=cmap(np.arange(256))
                colors = colors[128:]
                linestyle = '--'
        else:
                cmap = plt.cm.Purples
                colors=cmap(np.arange(256))
                colors = colors[128:]
                linestyle = '-'
                
        totalTracks = len(TrackNames[kk])
        print(totalTracks)
        print(len(colors))
        indices = np.array(len(colors)*np.linspace(0,0.9,totalTracks), dtype = 'int')
        plt_colors = colors[indices]
        for ii, currFolder in TrackNames[kk].items():
            path = os.path.join(dataFolder[kk], TrackNames[kk][ii][0])
            Track_curr = Track.GravMachineTrack(path, TrackFile, TrackNames[kk][ii][1],TrackNames[kk][ii][2])
            
#            TrackArray.append(Track.GravMachineTrack(path, TrackFile, TrackNames[kk][ii][1],TrackNames[kk][ii][2]))
    #        Track_curr.plotTrackWalls(walls=1)
    #        Track_curr.plotVelocity(Track_curr.Vx,Track_curr.Vy,Track_curr.Vz)
    #        Track_curr.plot3DComponents(Track_curr.X_smooth,Track_curr.Y_smooth,Track_curr.Z_smooth, walls = 1)
            Track_curr.T = Track_curr.T - Track_curr.T[0]
            Track_curr.Z = Track_curr.Z - Track_curr.Z[0]
            
            
            plt.plot(Track_curr.T, Track_curr.Z, linewidth = 2, linestyle = linestyle, color = plt_colors[ii])
            plt.fill_between(Track_curr.T,Track_curr.Z,color = plt_colors[ii],alpha=0.2)
            
            AutoTracking = np.array(~Track_curr.ManualTracking[:-1], dtype= 'bool')
            #--------------------------------------------------------------------------
            # Velocity distributions
            #--------------------------------------------------------------------------
    #        Velocities_X = np.hstack((Velocities_X,np.array(Track_curr.Vx[AutoTracking])))
    #        Velocities_Y = np.hstack((Velocities_Y,np.array(Track_curr.Vy[AutoTracking])))
    #        Velocities_Z = np.hstack((Velocities_Z,np.array(Track_curr.Vz[AutoTracking])))
            
    #        Velocities_X_notWall = np.hstack((Velocities_X_notWall,np.array(Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking])))
    #        Velocities_Y_notWall = np.hstack((Velocities_Y_notWall,np.array(Track_curr.Vy[~Track_curr.atWall[:-1]&AutoTracking])))
    #        Velocities_Z_notWall = np.hstack((Velocities_Z_notWall,np.array(Track_curr.Vz[~Track_curr.atWall[:-1]&AutoTracking])))
            #--------------------------------------------------------------------------
        
        
        totalTrackLen += (max(Track_curr.Time) - min(Track_curr.Time))
        
        
    plt.xlabel('Time (s)')
    plt.ylabel('Z displacement (mm)')
    
    
    
#    print(TrackArray[0].Time)
#    print(len(TrackNames))
#    # Save some useful data so it can be easily read back
#    saveFile = orgName+'_TrackStatistics.csv'
#    csv_register = csv.CSV_Register(header=[['nTracks', 'Total Track Time','Mean Velocity Z','Std Velocity Z','Mean Velocity X','Std Velocity X']])
#    csv_register.file_directory = os.path.join(saveFolder, saveFile)
#    csv_register.start_write()
#    data = [len(TrackNames), totalTrackLen, np.nanmean(Velocities_Z_notWall), np.nanstd(Velocities_Z_notWall), np.nanmean(Velocities_X_notWall),np.nanstd(Velocities_X_notWall)] 
#    csv_register.write_line([data])
#    csv_register.close()
    
    
   
    
    


    
#    print(np.shape(Velocities_X))
    

    
#    fig = plt.figure()
#    
#    
#    plt.subplot(131)
#    nX, binsX, patches = plt.hist(Velocities_X, bins = 'auto', facecolor = 'r')
#    plt.xlabel('X Velocity (mm/s)')
#    plt.ylabel('Probability')
#    plt.subplot(132)
#    nY, binsY, patches = plt.hist(Velocities_Y, bins = 'auto', facecolor = 'g')
#    plt.xlabel('Y Velocity (mm/s)')
#    plt.ylabel('Probability')
#    plt.subplot(133)
#    nZ, binsZ, patches = plt.hist(Velocities_Z, bins = 'auto', facecolor = 'b')
#    plt.xlabel('Z Velocity (mm/s)')
#    plt.ylabel('Probability')
#    
#    plt.show()
#    
#    print(np.shape(Velocities_X))
#    print(np.shape(Velocities_Y))
#    print(np.shape(Velocities_Z))
    
#    xlim_low = -2
#    xlim_high = 2
#    
#    color_X = list(cm.bwr(0))
#    color_Z = list(cm.bwr(255))
#    
##    color_X[-1] = 0.7
#    
#   
#    
#    fig = plt.figure(figsize=(5,8), dpi = 150)
#    
#    
#    nX, binsX, patches = plt.hist(Velocities_X,bins = 'auto',range = (-4,4), density = True, facecolor = color_X,alpha = 0.9, stacked= True, label ='X')  
#    nZ, binsZ, patches = plt.hist(Velocities_Z, bins = 'auto', range = (-4,4), density = True, facecolor = color_Z, alpha = 0.7, stacked = True, label ='Z')
#    plt.xlabel('Velocity (mm/s)')
##    plt.ylabel('Probability density')
##    plt.title('Full track')
##    plt.axis('square')
#    plt.ylim(0,max(np.max(nZ),np.max(nX))+0.1)
#    plt.xlim(xlim_low,xlim_high)
#    plt.legend()
#    plt.savefig(os.path.join(saveFolder,orgName+'_VelocityDistribution_Full.svg'))
#    
#    plt.show()
#    
#    fig = plt.figure(figsize=(5,8), dpi = 150)
#    
#    nX, binsX, patches = plt.hist(Velocities_X_notWall,bins = 'auto',range = (-4,4), density = True, facecolor = color_X, alpha = 0.9,stacked= True,label ='X')
#    nZ, binsZ, patches = plt.hist(Velocities_Z_notWall, bins = 'auto', range = (-4,4), density = True, facecolor = color_Z, alpha = 0.7, stacked = True,label ='Z')
#    plt.xlabel('Velocity (mm/s)')
##    plt.ylabel('Probability density')
##    plt.title('Track segments away from walls')
#    plt.ylim(0,max(np.max(nZ),np.max(nX))+0.1)
#    plt.xlim(xlim_low,xlim_high)
#    plt.legend()
#    plt.savefig(os.path.join(saveFolder,orgName+'_VelocityDistribution_noWalls.svg'))
#    plt.show()
#    
  
    

    
   
    
    
    
if __name__ == '__main__':
    main()
    
