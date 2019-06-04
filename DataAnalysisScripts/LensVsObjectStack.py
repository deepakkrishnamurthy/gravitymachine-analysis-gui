#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 23:00:45 2019

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

path = '/Users/deepak/Dropbox/GravityMachine/FocusTracking'

file1 = 'LiquidLensMoving_0_5mm_1Hz.pkl'
file2 = 'ObjectMoving_0_5mm.pkl'

with open(os.path.join(path, file1),'rb') as f:
    
    lens_disp, focus_measure_lens = pickle.load(f)
    
    
with open(os.path.join(path, file2),'rb') as f:
    
    obj_disp, focus_measure_obj = pickle.load(f)
    
    

plt.figure()

plt.scatter(lens_disp, focus_measure_lens, 20, color = 'r', alpha = 0.5, label='Moving liquid lens')
plt.scatter(obj_disp, focus_measure_obj, 20, color = 'b', alpha = 0.5, label='Moving object')

plt.title('Focus measure over a Z-stack by moving lens vs moving object')
plt.xlabel('Displacement (mm)')
plt.ylabel('Focus measure')
plt.legend()
