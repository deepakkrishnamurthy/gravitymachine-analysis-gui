# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 15:44:49 2018
Make a time-lapse video from a sequence of images
@author: deepak90
"""

import argparse
import time
import cv2
from roipoly import roipoly
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os
import Track
import cmocean
import imp
imp.reload(Track)
from matplotlib_scalebar.scalebar import ScaleBar

#path = 'L:/Hopkins_2018_08_31/MarSno2'
#path = 'G:/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_06/Tow_1/star'
#path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2'
path = 'F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Starfish/StarFish6highfreq'



dataFolder, fileName = os.path.split(path)

savFile = os.path.join(dataFolder, fileName+'_Video.avi')

imageFolder = os.path.join(path,'images')

saveFolder = os.path.join(path, 'images_proc')

if(not os.path.exists(saveFolder)):
    os.makedirs(saveFolder)

TrackName = 'track.csv'

Track1 = Track.GravMachineTrack(path,TrackName)
    
nData = Track1.trackLen

pixelsize = 1000/314

fig = plt.figure(1)
plt.ion()
scalebar = ScaleBar(pixelsize,'um')

for ii in range(nData):
    
    if(Track1.ImageName[ii]):
        
        Time_curr = Track1.T[ii]
        # Load the image
        print('Loading image: {}'.format(Track1.ImageName[ii]))
        image_a_path = os.path.join(imageFolder, Track1.ImageName[ii])
        
        
        
        dest_image_path = os.path.join(saveFolder, Track1.ImageName[ii])
        
        frame_a_color = cv2.imread(image_a_path)
        
        frame_gs = cv2.cvtColor(frame_a_color, cv2.COLOR_BGR2GRAY)
        
#        frame_gs_eq = cv2.equalizeHist(frame_gs)
        
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(12,12))
        frame_clahe = clahe.apply(frame_gs)
        
#        plt.clf()
#        
#        plt.subplot(131)
#        plt.imshow(frame_gs, cmap = cmocean.cm.gray)
#        
#        plt.subplot(132)
#        plt.imshow(frame_gs_eq,cmap = cmocean.cm.gray)
#        
#        plt.subplot(133)
#        plt.imshow(frame_clahe,cmap = cmocean.cm.gray)
#        plt.show()
#        
        
        cv2.imwrite(dest_image_path, frame_clahe)
#        plt.pause(0.001)
        
        
        
        
        

        
        
        
