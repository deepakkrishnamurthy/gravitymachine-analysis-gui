#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:37:43 2018
Track analysis for gravity machine
1. RMSD of tracks
2. Velocity distributions
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

def squared_displacement(data,i,n):
    # n is the track len over which an ensemble is calculated
    return (data[i:i+n]-data[i])**2

def squared_vector_3d(X,Y,Z,i,n):
    
    return (X[i:i+n] - X[i])**2 + (Y[i:i+n] - Y[i])**2 + (Z[i:i+n] - Z[i])**2 

def makeSubtracks(Track, Dia):
    # Binary Mask of the track: Near Wall: 1 Away From Wall: 0
    
    
    atWall = (Track.X < (Track.xmin+Dia))|(Track.X>(Track.xmax-Dia))|(Track.Y<(Track.ymin+Dia))|(Track.Y>(Track.ymax-Dia))
    print(np.sum(atWall))
    
    subTrackIndex = 0
    counter = 0
    startIndex = {}
    stopIndex = {}
    # If the first element is part of the track then initialize the subTrack
    if(atWall[0]==0):
        startIndex[counter]=0
        
    for ii in range(1,len(atWall)):
    #     print(ii)
    #     print(counter)
        
        if(atWall[ii-1] == 0 and atWall[ii] == 1):
            stopIndex[counter] = ii-1
            counter += 1    
        elif (atWall[ii-1]==1 and atWall[ii]== 0):
            startIndex [counter] = ii
            
    # if not stopIndex:
    #     stopIndex[counter]=len(atWall)-1
        
    if (len(stopIndex.keys()) < len(startIndex.keys())):
        stopIndex[counter] = len(atWall)-1
    
    print(startIndex)
    print(stopIndex)
    
    subTrack={}
    sqDispSubTrack = {}
    trackLens = {}
    # Create subtracks
    print(startIndex.keys())
    for ii in startIndex.keys():
       
        subTrack[ii] = np.array([Track.X[startIndex[ii]:stopIndex[ii]+1],Track.Y[startIndex[ii]:stopIndex[ii]+1],Track.Z[startIndex[ii]:stopIndex[ii]+1]])
       
        sqDispSubTrack[ii] = squared_vector_3d(subTrack[ii][0,:],subTrack[ii][1,:],subTrack[ii][2,:],0,np.size(subTrack[ii],axis=1))
        trackLens[ii] = np.size(subTrack[ii],axis=1)
        
    # Calculate the MSD using the ensemble average of the subtracks
    maxTrackLen = max(trackLens.values())
    numSubTracks = len(subTrack.keys())
    
    print('No:of subtracks : {}'.format(numSubTracks))
    
    SumSqDisp_subTracks = np.zeros(maxTrackLen,)
    meanWeights = np.zeros(maxTrackLen,)
    
    for ii in range(0,numSubTracks):
        for jj in range(0,np.size(subTrack[ii],axis=1)):
            SumSqDisp_subTracks[jj] += sqDispSubTrack[ii][jj]
            meanWeights[jj]+=1
    
    MSD_subTracks = SumSqDisp_subTracks/meanWeights
    
    T_subTrack = np.array(T[0:maxTrackLen])

    

def main():
    
    # Organism
    
    # Dendraster
    
    # Largest Organism diameter in mm
    Dorg = 0.3 
    
    dataFolder = '/Volumes/GRAVMACH1 2/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood'
    
    # Load the set of tracks we want to analyze
    TrackNames = {0:'Dendraster1',1:'Dendraster2',2:'Dendraster3'}
    
    TrackFile = 'track.csv'
    
    SquaredDisp_XY = []
    SquaredDisp_Z = []
    
    trackLen_array = np.zeros(len(TrackNames.keys()))
    
#    SquaredDisp_subtracks = 
    for ii,currFolder in TrackNames.items():
        
        
        Track_curr = Track.GravMachineTrack(os.path.join(dataFolder,currFolder,TrackFile))
        
        trackLen_array[ii] = Track_curr.trackLen
        
        SquaredDisp_Z.append(squared_displacement(Track_curr.Z,0,Track_curr.trackLen))
        
        SquaredDisp_XY.append(squared_displacement(Track_curr.X,0,Track_curr.trackLen) + squared_displacement(Track_curr.Y,0,Track_curr.trackLen))
        
    
    maxTrackLen = np.max(trackLen_array)
    
    stackedArray_Z = np.zeros((len(TrackNames.keys(), maxTrackLen)))
    stackedArray_XY = np.zeros((len(TrackNames.keys(), maxTrackLen)))
    
    for ii in TrackNames.keys():
        stackedArray_Z[ii,:trackLen_array[ii]] = SquaredDisp_Z[ii]
        stackedArray_XY[ii,:trackLen_array[ii]] = SquaredDisp_XY[ii]
        
    
    stackedArray_Z = np.ma.array(stackedArray_Z, mask = stackedArray_Z==0)
    stackedArray_XY = np.ma.array(stackedArray_XY, mask = stackedArray_XY==0)
    
    RMSD_Z = (stackedArray_Z.mean(axis=0))
    RMSD_XY = (stackedArray_XY.mean(axis=0))
    
    
if __name__ == '__main__':
    main()
    
