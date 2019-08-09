# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 10:21:31 2018

@author: Francois
"""

import csv
import CSV_Tool
import numpy as np


#--------------------------------------------------------------------------
#                       Data importation
#--------------------------------------------------------------------------

#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_08/BrittleStar/BrittleStar9_Long_Good_Ytracking/"

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish10/'

#path = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/nnn1/'
#path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2/'

#path = '/Volumes/DEEPAK-SSD/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_07/diatom_star/'

#path = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/nnn1/'

#path = '/Volumes/GravMachHD2/div1/'
path = '/Volumes/DEEPAK-SSD/Pyro_Division_Tracks/1121/'
tmin = 8250#0#80#0
tmax = 9250#300#380

 

file="track.csv"
#Test6_0_0_8mm_movTest2_0_2mm_away
Data=[]
reader = csv.reader(open(path+file,newline=''))
for row in reader:
    Data.append(row)
n=len(Data)

Time=np.array([float(Data[i][0]) for i in range(1,n)])             # Time stored is in milliseconds
Xobjet=np.array([float(Data[i][1]) for i in range(1,n)])             # Xpos in motor full-steps
Yobjet=np.array([float(Data[i][2]) for i in range(1,n)])             # Ypos in motor full-steps
Zobjet=np.array([float(Data[i][3]) for i in range(1,n)])             # Zpos is in encoder units
ThetaWheel=np.array([float(Data[i][4]) for i in range(1,n)])
ZobjWheel=np.array([float(Data[i][5]) for i in range(1,n)])
ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])   # 0 for auto, 1 for manual
ImageName=np.array([Data[i][7] for i in range(1,n)])
focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,n)])
#colorR=np.array([int(Data[i][11]) for i in range(1,n)])
#colorG=np.array([int(Data[i][12]) for i in range(1,n)])
#colorB=np.array([int(Data[i][13]) for i in range(1,n)])


# Check if the time column is an absolutely increasing column.

Time_new = np.zeros_like(Time)
ZobjWheel_new = np.zeros_like(Time)
for ii in range(1,n-1):
    
    if(Time[ii]-Time[ii-1] < 0):
        Time_new[ii] = Time_new[ii-1] + Time[ii]
        ZobjWheel_new[ii] = ZobjWheel_new[ii-1] + ZobjWheel[ii]
        print('Decreasing time found!')
        print(Time_new[ii-1])
        print(Time_new[ii])
        
    else:
        Time_new[ii] = Time_new[ii-1] + (Time[ii] - Time[ii-1])
        ZobjWheel_new[ii] = ZobjWheel_new[ii-1] + (ZobjWheel[ii] - ZobjWheel[ii-1])
    
if(tmax == 0):
    tmax = np.max(Time_new)

index_min=np.argmin(abs(Time_new-tmin))
index_max=np.argmin(abs(Time_new-tmax))

print(index_min,index_max)

Time2=Time_new[index_min:index_max+1]
Xobjet2=Xobjet[index_min:index_max+1]
Yobjet2=Yobjet[index_min:index_max+1]
Zobjet2=Zobjet[index_min:index_max+1]
ThetaWheel2=ThetaWheel[index_min:index_max+1]
ZobjWheel2=ZobjWheel_new[index_min:index_max+1]
ManualTracking2=ManualTracking[index_min:index_max+1]
ImageName2=ImageName[index_min:index_max+1]
focusMeasure2=focusMeasure[index_min:index_max+1]
focusPhase2=focusPhase[index_min:index_max+1]
MaxfocusMeasure2=MaxfocusMeasure[index_min:index_max+1]

Xobjet2[-1]=Xobjet.max()
Xobjet2[-2]=Xobjet.min()

Yobjet2[-1]=Yobjet.max()
Yobjet2[-2]=Yobjet.min()


file2="track_division.csv"

csv_writer=CSV_Tool.CSV_Register()
csv_writer.file_directory=path+file2
csv_writer.start_write()

for i in range(index_max-index_min+1):
    csv_writer.write_line([[Time2[i],Xobjet2[i],Yobjet2[i],Zobjet2[i],ThetaWheel2[i],ZobjWheel2[i],ManualTracking2[i],ImageName2[i],focusMeasure2[i],focusPhase2[i],MaxfocusMeasure2[i]]])
csv_writer.close()

print('finish')