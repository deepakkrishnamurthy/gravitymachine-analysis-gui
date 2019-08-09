#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 15:09:09 2019
Analysis of PIV data
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
import matplotlib.patches as patches
from matplotlib.lines import Line2D
plt.close("all")
from matplotlib import animation
import matplotlib.ticker as ticker
import pickle
import seaborn as sns

def readPIVdata(filename):
    
    with(open(filename,'rb')) as f:
        x, y , u, v, orgContour, circleContour =  pickle.load(f)
    
    return x,y,u,v,orgContour, circleContour

dataFolder_after = '/Users/deepak/Dropbox/GravityMachine/BackgroundFlowMeaurement/AfterMixing_Equlibration/AfterMixing_Equlibration_IMG_0_200/PIVdata_64px'

dataFolder_before = '/Users/deepak/Dropbox/GravityMachine/BackgroundFlowMeaurement/BeforeEquilibration/BeforeEquilibration_IMG_0_200/PIVdata_64px'

FilesList_before = os.listdir(dataFolder_before)

FilesList_after = os.listdir(dataFolder_after)


FlowSpeed_before = []
FlowSpeed_after = []

for ii, file in enumerate(FilesList_before):
    
    pklFile = os.path.join(dataFolder_before,file)
    
    x,y,u,v,orgContour, circleContour = readPIVdata(pklFile)
    
    u, v = (np.array(u), np.array(v))
    
    U = np.array((u**2 + v**2)**(1/2))
    
    FlowSpeed_before.append(U.ravel())
    
for ii, file in enumerate(FilesList_after):
    
    pklFile = os.path.join(dataFolder_after,file)
    
    x,y,u,v,orgContour, circleContour = readPIVdata(pklFile)
    
    u, v = (np.array(u), np.array(v))
    
    U = np.array((u**2 + v**2)**(1/2))
    
    FlowSpeed_after.append(U.ravel())
    
    

FlowSpeed_before = np.array(FlowSpeed_before)

FlowSpeed_after = np.array(FlowSpeed_after)

FlowSpeed_before = FlowSpeed_before.ravel()

FlowSpeed_after = FlowSpeed_after.ravel()


data = [1000*FlowSpeed_before, 1000*FlowSpeed_after]
plt.figure()
plt.boxplot(data, showfliers=False)
#sns.boxplot(x='Before',y=FlowSpeed_before, color = 'r',showfliers=False)
#sns.boxplot(x='After',y=FlowSpeed_after, color = 'b', showfliers=False)


