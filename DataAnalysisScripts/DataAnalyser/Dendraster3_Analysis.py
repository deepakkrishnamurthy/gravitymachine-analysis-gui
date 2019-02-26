# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 17:48:54 2018

@author: Francois
"""

"""
Created on Mon Jun 11 18:44:12 2018

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

path="C:/Users/Francois/Desktop/Dendraster3/"
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
    
    
"""
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
#                           Zoom on Z axis
#--------------------------------------------------------------------------
T=[]
Z=[]
Timage=[]
Zimage=[]

for i in range(len(Time)):
    if Time[i]>186 and Time[i]<196:
        T.append(Time[i])
        Z.append(ZobjWheel[i])
        if len(ImageName[i])>3:
            Timage.append(Time[i])
            Zimage.append(ZobjWheel[i])

print(len(Zimage),len(Z))
plt.figure()
plt.plot(T,Z)
plt.scatter(Timage,Zimage,color='r',marker='x')
plt.xlim( T[0],T[-1])
plt.ylabel('Z (mm)')
plt.ylabel('t (s)')

plt.savefig(path+'blink_189.svg')

#--------------------------------------------------------------------------
#                       XZ for TimeLaps
#--------------------------------------------------------------------------

def discrete_cmap(N, cmap=None):
    #Create an N-bin discrete colormap from the specified input map

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:
    base=cmap
    colors=cmap(np.arange(256))
    colors=colors[50:]
    cmap=mpl.colors.ListedColormap(colors)
    color_list = cmap(np.linspace(0, 1, N))
    return base.from_list('deep_tronc', color_list, N)




selected_images=[]
Ximage2=[]
Zimage2=[]
Timage2=[]
for i in range(1730,1775,5):
    selected_images.append('IMG_'+str(i)+'.tif')
    index=list(ImageName).index(selected_images[-1])
    Ximage2.append(Xobjet[index])
    Zimage2.append(ZobjWheel[index])
    Timage2.append(Time[index])
    
selected_images1=[]
Ximage1=[]
Zimage1=[]
Timage1=[]
for i in range(1730,1775,1):
    selected_images.append('IMG_'+str(i)+'.tif')
    index=list(ImageName).index(selected_images[-1])
    Ximage1.append(Xobjet[index])
    Zimage1.append(ZobjWheel[index])
    Timage1.append(Time[index])
    

zmax2=round(max(Zimage2),1)+0.3
zmin2=round(min(Zimage2),1)-0.3

xmax2=round(max(Ximage2),1)+0.3
xmin2=round(min(Ximage2),1)-0.3

ticks=[round(i,1) for i in Timage2 ]

print(ticks)

plt.figure()
N=len(Timage2)


plt.plot(Ximage1,Zimage1)
plt.scatter(Ximage2,Zimage2,c=Timage2,cmap= discrete_cmap(N, cmocean.cm.deep), marker='o',s=0.6)
plt.colorbar(ticks=ticks)

plt.xlabel('X (mm)')
plt.ylabel('Z (mm)')



plt.axis('equal')

plt.xlim(xmin2,xmax2)
plt.ylim(zmin2,zmax2)

#cbar3=fig3.colorbar(sc3,ticks=Timage2)
#cbar3.set_label('Time (s)')
plt.savefig(path+'XZ_Trajectory.svg',dpi=300)
"""
#--------------------------------------------------------------------------
#                       Frequency of the blinks
#--------------------------------------------------------------------------

def find_freq(Time,ZObjWheel):
    peaks=signal.find_peaks(-ZObjWheel,distance=100,width=50,prominence=(0.4, 4))
    print(len(peaks[0]))
    freq=len(peaks[0])/(Time[-1]-Time[0])
    return freq,peaks[0]

freq,peaks=find_freq(Time,ZobjWheel)
DeltaTBlink=[]
for i in peaks:
    DeltaTBlink.append(Time[i])
    

DeltaTBlink=np.array(DeltaTBlink)
freq2=np.mean(1/DeltaTBlink)
std=np.std(1/DeltaTBlink)

print('naive freq',freq)
print('freq',freq2,'std',std)

peak_indicator=[0 for i in range(len(Time))]
for j in peaks:
    peak_indicator[j]=ZobjWheel[j]
"""
plt.figure()

plt.plot(Time, ZobjWheel,label='trajectory')
plt.plot(Time,peak_indicator,label='blink')
plt.title('Dendraster3: "Blink" detection')
plt.legend()
plt.savefig(path+'Blink_Detection.svg')
"""
plt.figure()
print(len(DeltaTBlink))
weights = np.ones_like(DeltaTBlink)/float(len(DeltaTBlink))
plt.hist(DeltaTBlink,bins=100)

plt.title('Dendraster3: "Blink" distribution')
plt.xlabel('Delta T (s)')
plt.xlabel('nb of blinks')
plt.savefig(path+'Blink_Distribution.svg')