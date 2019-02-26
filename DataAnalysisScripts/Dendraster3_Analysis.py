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
import scipy.signal as signal
import scipy.stats as stats
import cmocean as cmocean
import os

#--------------------------------------------------------------------------
#                       Plots parameters
#--------------------------------------------------------------------------
from matplotlib import rcParams
from matplotlib import rc

rc('font', family='sans-serif') 
rc('font', serif='Helvetica') 
rc('text', usetex='false') 
rcParams.update({'font.size': 16})

#--------------------------------------------------------------------------
#                       Data importation
#--------------------------------------------------------------------------

#path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_11/Dendraster_starved_11Days_withfood/Dendraster3/"

path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'

file="track.csv"
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
#mean=[]

#for all of them:
#distance=30,width=30,prominence=(0.1, 4)

#starved no food dendraster 1 => freq 0.21112659070720075 std 0.19570059458356384
#starved no food dendraster 2 => freq 0.250360576228786 std 0.13771095472476189
#starved no food dendraster 3 => freq 0.19153938487249564 std 0.1122540557457484


#starved with food dendraster 2 => freq 0.16574662129270823 std 0.15438808750546926
#starved with food dendraster 3 => freq 0.1880014210817598 std 0.12833643567042663
    
#well fed dendraster 1  => 0.2202837536843219 std 0.14427998229025313
#well fed dendraster 2  => freq 0.4268368534512537 std 0.24982695184062523
#well fed dendraster 3  => freq 0.2939107949961588 std 0.13001487950037172

#freq1=[0.21112659070720075,0.250360576228786,0.19153938487249564]
#freq2=[0.16574662129270823,0.1880014210817598]
#freq3=[0.2202837536843219,0.4268368534512537,0.2939107949961588]
#
#std1=[0.19570059458356384,0.13771095472476189,0.1122540557457484]
#std2=[0.15438808750546926,0.12833643567042663]
#std3=[0.14427998229025313,0.24982695184062523,0.13001487950037172]
#
#ypos1=[1,2,3]
#ypos2=[4,5]
#ypos3=[6,7,8]
#
#plt.figure()
#plt.errorbar(ypos1,freq1,yerr=std1,fmt='o',label='straved / no food')
#plt.errorbar(ypos2,freq2,yerr=std2,fmt='o',label='straved / with food')
#plt.errorbar(ypos3,freq3,yerr=std3,fmt='o',label='well fed / no food')
#plt.xlabel('Organisms')
#plt.ylabel('frequency of the blnk (Hz)')
#plt.legend()
#plt.title('frequency of the blinks for the Dendrasters')

  
def find_freq(Time,ZObjWheel):
    peaks = signal.find_peaks(-ZObjWheel,distance=30,width=30,prominence=(0.1, 4))
    freq=len(peaks[0])/(Time[-1]-Time[0])
    return freq,peaks[0]

freq,peaks=find_freq(Time,ZobjWheel)

DeltaTBlink=[]
for i in range(1,len(peaks)-1):
    DeltaTBlink.append(Time[peaks[i+1]]-Time[peaks[i]])
    

DeltaTBlink=np.array(DeltaTBlink)
freq2=np.mean(1/DeltaTBlink)
std=np.std(1/DeltaTBlink)

print('freq',freq2,'std',std)

peak_indicator=np.array([0 for i in range(len(Time))],dtype='bool')
for j in peaks:
    peak_indicator[j]= 1

plt.figure(figsize=(8,6))

indexArray = np.array([i for i in range(len(Time))],dtype='int')

plt.plot(Time, ZobjWheel,color='k',label='trajectory')
for ii in indexArray[peak_indicator]:
    plt.vlines(Time[ii],np.floor(ZobjWheel.min())-1,ZobjWheel[ii],linewidth=1,linestyles='-',alpha=0.5,color='r')

plt.scatter(Time[peak_indicator],ZobjWheel[peak_indicator], 5, color='r',label='blink')
plt.title('"Blink" detection')
plt.legend()
plt.xlim( Time[0],Time[-1])
plt.savefig('Blink_Detection.svg')
plt.ylim( np.floor(ZobjWheel.min())-1,np.ceil(ZobjWheel.max()+1))
plt.show()



plt.figure()
weights = np.ones_like(DeltaTBlink)/float(len(DeltaTBlink))
plt.hist(DeltaTBlink,bins=20)
plt.title('"Blink" distribution')
plt.xlabel('Delta T (s)')
plt.ylabel('nb of blinks')
plt.show()
#plt.savefig(path+'Blink_Distribution.svg')


#--------------------------------------------------------------------------
#                       Distribution of angle
#--------------------------------------------------------------------------
"""
def get_speed(T,X,Y,Z):
    Vx,intercept,r_value,p_value,stderr=stats.linregress(T,X)
    Vy,intercept,r_value,p_value,stderr=stats.linregress(T,Y)
    Vz,intercept,r_value,p_value,stderr=stats.linregress(T,Z)
    return [Vx,Vy,Vz]

speed_blink=[]
for peak in peaks:
    n=50
    speed_blink.append( get_speed(Time[peak:peak+n],Xobjet[peak:peak+n],Yobjet[peak:peak+n],ZobjWheel[peak:peak+n]))

def norm(V):
    return (V[0]**2+V[1]**2+V[2]**2)**0.5

def theta(V):
    return np.arccos(V[2]/norm(V))

def phi(V):
    sin_theta=(1-(V[2]/norm(V))**2)**0.5
    p=np.arccos(V[0]/norm(V)/sin_theta)
    if V[1]<0:
        p=2*np.pi-p
    return p

Theta=[]
Phi=[]

for v in speed_blink:
    Theta.append(theta(v))
    Phi.append(phi(v))
print(len(Phi))
print(len(Theta))
print(Phi)

plt.figure()
weights = np.ones_like(Theta)/float(len(Theta))
plt.hist(Theta,bins=20)
plt.title('Dendraster3: "theta" distribution')
plt.xlabel('theta (rad)')
plt.ylabel('nb of occurences')
plt.xlim(0,np.pi)
plt.savefig(path+'Theta_Distribution.svg')

plt.figure()
#weights = np.ones_like(Phi)/float(len(Phi))
plt.hist(Phi,bins=40)
plt.title('Dendraster3: "phi" distribution')
plt.xlabel('phi (rad)')
plt.ylabel('nb of occurences')

plt.xlim(0,2*np.pi)
plt.savefig(path+'Phi_Distribution.svg')
"""