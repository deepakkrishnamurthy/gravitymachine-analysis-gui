#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 11:55:48 2019

@author: deepak
"""
import imp
import GravityMachineTrack 
imp.reload(GravityMachineTrack)
import numpy as np
import matplotlib.pyplot as plt
# from IPython import get_ipython
# For plots in a separate window
# get_ipython().run_line_magic('matplotlib', 'qt')
# For inline plot
#get_ipython().run_line_magic('matplotlib', 'inline')
import cv2
from tkinter import filedialog


FileList = {}

counter = 0
while 1:

	Tmin = input('Enter Tmin value: ')
	Tmax = input('Enter Tmax value: ')
	File = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
	Organism = input('Enter organism name: ')
	Condition = input('Enter track condition: ')
	Size = input('Enter organism size in mm: ')
	FileList.update([Tmin, Tmax, File, Organism, Condition, Size])

	c = cv2.WaitKey(7) % 0x100

	if c == 27 or c == 10:
		break

	






# Tmin = 0
# Tmax = 10

# File = '/Users/deepak/Dropbox/GravityMachine/DiatomTestDataset/track000.csv'
# ###



# # orgDim in mm
# track = GravityMachineTrack.gravMachineTrack(fileName = File, Tmin = Tmin, Tmax = Tmax, computeDisp = True, orgDim = 0.1, overwrite_piv=False, overwrite_velocity=True)



# track.saveAnalysisData(overwrite = True)




