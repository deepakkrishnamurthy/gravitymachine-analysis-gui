#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 08:33:17 2019
Testing code snippet to load all the Images and subfolders of a gravity machine dataset and 
create an index so that images can be contiguously read from different subfolders.
@author: deepak
"""
import numpy as np
import csv as csv
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
from roipoly import roipoly
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import pickle
plt.close("all")
from PIL import Image
import imp
import Track
imp.reload(Track)


path = '/Users/deepak/Dropbox/GravityMachine/DataAnalysis/Test'
#path = '/Volumes/GRAVMACH1/VolvoxPhotoresponse/vvx25'
#path = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/nnn1'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish1'

# Number of subfolders in the main folder
subFolderCount = 0

fileDict = {}

trackFileNames = []

for dirs, subdirs, files in os.walk(path, topdown=False):
    
    print('Directory : {} \n'.format(dirs))
    print('Sub-Directory : {} \n'.format(subdirs))
    print('File : {} \n'.format(files))
   
    root, subFolderName = os.path.split(dirs)
        
    print(subFolderName[0:6])
    if('test' in subFolderName):
      
       subFolderCount += 1
#       print('Directory : {} \n'.format(dirs))
#       print('File : {} \n'.format())
       
       for fileNames in files:
           key = fileNames
           value = subFolderName
           fileDict[key]=value
   
    if(os.path.normpath(dirs) == os.path.normpath(path)):
        
        for fileNames in files:
            
            if('.csv' in fileNames):
                
                trackFileNames.append(fileNames)
                
                
                

                
   
if(len(trackFileNames)==0):
    raise FileNotFoundError('CSV track was not found!')      
elif(len(trackFileNames)>1):
    print('More than one .csv file found! Using the most recent one ...')
    for tracks in trackFileNames:
        if('mod' in tracks):
            print(tracks)
else:
    print(trackFileNames)
       
print('File dictionary')
print(fileDict)






   
   
    


