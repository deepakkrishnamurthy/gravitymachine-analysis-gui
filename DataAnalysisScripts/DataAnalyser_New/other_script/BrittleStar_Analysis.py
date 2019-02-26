# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 15:36:42 2018

@author: Francois
"""
import csv
import CSV_Tool
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
import scipy.optimize as opt
import scipy.stats as stats
import scipy.signal as signal
import matplotlib as mpl
from utils import units_converter as units_converter
import cmocean as cmocean

#--------------------------------------------------------------------------
#                       Plots parameters
#--------------------------------------------------------------------------
from matplotlib import rcParams
from matplotlib import rc
rcParams['axes.titlepad'] = 20 
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

#--------------------------------------------------------------------------
#                       Data importation
#--------------------------------------------------------------------------

path="C:/Users/Francois/Desktop/BrittleStar9_Long_Good_Ytracking/"
file="track.csv"
#Test6_0_0_8mm_movTest2_0_2mm_away
Data=[]
reader = csv.reader(open(path+file,newline=''))
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

#--------------------------------------------------------------------------
#                              Duration
#--------------------------------------------------------------------------

duration=' ( '+str(int(round(Time[-1]/60)))+' mn '+str(int(round(Time[-1]%60)))+' s )'
#--------------------------------------------------------------------------
#                       Boundaries equilibration
#--------------------------------------------------------------------------
xmin=Xobjet.min()
xmax=Xobjet.max()

ymin=Yobjet.min()
ymax=Yobjet.max()


zmin=ZobjWheel.min()
zmax=ZobjWheel.max()

if xmax-xmin>15 and (xmin<-7.5 or xmax>7.5):
    delta_x=-np.mean(Xobjet)
    Xobjet=Xobjet+delta_x
    xmin+=delta_x
    xmax+=delta_x

elif xmin<-7.5:
    delta_x=-7.5-xmin
    Xobjet=Xobjet+delta_x
    xmin+=delta_x
    xmax+=delta_x
    
elif xmax>7.5:
    delta_x=7.5-xmax
    Xobjet=Xobjet+delta_x
    xmin+=delta_x
    xmax+=delta_x

if ymax-ymin>3 and (ymin<0 or ymax>3):
    delta_y=-(np.mean(Yobjet)-1.5)
    Yobjet=Yobjet+delta_y
    ymin+=delta_y
    ymax+=delta_y
    
elif ymin<0:
    delta_y=-ymin
    Yobjet=Yobjet+delta_y
    ymin+=delta_y
    ymax+=delta_y
    
elif ymax>3:
    delta_y=3-ymax
    Yobjet=Yobjet+delta_y
    ymin+=delta_y
    ymax+=delta_y
    
#--------------------------------------------------------------------------
#                       smooth Y and X trajectory
#--------------------------------------------------------------------------
 
def sliding_average(data,n):
    new_data=[]
    if len(data)<=2*n:
        new_data=data
    else:        
        for j in range(0,n):
            y=data[j]
            for i in range(1,j+1):
                y+=data[j+i]+data[j-i]
            new_data.append(y/(2*j+1))
        for j in range(n,len(data)-n):
            y=data[j]
            for i in range(1,n+1):
                y+=data[j-i]+data[j+i]
            new_data.append(y/(2*n+1))
        for j in range(len(data)-n,len(data)):
            y=data[j]
            for i in range(1,len(data)-j):
                y+=data[j+i]+data[j-i]
            new_data.append(y/(2*(len(data)-1-j)+1))
            
    return np.array(new_data)

def regularize(Time,Y):
    f = interpolate.interp1d(Time, Y)
    new_time=np.linspace(Time[0],Time[-1],len(Time))
    new_Y=f(new_time)
    
    return new_time,new_Y
    
def smooth(Time,Y):
    f = interpolate.spline(Time, Y,Time)
    return f(Time)

def get_Vz(Time,ZobjWheel):
    slope,intercept,r_value,p_value,stderr=stats.linregress(Time, ZobjWheel)
    return slope

def find_freq(Time,Xobjet):
    nb_peaks=signal.find_peaks(Xobjet,distance=100,width=50)
    print(len(nb_peaks[0]))
    freq=len(nb_peaks[0])/(Time[-1]-Time[0])
    return freq

def find_radius(Time,Xobjet):
    nb_peaks1=signal.find_peaks(Xobjet,distance=100,width=50)
    nb_peaks2=signal.find_peaks(-Xobjet,distance=150,width=50)
    nb_peaks1,nb_peaks2=nb_peaks1[0],nb_peaks2[0]
    n=min(len(nb_peaks1),len(nb_peaks2))
    diameters=[]
    for i in range(n):
        diameters.append(Xobjet[nb_peaks1[i]]-Xobjet[nb_peaks2[i]])
    radius=np.mean(diameters)/2
    return radius

def find_center(Xobjet,Yobjet):
    return [np.mean(Xobjet),np.mean(Yobjet)]


    
Xobjet2=sliding_average(Xobjet,10)
Yobjet2=sliding_average(Yobjet,100)
Vz=get_Vz(Time,ZobjWheel)
freq=find_freq(Time,Xobjet)
radius_x=find_radius(Time,Xobjet2)
radius_y=find_radius(Time,Yobjet2)
center=find_center(Xobjet,Yobjet)

print('freq',freq)
print('radius x',radius_x)
print('radius y',radius_y)
print('Vz',Vz)
print('center',center)

def find_Zoffset(Xobjet,Yobjet):
    return [np.mean(Xobjet),np.mean(Yobjet)]

#antitrigosens
def helix(t): 
    omega=2*np.pi*freq
    return center[0]+radius_x*np.cos(omega*t),center[1]-radius_y*np.sin(omega*t),ZobjWheel[0]+Vz*t

Xobjet3, Yobjet3,ZobjWheel3= helix(Time)

file2="track2.csv"

csv_writer=CSV_Tool.CSV_Register()
csv_writer.file_directory=path+file2
csv_writer.start_write()

for i in range(len(Time)):
    csv_writer.write_line([[Time[i],Xobjet2[i],Yobjet2[i],Zobjet[i],ThetaWheel[i],ZobjWheel[i],ManualTracking[i],ImageName[i],focusMeasure[i],focusPhase[i],MaxfocusMeasure[i]]])
csv_writer.close()

file3="track3.csv"

csv_writer=CSV_Tool.CSV_Register()
csv_writer.file_directory=path+file3
csv_writer.start_write()

for i in range(len(Time)):
    csv_writer.write_line([[Time[i],Xobjet3[i],Yobjet3[i],Zobjet[i],ThetaWheel[i],ZobjWheel3[i],ManualTracking[i],ImageName[i],focusMeasure[i],focusPhase[i],MaxfocusMeasure[i]]])
csv_writer.close()



print('finish')