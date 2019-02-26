# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:16:25 2018
# Script to remove outliers in data due to tracking errors
@author: deepak90
"""

import csv as csv
import numpy as np
import matplotlib.pyplot as plt
import os
plt.close("all")

import Track
import imp
imp.reload(Track)

class CSV_Register(Track.GravMachineTrack):
    
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

    def readCSV(self):
        path, fileName = os.path.split(self.file_directory)
        Track.GravMachineTrack.__init__(self,path=path, file=fileName)
       

        return self.Time,self.Xobj, self.Yobj, self.Zobj, self.ThetaWheel, self.ZobjWheel, self.ManualTracking,self.ImageName, self.focusMeasure, self.focusPhase,self.MaxfocusMeasure, self.LED_R, self.LED_G, self.LED_B
#        return Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName, focusMeasure, focusPhase, MaxfocusMeasure



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
    
    dataFolder = 'F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Starfish'
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D'
    
    TrackFolder = 'StarFish6highfreq'
    
  
    
    
    TrackName = 'track_mod.csv'
    modTrackName = 'track_mod_1.csv'
    
    
        
        
    csv_register = CSV_Register()
    csv_register.file_directory = os.path.join(dataFolder, TrackFolder, modTrackName)
#        print(csv_register.file_directory)
    csv_register.start_write()
    #--------------------------------------------------------------------------
    # Load data from the track into numpy arrays
    #--------------------------------------------------------------------------
    csv_register_0 = CSV_Register()
    csv_register_0.file_directory = os.path.join(dataFolder, TrackFolder, TrackName)

    Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure, LED_R, LED_G, LED_B = csv_register_0.readCSV()
#        Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure = csv_register.readCSV(fileName = os.path.join(dataFolder, TrackFolder, TrackName))
    
    nData = len(Time)
    print("{:~^50} {}".format('No:of Data points:',nData))

    
    
    for ii in range(1,nData):
        
        
        
        
        data = [Time[ii-1], Xobj[ii-1], Yobj[ii-1], Zobj[ii-1], ThetaWheel[ii-1], ZobjWheel[ii-1], ManualTracking[ii-1],ImageName[ii-1],focusMeasure[ii-1], focusPhase[ii-1], MaxfocusMeasure[ii-1], LED_R[ii-1], LED_G[ii-1], LED_B[ii-1]]
        
       
        csv_register.write_line([data])
    
    lastIndex = nData - 1 
    data = [Time[lastIndex], Xobj[lastIndex], Yobj[lastIndex], Zobj[lastIndex], ThetaWheel[lastIndex], ZobjWheel[lastIndex], ManualTracking[lastIndex],ImageName[lastIndex],focusMeasure[lastIndex], focusPhase[lastIndex], MaxfocusMeasure[lastIndex], LED_R[lastIndex], LED_G[lastIndex], LED_B[lastIndex]]
    
    
    csv_register.write_line([data])
    csv_register.close()
    
     # Plot the original Z track
    f = plt.figure()
    plt.plot(Time,Yobj,color='r')
    plt.xlabel('Time (s)')
    plt.ylabel('Y')
    plt.title('Original Data')
     
    
    
            
if __name__ == '__main__':
    main()

