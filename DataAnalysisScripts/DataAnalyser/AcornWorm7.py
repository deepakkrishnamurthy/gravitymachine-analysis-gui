# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 10:22:21 2018

@author: Francois
"""

import csv as csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
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

path="F:/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment1_nolight/AcornWorm7/"
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
#                       XZ and YZ Trajectory
#--------------------------------------------------------------------------

def discrete_cmap(N, cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

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
for i in range(7857,7990,12):
    print(i)
    selected_images.append('IMG_'+str(i)+'.tif')
    index=list(ImageName).index(selected_images[-1])
    Ximage2.append(Xobjet[index])
    Zimage2.append(ZobjWheel[index])
    Timage2.append(Time[index])
print(len(Ximage2))  

selected_images1=[]
Ximage1=[]
Zimage1=[]
Timage1=[]

for i in range(7845,7990,1):
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



plt.scatter(Ximage2,Zimage2,c=Timage2,cmap= discrete_cmap(N, cmocean.cm.deep), marker='o',s=0.6)
plt.colorbar(ticks=ticks)
#plt.plot(Ximage1,Zimage1)
plt.xlabel('X (mm)')
plt.ylabel('Z (mm)')



plt.axis('equal')

plt.xlim(xmin2,xmax2)
plt.ylim(zmin2,zmax2)

plt.savefig(path+'XZ_Trajectory.svg',dpi=300)