#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 14:51:42 2018
Script to rescale the Z data of gravity machine to the correct scale
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
from pathlib import Path

Rcenter = 87.5
gearRatio = 99+1044/float(2057) 

class CSV_Register():
    
    def __init__(self,parent=None):
        self.file_directory=None
        self.header = [['Time', 'Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum','LEDPanel color R','LEDPanel color G','LEDPanel color B']]
#        self.header = [['Time', 'Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum']]

        self.currTrackFile=None
        self.writer=None
        
        
    def start_write(self):
        
        self.currTrackFile=open(self.file_directory,'w')
        csv.register_dialect('myDialect', delimiter=',', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
        self.writer = csv.writer(self.currTrackFile , dialect='myDialect')
        self.writer.writerows(self.header)
        
    def write_line(self,data):
        self.writer.writerows(data)
        
    def close(self):
        self.currTrackFile.close()

    def readCSV(self,fileName):
        Data=[]
        reader = csv.reader(open(fileName,newline=''))
        for row in reader:
            Data.append(row)
        n=len(Data) 
        
        #Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
        Time=np.array([float(Data[i][0]) - float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
        Xobj=np.array([float(Data[i][1]) for i in range(1,n)])                    # Xpos in the image in mm
        Yobj=np.array([float(Data[i][2]) for i in range(1,n)])                    # Ypos in motor full-steps
        Zobj=np.array([float(Data[i][3]) for i in range(1,n)])                    # Zpos in the image in mm
        ThetaWheel=np.array([float(Data[i][4]) for i in range(1,n)])
        ZobjWheel=np.array([float(Data[i][5]) for i in range(1,n)])
        ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])              # 0 for auto, 1 for manual
        ImageName=np.array([Data[i][7] for i in range(1,n)])
        focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
        focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
        MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,n)])
        LED_R = np.array([float(Data[i][11]) for i in range(1,n)])	
        LED_G = np.array([float(Data[i][12]) for i in range(1,n)])	
        LED_B = np.array([float(Data[i][13]) for i in range(1,n)])	

        return Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName, focusMeasure, focusPhase, MaxfocusMeasure, LED_R, LED_G, LED_B
#        return Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName, focusMeasure, focusPhase, MaxfocusMeasure

def rad_to_mm(ThetaWheel,Xobjet):
    return ThetaWheel*(Rcenter+Xobjet)

def main():
    
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'
#    path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2'
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'

#    dataFolder ='/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_well_fed_11Days_nofood'
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07'
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin'
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight'
    
    # Brittle Star
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar'
    
    
#    TrackNames = {0:'BrittleStar1',1:'BrittleStar9_Long_Good_Ytracking',2:'BrittleStar10_Ytracking_Good',3:'BrittleStar12_Ytracking_Good'}
    
    # Snail
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail'
    
#    TrackNames = {0:'snail1',1:'snail2',2:'snail4',3:'snail6',4:'snail8',5:'snail10',6:'snail13'}
    
    
    # Noctiluca
#    dataFolder = Path('/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca')
    
#    TrackNames = {0:'Noctilica6',1:'Noctilica7'}
    
#    TrackNames = {0:'StarFish1',1:'StarFish6',2:'StarFish7',3:'StarFish9',4:'StarFish10'}
#    TrackNames = {0:'Dendraster1',1:'Dendraster2',2:'Dendraster3'}


#    TrackNames = {0:'seacucmber4_auto_verylong_goodtrack', 1:'seacucmber9_Auto',2:'falling_sea_cucumber',3:'falling_sea_cucumber_1',4:'seacucmber7_Manual'}
#    TrackNames = {0: 'SeaUrchin5',1: 'SeaUrchin7',2: 'SeaUrchin8'}
    
#    TrackNames = {0: 'AcornWorm2',1: 'AcornWorm3',2: 'AcornWorm4',3: 'AcornWorm7'}
    
#    dataFolder = 'F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_14/AssortedPlankton/Noctiluca'
    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D'
    
    
    Tracks = [dI for dI in os.listdir(dataFolder) if os.path.isdir(os.path.join(dataFolder, dI))]
    
    for TrackNames in Tracks:
        print('Analyzing {} ... '.format(TrackNames))
    
    
    TrackName = 'track.csv'
    modTrackName = 'track_mod.csv'
    
    
    for TrackFolder in Tracks:
        
        
        csv_register = CSV_Register()
        csv_register.file_directory = os.path.join(dataFolder, TrackFolder, modTrackName)
#        print(csv_register.file_directory)
        csv_register.start_write()
        #--------------------------------------------------------------------------
        # Load data from the track into numpy arrays
        #--------------------------------------------------------------------------
        Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure, LED_R, LED_G, LED_B = csv_register.readCSV(fileName = os.path.join(dataFolder, TrackFolder, TrackName))
#        Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure = csv_register.readCSV(fileName = os.path.join(dataFolder, TrackFolder, TrackName))
        
        nData = len(Time)
        print("{:~^50} {}".format('No:of Data points:',nData))
        
        if(nData == 0):
            continue
        
        ThetaWheel_new = np.zeros_like(ThetaWheel)
        ZobjWheel_new = np.zeros_like(ZobjWheel)
        
        for ii in range(1,nData):
            
            # Scaling factor for Marine snow dataset
    #        scalingFactor = 2*np.pi*(20*16/0.5)/float(gearRatio*600)
            
            # Scaling factor for Hopkins datasets
            scalingFactor = 1/float(3)
            
            deltaTheta_new = (ThetaWheel[ii] - ThetaWheel[ii-1])*scalingFactor
            ThetaWheel_new[ii] = ThetaWheel_new[ii-1] + deltaTheta_new
            
    #        print('Image displacement: {}'.format(Zobj[ii] - Zobj[ii-1]))
            ZobjWheel_new[ii] = ZobjWheel_new[ii-1] + (Zobj[ii]-Zobj[ii-1]) - rad_to_mm(ThetaWheel_new[ii] - ThetaWheel_new[ii-1], Xobj[ii])
            
            data = [Time[ii-1], Xobj[ii-1], Yobj[ii-1], Zobj[ii-1], ThetaWheel_new[ii-1], ZobjWheel_new[ii-1], ManualTracking[ii-1],ImageName[ii-1],focusMeasure[ii-1], focusPhase[ii-1], MaxfocusMeasure[ii-1], LED_R[ii-1], LED_G[ii-1], LED_B[ii-1]]
            
            # Older data format
#            data = [Time[ii-1], Xobj[ii-1], Yobj[ii-1], Zobj[ii-1], ThetaWheel_new[ii-1], ZobjWheel_new[ii-1], ManualTracking[ii-1],ImageName[ii-1],focusMeasure[ii-1], focusPhase[ii-1], MaxfocusMeasure[ii-1]]

            csv_register.write_line([data])
        
        lastIndex = nData - 1 
        data = [Time[lastIndex], Xobj[lastIndex], Yobj[lastIndex], Zobj[lastIndex], ThetaWheel_new[lastIndex], ZobjWheel_new[lastIndex], ManualTracking[lastIndex],ImageName[lastIndex],focusMeasure[lastIndex], focusPhase[lastIndex], MaxfocusMeasure[lastIndex], LED_R[lastIndex], LED_G[lastIndex], LED_B[lastIndex]]
        
        # Older data format
#        data = [Time[lastIndex], Xobj[lastIndex], Yobj[lastIndex], Zobj[lastIndex], ThetaWheel_new[lastIndex], ZobjWheel_new[lastIndex], ManualTracking[lastIndex],ImageName[lastIndex],focusMeasure[lastIndex], focusPhase[lastIndex], MaxfocusMeasure[lastIndex]]

        csv_register.write_line([data])
        csv_register.close()
        
         # Plot the original Z track
        f = plt.figure()
        plt.subplot(121)
        plt.plot(Time,ThetaWheel - ThetaWheel[0],color='r')
        plt.xlabel('Time (s)')
        plt.ylabel('Theta (radians)')
        plt.title('Original Data')
        # Plot the rescaled Z track
        plt.subplot(122)
        plt.plot(Time,ThetaWheel_new,color='g')
        plt.xlabel('Time (s)')
        plt.ylabel('Theta (radians)')
        plt.title('Rescaled Data')
        plt.show()
        
        # Plot the original Z track
        f = plt.figure()
        plt.subplot(121)
        plt.plot(Time,ZobjWheel - ZobjWheel[0],color='r')
        plt.xlabel('Time (s)')
        plt.ylabel('Z displacement (mm)')
        plt.title('Original Data')
        # Plot the rescaled Z track
        plt.subplot(122)
        plt.plot(Time,ZobjWheel_new,color='g')
        plt.xlabel('Time (s)')
        plt.ylabel('Z displacement (mm)')
        plt.title('Rescaled Data')
        plt.show()
    
    
            
if __name__ == '__main__':
    main()