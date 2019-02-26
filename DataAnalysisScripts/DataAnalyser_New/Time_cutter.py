# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 10:21:31 2018

@author: Francois
"""

import csv
import CSV_Tool
import numpy as np
import os


#--------------------------------------------------------------------------
#                       Data importation
#--------------------------------------------------------------------------

#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_08/BrittleStar/BrittleStar9_Long_Good_Ytracking/"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_06/AcornWorm_Experiment2_nolight/SeaUrchin/SeaUrchin7"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_06/SeaUrchin/SeaUrchin7"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_07/Sea_Cucumber/seacucmber4_auto_verylong_goodtrack"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_08/BrittleStar/BrittleStar9_Long_Good_Ytracking"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Dendraster_embryo/Dendraster_Embryo2"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Polychaete_4D/Polychaete6_longest_6mn"
path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Starfish/StarFish6highfreq"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_13/Snail/snail1"
#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_14/AssortedPlankton/Noctiluca/Noctilica6"


tmin=0#0#80#0
tmax=500#300#380

file="track_mod_1.csv"
#Test6_0_0_8mm_movTest2_0_2mm_away
Data=[]
reader = csv.reader(open(os.path.join(path,file),newline=''))
for row in reader:
    Data.append(row)
n=len(Data)

Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])             # Time stored is in milliseconds
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

index_min=np.argmin(abs(Time-tmin))
index_max=np.argmin(abs(Time-tmax))

print(index_min,index_max)

Time2=Time[index_min:index_max+1]
Xobjet2=Xobjet[index_min:index_max+1]
Yobjet2=Yobjet[index_min:index_max+1]
Zobjet2=Zobjet[index_min:index_max+1]
ThetaWheel2=ThetaWheel[index_min:index_max+1]
ZobjWheel2=ZobjWheel[index_min:index_max+1]
ManualTracking2=ManualTracking[index_min:index_max+1]
ImageName2=ImageName[index_min:index_max+1]
focusMeasure2=focusMeasure[index_min:index_max+1]
focusPhase2=focusPhase[index_min:index_max+1]
MaxfocusMeasure2=MaxfocusMeasure[index_min:index_max+1]

#Xobjet2[-1]=Xobjet.max()
#Xobjet2[-2]=Xobjet.min()
#
#Yobjet2[-1]=Yobjet.max()
#Yobjet2[-2]=Yobjet.min()


file2="track_cropped.csv"

csv_writer=CSV_Tool.CSV_Register()
csv_writer.file_directory=os.path.join(path,file2)
csv_writer.start_write()

for i in range(index_max-index_min+1):
    csv_writer.write_line([[Time2[i],Xobjet2[i],Yobjet2[i],Zobjet2[i],ThetaWheel2[i],ZobjWheel2[i],ManualTracking2[i],ImageName2[i],focusMeasure2[i],focusPhase2[i],MaxfocusMeasure2[i]]])
csv_writer.close()

print('finish')