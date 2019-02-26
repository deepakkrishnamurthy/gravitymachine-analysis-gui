#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 21:42:19 2018

@author: deepak
"""

import trackpy
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
import argparse
import imutils
import time
import numpy as np
import os, sys
import trackpy as tp
import pims
import matplotlib.pyplot as plt
import imageio
import roipoly
import cmocean
import pandas as pd
import pickle
imageio.plugins.ffmpeg.download()
import csv
plt.close("all")

class particleTrack:
    
    def __init__(self,frames, positionX, positionY, FPS, pixelPermm):
        
        self.frames = np.array(frames)
        
        self.X = np.array(positionX)
        
        self.Y = np.array(positionY)
        
#        index = np.argsort(self.frames)
#        
#        self.frames = self.frames[index]
#        self.X = self.X[index]
#        self.Y = self.Y[index]
        
        self.fps = FPS
        
        self.pixelPermm = pixelPermm
        
        self.computeSpeed()
        
    
    def computeSpeed(self):
        
        self.velocity_x = (self.X[1:] - self.X[:-1])*(1/self.pixelPermm)*(self.fps)
        self.velocity_y = (self.Y[1:] - self.Y[:-1])*(1/self.pixelPermm)*(self.fps)
        
        self.Speed = (self.velocity_x**2 + self.velocity_y**2)**(1/2)
        
#        self.Speed = self.smoothSignal(self.Speed, window_time = 1)
        
    def smoothSignal(self, data, window_time):      # Window is given in seconds
        
        avgWindow = int(window_time*self.fps)

        return pd.rolling_mean(data, avgWindow, min_periods = 1, center = True)
    
    
def loadCSV(dataPath, fileName):
    Data=[]
    reader = csv.reader(open(os.path.join(dataPath,fileName),newline=''))
    for row in reader:
        Data.append(row)
    n=len(Data)
    
    frameNum =np.array([Data[i][0] for i in range(1,n)])            # Time stored is in milliseconds
    X_pos = np.array([float(Data[i][3]) for i in range(1,n)])             # Xpos in motor full-steps
    Y_pos = np.array([float(Data[i][4]) for i in range(1,n)])             # Ypos in motor full-steps
    Speed = np.array([float(Data[i][6]) for i in range(1,n)])    
    

    return frameNum, X_pos, Y_pos, Speed
    
    #VideoFolder = '/Users/deepak/Dropbox/GravityMachine/ExperimentResults/AbioticExperiments'
VideoFolder = '/Volumes/GRAVMACH1/GravityMachine/2017_06_01_DissolvingCrystalsInFlow'

DestinationFolder = os.path.join(VideoFolder, 'TrackOverlaySimple')
if(not os.path.exists(DestinationFolder)):
    os.makedirs(DestinationFolder)
    
#VideoFile = 'kiss_tumble_1214_1343'
VideoFile = 'Substack_1_99'


frames = pims.ImageSequence(os.path.join(VideoFolder, VideoFile), as_grey=True)


FPS = 60

BeadFile = 'SugarTrack.csv'

ParticleFile = 'ParticleTrack.csv'

frame_depth = 100

#print('Total number of frames in the Folder : {}'.format(totalFrames))
print('Video frame rate: {} fps'.format(FPS))

frameNum_bead, X_pos_bead, Y_pos_bead, Speed_bead = loadCSV(VideoFolder, BeadFile)

frameNum, X_pos, Y_pos, Speed = loadCSV(VideoFolder, ParticleFile)

Track_bead = particleTrack(frames, X_pos_bead, Y_pos_bead,FPS,1) # Track of the sugar bead

Track_particle = particleTrack(frames, X_pos, Y_pos,FPS,1)      # Track of the ejected particle

#Track_particle.X, Track_particle.Y = (Track_particle.smoothSignal(Track_particle.X,0.05),Track_particle.smoothSignal(Track_particle.Y,0.05))

Umax = 0

imW = 216
imH = 320

origins_Y = Track_bead.Y - int(imH/2)
origins_X = Track_bead.X - int(imW/2)

TimeArray = np.array(range(len(frames)))/FPS

for ii in range(len(frames)-5):
    
    plt.clf()
    
    currFrame = frames[ii]
    
    originY = int(Track_bead.Y[ii+1])-int(imH/2)
    
    originX = int(Track_bead.X[ii+1])-int(imW/2)
    
    currFrame_cropped = currFrame[int(Track_bead.Y[ii+1])-int(imH/2):int(Track_bead.Y[ii+1])+int(imH/2), int(Track_bead.X[ii+1])-int(imW/2):int(Track_bead.X[ii+1])+int(imW/2)]
    plt.imshow(currFrame_cropped,cmap = cmocean.cm.gray)
#    
    startIndex = ii +1 - frame_depth
    if(startIndex < 0):
        startIndex = 0
#    ax1 = plt.scatter(X_pos_bead[startIndex:ii], Y_pos_bead[startIndex:ii], s = 10, color = 'r')
#    ax2 = plt.scatter(X_pos[startIndex:ii], Y_pos[startIndex:ii], s = 10, c= Speed[startIndex:ii], cmap = plt.cm.plasma)
    
    ax2 = plt.scatter(Track_particle.X[startIndex:ii] - origins_X[startIndex:ii], Track_particle.Y[startIndex:ii] - origins_Y[startIndex:ii],cmap = plt.cm.plasma, s = 10, c = 'Orange', alpha=0.75, edgecolors = 'none', marker = 'o')
    ax3 = plt.scatter(Track_particle.X[ii] - originX, Track_particle.Y[ii] - originY, s = 70, facecolors='none', edgecolors = 'r', marker = 'o')


    plt.pause(0.001)
    
    Umax = max(Umax, max(Speed))
        
    plt.savefig(os.path.join(DestinationFolder,'IMG'+'{:03d}'.format(ii)+'.png'), dpi=300)

        
#plt.colorbar(ax2)
    
print(Umax)



