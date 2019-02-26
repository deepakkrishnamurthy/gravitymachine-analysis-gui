# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 10:46:13 2018

@author: Francois
"""

import csv as csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import scipy.signal as signal
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

path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_07/Ctenaphore_Larvae/ctenaphore10_Continued_nothatched/"
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

print(ymin,ymax)

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
#                           Trajectory function of time
#--------------------------------------------------------------------------
xrange=int(np.ceil(xmax)-np.floor(xmin)+2)
yrange=int(np.ceil(ymax)-np.floor(ymin)+2)
zrange=int(np.ceil(zmax)-np.floor(zmin)+2)

plt.figure(figsize=plt.figaspect(1)*2)
#grid = plt.GridSpec(xrange+yrange+zrange, 1, wspace=1, hspace=8)
#
#ax7=plt.subplot(grid[xrange+yrange:])
ax7=plt.subplot(3,1,3)
plt.plot(Time,ZobjWheel)
plt.xlabel('T (s)')
plt.ylabel('Z (mm)')
plt.xlim( Time[0],Time[-1])
plt.ylim( np.floor(zmin)-1,np.ceil(zmax)+1)

#ax5=plt.subplot(grid[:xrange],sharex=ax7)
ax5=plt.subplot(3,1,1,sharex=ax7)
plt.plot(Time,Xobjet)
plt.ylabel('X (mm)')
p5 = patches.Rectangle((Time[0]-3, -7.5), Time[-1]-Time[0]+6, 15,fill=False,linestyle='--')
ax5.add_patch(p5)
plt.xlim( Time[0],Time[-1])
plt.ylim( np.floor(xmin)-1,np.ceil(xmax)+1)
plt.setp(ax5.get_xticklabels(), visible=False)



#ax6=plt.subplot(grid[xrange:xrange+yrange],sharex=ax7)
ax6=plt.subplot(3,1,2,sharex=ax7)
plt.plot(Time,Yobjet)
p6 = patches.Rectangle((Time[0]-3, 0), Time[-1]-Time[0]+6, 3,fill=False,linestyle='--')
ax6.add_patch(p6)
plt.xlim( Time[0],Time[-1])
plt.ylabel('Y (mm)')
plt.setp(ax6.get_xticklabels(), visible=False)

plt.ylim( np.floor(ymin)-1,np.ceil(ymax)+1)




plt.savefig(path+'Trajectory_in_Time.svg')

plt.show()

#--------------------------------------------------------------------------
#                       Frequency of the blinks
#--------------------------------------------------------------------------

def find_freq(Time,ZObjWheel):
    peaks=signal.find_peaks(ZObjWheel,distance=20,width=20,prominence=(0.06, 4))
    print(len(peaks[0]))
    print(peaks[0])
    freq=len(peaks[0])/(Time[-1]-Time[0])
    return freq,peaks[0]

freq,peaks=find_freq(Time,ZobjWheel)
DeltaTBlink=[]
for i in range(1,len(peaks)-1):
    DeltaTBlink.append(Time[peaks[i+1]]-Time[peaks[i]])
    

DeltaTBlink=np.array(DeltaTBlink)
freq2=np.mean(1/DeltaTBlink)
std=np.std(1/DeltaTBlink)

print('naive freq',freq)
print('freq',freq2,'std',std)

peak_indicator=[0 for i in range(len(Time))]
for j in peaks:
    peak_indicator[j]=ZobjWheel[j]

plt.figure()

plt.plot(Time, ZobjWheel,label='trajectory')
plt.plot(Time,peak_indicator,label='blink')
plt.title('Dendraster3: "Blink" detection')
plt.legend()
plt.savefig(path+'Blink_Detection.svg')

plt.figure()
weights = np.ones_like(DeltaTBlink)/float(len(DeltaTBlink))
plt.hist(DeltaTBlink,bins=40)
plt.title('Ctenaphore10: "Blink" distribution')
plt.xlabel('Delta T (s)')
plt.ylabel('nb of blinks')
plt.savefig(path+'Blink_Distribution.svg')
