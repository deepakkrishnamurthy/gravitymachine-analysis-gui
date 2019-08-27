#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 09:19:55 2018

@author: deepak
"""


import argparse
import time
import cv2
from roipoly import roipoly
import pylab as pl
import numpy as np
import os


#VideoFolder = '/Users/deepak/Dropbox/GravityMachine/ExperimentResults/AbioticExperiments'

#VideoFolder = 'L:/GravityMachine/DissolvingCrystals'

#VideoFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/SedimentingBeads'

#VideoFolder = '/Users/deepak/Dropbox/MiscData'

#VideoFolder = '/Volumes/GRAVMACH1/GravityMachine/SedimentingGlassBeads_2017'

VideoFolder = '/Volumes/My Book/2019 Monterey Trip/Tunicates/LarvaeReleaseImaging/2019_08_10'


#VideoFile = 'MVI_1916.MOV'
#VideoFile = 'InfiniteBeadDance.MOV'
#VideoFile = 'StablePair_Trimmed.MOV'

VideoFile = 'Video0003.mkv'

VideoSaveFolder = os.path.join(VideoFolder,'images')

if (not os.path.exists(VideoSaveFolder)):
    os.makedirs(VideoSaveFolder)

VideoPath = os.path.join(VideoFolder, VideoFile)

#cap = VideoStream(src = VideoPath)

cap = cv2.VideoCapture(VideoPath)

def chooseROI(image):
    
    fromCenter = False
    r = cv2.selectROI("Image", image, fromCenter)    
    return r
   

imgCounter = 0
r = 0
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()

#    if(imgCounter == 0):
#        r = chooseROI(frame)
#        frame = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
#    elif(r is not 0):
#        frame = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        
        
        
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    
    ImgName = 'IMG_{:05d}'.format(imgCounter)+'.tif'
    
    print('Writing Image: {}'.format(ImgName))
    
    cv2.imwrite(os.path.join(VideoSaveFolder,ImgName), gray)
    
    imgCounter += 1
    
    key = cv2.waitKey(1) & 0xFF
			# if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# When everything done, release the capture
#cap.stop()
cap.release()
cv2.destroyAllWindows()

