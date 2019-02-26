# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 18:44:12 2018

@author: Deepak and Francois
"""
import csv as csv
import numpy as np
import matplotlib.pyplot as plt
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
plt.close("all")
#==============================================================================
#                              Plot Parameters   
#==============================================================================
from matplotlib import rcParams
from matplotlib import rc
rcParams['axes.titlepad'] = 20 
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)
plt.rc('font', family='serif')


#==============================================================================
#                               Data Import     
#==============================================================================
#------------------------------------------------------------------------------
# Brittle Star
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar1'
#path="C:/Users/Francois/Desktop/StarFish1/"
#path = "/Users/deepak/Dropbox/GravityMachine/TrackAnalysis/TestData/seacucmber9_Auto/"

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto/'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6highfreq/'

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_withfood/Dendraster3'
#------------------------------------------------------------------------------
# Acorn Worm
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm2'
#path='/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm3'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm4'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm7'

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment1_nolight/AcornWorm7'

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar9_Long_Good_Ytracking'

#------------------------------------------------------------------------------
# Sea Urchin
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin/SeaUrchin8'
#------------------------------------------------------------------------------
# Sea Cucumber
#------------------------------------------------------------------------------
#path= '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber7_Manual'
#------------------------------------------------------------------------------
# Dendraster
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_well_fed_11Days_nofood/Dendraster3'
#------------------------------------------------------------------------------
# Polychaete
#------------------------------------------------------------------------------
path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D/Polychaete6_longest_6mn'
#------------------------------------------------------------------------------
# Starfish
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish10'
#------------------------------------------------------------------------------
# Snail
#------------------------------------------------------------------------------
#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail10'


file="track.csv"
dataFolder, TrackName = os.path.split(path)

#dataFolder = '/Users/deepak/Dropbox/GravityMachine/Presentations/Figures/'

print(50*'*')
print('Folder in which to save data: {}'.format(dataFolder))
print(50*'*')

print(50*'*')
print('Tail: {}'.format(TrackName))

resultFolder = os.path.join(dataFolder,'TrackResults')

if(not os.path.exists(resultFolder)):
    os.makedirs(resultFolder)

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

print(ymin,ymax)

zmin=ZobjWheel.min()
zmax=ZobjWheel.max()

if xmax-xmin>15 and (xmin<-7.5 or xmax>7.5):
    delta_x=np.mean(Xobjet)
    Xobjet=Xobjet-delta_x
    xmin-=delta_x
    xmax-=delta_x

if ymax-ymin>3 and (ymin<0 or ymax>3):
    delta_y=(np.mean(Yobjet)-1.5)
    Yobjet=Yobjet-delta_y
    ymin-=delta_y
    ymax-=delta_y
    


#--------------------------------------------------------------------------
#                            Plot the box
#--------------------------------------------------------------------------

 
def x_y_edge(ax,x_range, y_range, z_range,alpha1,alpha2):
    xx, yy = np.meshgrid(x_range, y_range)

    for value in [0, 1]:
        ax.plot_wireframe(xx, yy, z_range[value], color="b",alpha=alpha1,linewidth=0)
        ax.plot_surface(xx, yy, z_range[value], color="b", alpha=alpha2)


def y_z_edge(ax,x_range, y_range, z_range,alpha1,alpha2):
    yy, zz = np.meshgrid(y_range, z_range)

    for value in [0, 1]:
        ax.plot_wireframe(x_range[value], yy, zz, color="b",alpha=alpha1,linewidth=0.7)
        ax.plot_surface(x_range[value], yy, zz, color="b", alpha=alpha2)


def x_z_edge(ax,x_range, y_range, z_range,alpha1,alpha2):
    xx, zz = np.meshgrid(x_range, z_range)

    for value in [0, 1]:
        ax.plot_wireframe(xx, y_range[value], zz, color="b",alpha=alpha1,linewidth=0.7)
        ax.plot_surface(xx, y_range[value], zz, color="b", alpha=alpha2)


def rect_prism(ax,x_range, y_range, z_range,alpha1,alpha2):
    x_z_edge(ax,x_range, y_range, z_range,alpha1,alpha2)
    #x_y_edge(ax,x_range, y_range, z_range,alpha1,alpha2)
    y_z_edge(ax,x_range, y_range, z_range,alpha1,alpha2)
  
def draw_channel(ax,zmin,zmax):
    rect_prism(ax,np.array([-7.5, 7.5]),np.array([-7.5, 7.5]),np.array([zmin, zmax]),0,0)
    rect_prism(ax,np.array([-7.5, 7.5]),np.array([0, 3]),np.array([zmin, zmax]),1,0.1)

#==============================================================================
#                       Calculations using Raw Data  
#==============================================================================
##                         data equalization
##--------------------------------------------------------------------------

T = np.linspace(Time[0],Time[-1],len(Time))  # Create a equi-spaced (in time) vector for the data.

# Sampling Interval
dT = T[1]-T[0]
print(75*'*')
print('Sampling Interval: {} s'.format(dT))
print('Sampling Frequency: {} Hz'.format(1/dT))
print(75*'*')

func_X = interpolate.interp1d(Time,Xobjet)
func_Y = interpolate.interp1d(Time,Yobjet)
func_Z = interpolate.interp1d(Time,ZobjWheel)

X=func_X(T)     # Interpolated object positions
Y=func_Y(T)     # Interpolated object positions
Z=func_Z(T)     # Interpolated object positions

Tmin = np.min(T)
Tmax = np.max(T)
#Tmin = 10
Tmax = 300
mask = (T >= Tmin) & (T<=Tmax)
T = T[mask]
X = X[mask]
Y = Y[mask]
Z = Z[mask]

##--------------------------------------------------------------------------
##                       Diffusivity
##--------------------------------------------------------------------------
N = int(len(X)/2)

def squared_displacement(data,i,n):
    # n is the track len over which an ensemble is calculated
    return (data[i:i+n]-data[i])**2

def squared_vector_3d(X,Y,Z,i,n):
    
    return (X[i:i+n] - X[i])**2 + (Y[i:i+n] - Y[i])**2 + (Z[i:i+n] - Z[i])**2 
    

sqDisp = squared_vector_3d(X,Y,Z,0,len(X))
Disp = (sqDisp)**(1/2)

MSD_X_array = np.zeros((N,))
MSD_Y_array = np.zeros((N,))
MSD_Z_array = np.zeros((N,))
MSD_total_array = np.zeros((N,))
trackLenArray = np.zeros((N))

MSDisp_Vector=[]
# Calculate the mean over the squared displacements
for i in range(1,N):
    MSD_X_array += squared_displacement(X,i,N)
    MSD_Y_array += squared_displacement(Y,i,N)
    MSD_Z_array += squared_displacement(Z,i,N)
    MSD_total_array += squared_vector_3d(X,Y,Z,i,N)
    
    
MSD_X = MSD_X_array/N
MSD_Y = MSD_Y_array/N
MSD_Z = MSD_Z_array/N
MSD_total = MSD_total_array/N

#    MSDisp_X.append(mean_square_displacement(X,i))
#    MSDisp_Y.append(mean_square_displacement(Y,i))
#    MSDisp_Z.append(mean_square_displacement(Z,i))
#    MSDisp_Vector.append(mean_square_vector(i))



DeltaT=Time[:N]


##--------------------------------------------------------------------------
##                      MSD of track segments away from the wall
##--------------------------------------------------------------------------
# Mark the track based on if it is in the wall vicinity.
# Calculate the MSD of the track segments which are far away from the wall
# Find the minimum and maximum extents of the track

#Ymin = 0
#Ymax = 3
#Xmin = -7.5
#Xmax = 7.5

D = 0.1             # Measured major axis dimension of the organism
Xmin = np.min(X)    
Xmax = np.max(X)

Ymin = np.min(Y)
Ymax = np.max(Y)

Zmin = np.min(Z)
Zmax = np.max(Z)



# Binary Mask of the track: Near Wall: 1 Away From Wall: 0
atWall = (X < (Xmin+D))|(X>(Xmax-D))|(Y<(Ymin+D))|(Y>(Ymax-D))
#print(np.sum(atWall))
#
#subTrackIndex = 0
#counter = 0
#startIndex = {}
#stopIndex = {}
## If the first element is part of the track then initialize the subTrack
#if(atWall[0]==0):
#    startIndex[counter]=0
#    
#for ii in range(1,len(atWall)):
##     print(ii)
##     print(counter)
#    
#    if(atWall[ii-1] == 0 and atWall[ii] == 1):
#        stopIndex[counter] = ii-1
#        counter += 1    
#    elif (atWall[ii-1]==1 and atWall[ii]== 0):
#        startIndex [counter] = ii
#        
## if not stopIndex:
##     stopIndex[counter]=len(atWall)-1
#    
#if (len(stopIndex.keys()) < len(startIndex.keys())):
#    stopIndex[counter] = len(atWall)-1
#
#print(startIndex)
#print(stopIndex)
#
#subTrack={}
#sqDispSubTrack = {}
#trackLens = {}
## Create subtracks
#print(startIndex.keys())
#for ii in startIndex.keys():
#   
#    subTrack[ii] = np.array([X[startIndex[ii]:stopIndex[ii]+1],Y[startIndex[ii]:stopIndex[ii]+1],Z[startIndex[ii]:stopIndex[ii]+1]])
#   
#    sqDispSubTrack[ii] = squared_vector_3d(subTrack[ii][0,:],subTrack[ii][1,:],subTrack[ii][2,:],0,np.size(subTrack[ii],axis=1))
#    trackLens[ii] = np.size(subTrack[ii],axis=1)
#    
## Calculate the MSD using the ensemble average of the subtracks
#maxTrackLen = max(trackLens.values())
#numSubTracks = len(subTrack.keys())
#
#print('No:of subtracks : {}'.format(numSubTracks))
#
#SumSqDisp_subTracks = np.zeros(maxTrackLen,)
#meanWeights = np.zeros(maxTrackLen,)
#
#for ii in range(0,numSubTracks):
#    for jj in range(0,np.size(subTrack[ii],axis=1)):
#        SumSqDisp_subTracks[jj] += sqDispSubTrack[ii][jj]
#        meanWeights[jj]+=1
#
#MSD_subTracks = SumSqDisp_subTracks/meanWeights
#
#T_subTrack = np.array(T[0:maxTrackLen])    
  
##--------------------------------------------------------------------------
##                      Power Spectrum of Tracks (Frequency Analysis)
##--------------------------------------------------------------------------
# First fit a <3 order polynomial to remove fluctuating DC components

#Xcoeff, StatsX = Poly.polyfit(T,X,2,full=True)
#Ycoeff, StatsY = Poly.polyfit(T,Y,2,full=True)
#Zcoeff, StatsZ = Poly.polyfit(T,Z,2,full=True)
#
#
#Xfit = np.zeros_like(X)
#Yfit = np.zeros_like(Y)
#Zfit = np.zeros_like(Z)
#
#for i in range(0,len(Zcoeff)):
#    Xfit += Xcoeff[i]*(T**i)
#    Yfit += Ycoeff[i]*(T**i)
#    Zfit += Zcoeff[i]*(T**i)
#    
#Xfluc = X - Xfit
#Yfluc = Y - Yfit
#Zfluc = Z - Zfit
#    
#    
#plt.figure()
#plt.subplot(311)
#plt.plot(T,X,marker='o',color='r')
#plt.plot(T,Xfit,color='r')
#
#plt.subplot(312)
#plt.plot(T,Y,marker='o',color='b')
#plt.plot(T,Yfit,color='b')
#
#plt.subplot(313)
#plt.plot(T,Z,marker='o',color='g')
#plt.plot(T,Zfit,color='g')
#
#plt.show(block=False)
#
#plt.figure()
#plt.subplot(311)
#plt.plot(T,Xfluc,marker='o',color='r')
#
#plt.subplot(312)
#plt.plot(T,Yfluc,marker='o',color='b')
#
#plt.subplot(313)
#plt.plot(T,Zfluc,marker='o',color='g')
#plt.show()
#
#
#
#print('*'*50)
#print('Mean of fluctuating component: {}'.format(np.mean(Zfluc)))
#print('*'*50)
#
#    
#freq = 1/float(T[2]-T[1])
#print('*'*50)
#print('Sampling Frequency: {}'.format(freq))
#print('*'*50)
#
## Calculate the Frequency spectrum using a STFT
#f, t, Zxx = signal.stft(Zfluc, freq, nperseg=1024)
#
#ax1 = plt.pcolormesh(t, f, np.abs(Zxx),cmap=cmocean.cm.deep)
#plt.title('STFT Magnitude')
#plt.ylabel('Frequency [Hz]')
#plt.xlabel('Time [sec]')
#plt.axis([t.min(), t.max(), f.min(), 1])
#plt.colorbar(ax1)
#plt.show()


#==============================================================================
#                               PLOTS     
#==============================================================================

#--------------------------------------------------------------------------
#                       3D Trajectory
#--------------------------------------------------------------------------


#aspect=(zmax-zmin)/15.
#
#fig = plt.figure(figsize=plt.figaspect(aspect))
#ax = fig.gca(projection='3d')
#
#draw_channel(ax,zmin,zmax)
#
#sc1=ax.scatter(Xobjet, Yobjet, ZobjWheel, marker='o',s=0.6,c=Time, cmap=plt.hot())
#ax.plot(Xobjet, Yobjet, ZobjWheel,linewidth=0.4)
#ax.set_xlabel('X (mm)')
#ax.set_ylabel('Y (mm)')
#ax.set_zlabel('Z (mm)')
#cbar1=fig.colorbar(sc1)
#cbar1.set_label('Time (s)')
#
#
#
#
##--------------------------------------------------------------------------
##                       XY Trajectory
##--------------------------------------------------------------------------
#
#fig2=plt.figure()
#ax2 = fig2.add_axes([0.2,0.2,0.8,0.6])
#sc2=plt.scatter(Xobjet,Yobjet,c=Time, marker='o',s=0.6)
#plt.plot(Xobjet,Yobjet,linewidth=0.4)
#
#p2 = patches.Rectangle((-7.5, 0), 15, 3,fill=False)
#ax2.add_patch(p2)
#
#plt.xlim(-8,8)
#plt.ylim(-1,4)
#plt.xlabel('X (mm)')
#plt.ylabel('Y (mm)')
#plt.title('XY Trajectory'+duration)
#cbar2=fig2.colorbar(sc2)
#cbar2.set_label('Time (s)')
#plt.gca().set_aspect('equal', adjustable='box')
#plt.savefig(path+'XY_Trajectory.png',dpi=300)
#
#
##--------------------------------------------------------------------------
##                       XZ and YZ Trajectory
##--------------------------------------------------------------------------
#
#
#fig3=plt.figure()
#ax3 = fig3.add_axes([0.2,0.2,0.8,0.6])
#sc3=plt.scatter(Xobjet,ZobjWheel,c=Time, marker='o',s=0.6)
#plt.plot(Xobjet,ZobjWheel,color='gray',linewidth=0.4)
#
#p3 = patches.Rectangle((-7.5, zmin-3), 15, zmax-zmin+6,fill=False)
#ax3.add_patch(p3)
#
#plt.xlabel('X (mm)')
#plt.ylabel('Z (mm)')
#
#plt.xlim(-8,8)
#plt.ylim(zmin-1,zmax+1)
#
#plt.title('XZ Trajectory'+duration)
#cbar3=fig3.colorbar(sc3)
#cbar3.set_label('Time (s)')
#plt.gca().set_aspect('equal', adjustable='box')
#plt.savefig(path+'XZ_Trajectory.png',dpi=300)
#
#
#fig4=plt.figure()
#ax4 = fig4.add_axes([0.2,0.2,0.8,0.6])
#sc4=plt.scatter(Yobjet,ZobjWheel,c=Time, marker='o',s=0.6)
#plt.plot(Yobjet,ZobjWheel,color='gray',linewidth=0.4)
#
#p4 = patches.Rectangle((0, zmin-3), 3, zmax-zmin+6,fill=False)
#ax4.add_patch(p4)
#
#plt.xlabel('Y (mm)')
#plt.ylabel('Z (mm)')
#
#plt.xlim(-1,4)
#plt.ylim(zmin-1,zmax+1)
#
#plt.title('YZ Trajectory'+duration)
#cbar4=fig4.colorbar(sc4)
#cbar4.set_label('Time (s)')
#plt.gca().set_aspect('equal', adjustable='box')
#plt.savefig(path+'YZ_Trajectory.png',dpi=300)
#
##--------------------------------------------------------------------------
##                           Trajectory function of time
##--------------------------------------------------------------------------
xrange=int(np.ceil(xmax)-np.floor(xmin)+2)
yrange=int(np.ceil(ymax)-np.floor(ymin)+2)
zrange=int(np.ceil(zmax)-np.floor(zmin)+2)

#plt.figure(figsize=plt.figaspect(1)*2)
#grid = plt.GridSpec(xrange+yrange+zrange, 1, wspace=1, hspace=8)
#
#ax7=plt.subplot(grid[xrange+yrange:])
#plt.plot(T,Z)
#plt.scatter(T[atWall],Z[atWall],c='r')
#
#plt.xlabel('T (s)')
#plt.ylabel('Z (mm)')
#plt.xlim( T[0],T[-1])
#plt.ylim( np.floor(zmin)-1,np.ceil(zmax)+1)
#
#ax5=plt.subplot(grid[:xrange],sharex=ax7)
#plt.plot(T,X)
#plt.scatter(T[atWall],X[atWall],c='r')
#plt.ylabel('X (mm)')
#p5 = patches.Rectangle((T[0]-3, -7.5), T[-1]-T[0]+6, 15,fill=False,linestyle='--')
#ax5.add_patch(p5)
#plt.xlim( T[0],T[-1])
#plt.ylim( np.floor(xmin)-1,np.ceil(xmax)+1)
#plt.setp(ax5.get_xticklabels(), visible=False)
#
#plt.title('Trajectory projection'+duration)
#
#ax6=plt.subplot(grid[xrange:xrange+yrange],sharex=ax7)
#plt.plot(T,Y)
#plt.scatter(T[atWall],Y[atWall],c='r')
#p6 = patches.Rectangle((T[0]-3, 0), T[-1]-T[0]+6, 3,fill=False,linestyle='--')
#ax6.add_patch(p6)
#plt.xlim( T[0],T[-1])
#plt.ylabel('Y (mm)')
#plt.setp(ax6.get_xticklabels(), visible=False)
#
#plt.ylim( np.floor(ymin)-1,np.ceil(ymax)+1)
#
##plt.savefig(path+'Trajectory_in_Time.png',dpi=300)
#
#plt.show(block=False)


plt.figure(figsize=plt.figaspect(1)*2)
grid = plt.GridSpec(xrange+yrange+zrange, 1, wspace=1, hspace=8)

ax7=plt.subplot(313)
plt.plot(T,Z)
plt.scatter(T[atWall],Z[atWall],c='r')

plt.xlabel('T (s)')
plt.ylabel('Z (mm)')
plt.xlim( T[0],T[-1])
plt.ylim( np.floor(zmin)-1,np.ceil(zmax)+1)

ax5=plt.subplot(311)
plt.plot(T,X)
plt.scatter(T[atWall],X[atWall],c='r')
plt.ylabel('X (mm)')
p5 = patches.Rectangle((T[0]-3, -7.5), T[-1]-T[0]+6, 15,fill=False,linestyle='--')
ax5.add_patch(p5)
plt.xlim( T[0],T[-1])
plt.ylim( np.floor(xmin)-1,np.ceil(xmax)+1)
plt.setp(ax5.get_xticklabels(), visible=False)

plt.title('Trajectory projection'+duration)

ax6=plt.subplot(312)
plt.plot(T,Y)
plt.scatter(T[atWall],Y[atWall],c='r')
p6 = patches.Rectangle((T[0]-3, 0), T[-1]-T[0]+6, 3,fill=False,linestyle='--')
ax6.add_patch(p6)
plt.xlim( T[0],T[-1])
plt.ylabel('Y (mm)')
plt.setp(ax6.get_xticklabels(), visible=False)

plt.ylim( np.floor(ymin)-1,np.ceil(ymax)+1)

plt.savefig(os.path.join(resultFolder,TrackName+'Trajectory_in_Time.eps'),dpi=300)
plt.savefig(os.path.join(resultFolder,TrackName+'Trajectory_in_Time.png'),dpi=300)

plt.show(block=False)
###--------------------------------------------------------------------------
## Plot of displacement
###--------------------------------------------------------------------------
#plt.figure()
#plt.plot(T,Disp,color='r')
#plt.title('Squared Displacement' )
#plt.xlabel('Elapsed Time (s)')
#plt.legend()
#plt.ylabel('Squared Displacement')
#plt.show(block=False)
#
#
###--------------------------------------------------------------------------
## Plot the Mean-Squared Displacements
###--------------------------------------------------------------------------
plt.figure()
#plt.plot(DeltaT,MSD_X, label='X')
#plt.plot(DeltaT,MSD_Y, label='Y')
#plt.plot(DeltaT,MSD_Z, label='Z')
#plt.plot(DeltaT,MSD_total, label='Vector')

plt.loglog(DeltaT,MSD_X, label='X')
plt.loglog(DeltaT,MSD_Y, label='Y')
plt.loglog(DeltaT,MSD_Z, label='Z')
plt.loglog(DeltaT,MSD_total, label='Vector')
plt.loglog(DeltaT[int(N/5):],DeltaT[int(N/5):],label='Linear Slope',color='k',linestyle='-')
plt.loglog(DeltaT[int(N/5):],0.001*DeltaT[int(N/5):]**2,label='Quadratic Slope',color='k',linestyle='--')

plt.title('Mean Square Displacement' )
plt.xlabel('Elapsed Time (s)')
plt.legend()
plt.ylabel('Mean Square Displacement')
plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MSD_awayFrom Wall.eps'),dpi=300)  
plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MSD_awayFrom Wall.png'),dpi=300) 
plt.show(block=False)

##--------------------------------------------------------------------------
# Mean-Squared-Displacement of Track segments away from wall
##--------------------------------------------------------------------------
#print(MSD_subTracks)
#plt.figure()
##plt.plot(DeltaT,MSD_X, label='X')
##plt.plot(DeltaT,MSD_Y, label='Y')
##plt.plot(DeltaT,MSD_Z, label='Z')
##plt.plot(DeltaT,MSD_total, label='Vector')
#
#plt.loglog(T_subTrack,MSD_subTracks, label='MSD of subtracks')
#plt.loglog(DeltaT,MSD_total, label='MSD of Full Track')
#plt.loglog(DeltaT[int(N/5):],DeltaT[int(N/5):],label='Linear Slope',color='k',linestyle='-')
#plt.loglog(DeltaT[int(N/5):],0.001*DeltaT[int(N/5):]**2,label='Quadratic Slope',color='k',linestyle='--')
#
#plt.title('Mean Square Displacement' )
#plt.xlabel('Elapsed Time (s)')
#plt.legend()
#plt.ylabel('Mean Square Displacement')  
#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MSD_awayFrom Wall.eps'),dpi=300)  
#plt.savefig(os.path.join(resultFolder,TrackName+'_'+'MSD_awayFrom Wall.png'),dpi=300) 
#plt.show(block=False)

##--------------------------------------------------------------------------
##                      Velocity autocorrelation
##--------------------------------------------------------------------------

Vx=[]
Vy=[]
Vz=[]

#X_smooth = pd.rolling_mean(X, 10)
#Y_smooth = pd.rolling_mean(Y, 10)
#Z_smooth = pd.rolling_mean(Z, 10)
#
## Plot the instantaneous velocities
#plt.figure()
#plt.subplot(311)
##plt.plot(T[0:-1],Vx,color='r')
#plt.plot(T,X_smooth,color='r')
#plt.xlabel('Elapsed Time (s)')
#plt.ylabel('X (mm)')
#
#
#plt.subplot(312)
##plt.plot(T[0:-1],Vy,color='b')
#plt.plot(T,Y_smooth,color='g')
#plt.xlabel('Elapsed Time (s)')
#plt.ylabel('Y (mm)')
#
#plt.subplot(313)
##plt.plot(T[0:-1],Vz,color='g')
#plt.plot(T,Z_smooth,color='b')
#plt.xlabel('Elapsed Time (s)')
#plt.ylabel('Z (mm)')

for i in range(len(X)-1):
    Vx.append((X[i+1]-X[i])/(T[i+1]-T[i]))
    Vy.append((Y[i+1]-Y[i])/(T[i+1]-T[i]))
    Vz.append((Z[i+1]-Z[i])/(T[i+1]-T[i])) 
    
#for i in range(len(X)-1):
#    Vx.append((X_smooth[i+1]-X_smooth[i])/(T[i+1]-T[i]))
#    Vy.append((Y_smooth[i+1]-Y_smooth[i])/(T[i+1]-T[i]))
#    Vz.append((Z_smooth[i+1]-Z_smooth[i])/(T[i+1]-T[i])) 
Vx=np.array(Vx)
Vy=np.array(Vy)
Vz=np.array(Vz)




#Vx_smooth = ndimage.gaussian_filter(Vx, sigma= 10.0, order= 0)
#Vy_smooth = ndimage.gaussian_filter(Vy, sigma= 10.0, order= 0)
#Vz_smooth = ndimage.gaussian_filter(Vz, sigma= 10.0, order= 0)

Vx_smooth = pd.rolling_mean(Vx, 5)
Vy_smooth = pd.rolling_mean(Vy, 5)
Vz_smooth = pd.rolling_mean(Vz, 5)

#Vx_smooth = Vx
#Vy_smooth = Vy
#Vz_smooth = Vz

# Plot the instantaneous velocities
plt.figure()
plt.subplot(311)
#plt.plot(T[0:-1],Vx,color='r')
plt.plot(T[0:-1],Vx_smooth,color='r')
plt.xlabel('Elapsed Time (s)')
plt.ylabel('Velocity X-component (mm/s)')


plt.subplot(312)
#plt.plot(T[0:-1],Vy,color='b')
plt.plot(T[0:-1],Vy_smooth,color='g')
plt.xlabel('Elapsed Time (s)')
plt.ylabel('Velocity Y-component (mm/s)')

plt.subplot(313)
#plt.plot(T[0:-1],Vz,color='g')
plt.plot(T[0:-1],Vz_smooth,color='b')
plt.xlabel('Elapsed Time (s)')
plt.ylabel('Velocity Z-component (mm/s)')

plt.savefig(os.path.join(resultFolder,TrackName+'_'+'Velocity.png'),dpi=300)  


plt.show()

# Choose the window size over which we want to extract the autocorrelation
T_window = 50


N2=int(T_window/dT)


V = np.zeros((3,len(Vx)))
V[0,:] = Vx_smooth
V[1,:] = Vy_smooth
V[2,:] = Vz_smooth

print(np.shape(Vx_smooth))
print(N2)


def autocorrelation(data,i,n):
    
    return (data[i:i+n]*data[i])

def autocorrelation_3D(data,i,n):
    return (data[0,i:i+n]*data[0,i] + data[1,i:i+n]*data[1,i] + data[2,i:i+n]*data[2,i])

autocorrelation_Vx=np.zeros((1,N2))
autocorrelation_Vy=np.zeros((1,N2))
autocorrelation_Vz=np.zeros((1,N2))
autocorrelation_V=np.zeros((1,N2))

Vx_mean = np.nanmean(Vx)
Vy_mean = np.nanmean(Vy)
Vz_mean = np.nanmean(Vz)

Vx_std = np.nanstd(Vx)
Vy_std = np.nanstd(Vy)
Vz_std = np.nanstd(Vz)

Vx_max = np.nanmax(np.abs(Vx_smooth))
Vy_max = np.nanmax(np.abs(Vy_smooth))
Vz_max = np.nanmax(np.abs(Vz_smooth))



print(50*'*')
print('Mean velocity in X direction: {} mm/s'.format(Vx_mean))
print('Mean velocity in Y direction: {} mm/s'.format(Vy_mean))
print('Mean velocity in Z direction: {} mm/s'.format(Vz_mean))
print(50*'*')

print(50*'*')
print('Max velocity in X direction: {} mm/s'.format(Vx_max))
print('Max velocity in Y direction: {} mm/s'.format(Vy_max))
print('Max velocity in Z direction: {} mm/s'.format(Vz_max))
print(50*'*')

print(50*'*')
print('Vz/Vx: {}'.format(Vz_mean/Vx_mean))
print('Vz/Vy {}'.format(Vz_mean/Vy_mean))
print('Vx/Vy: {}'.format(Vx_mean/Vy_mean))
print(50*'*')

#print(50*'*')
#print('...Calculating velocity autocorrelation over a time window of {} s'.format(T_window))
#print(50*'*')
#
#for i in range(0,len(Vx)-N2):
#    autocorrelation_Vx += autocorrelation(Vx_smooth,i,N2)
#    autocorrelation_Vy += autocorrelation(Vy_smooth,i,N2)
#    autocorrelation_Vz += autocorrelation(Vz_smooth,i,N2)
#    autocorrelation_V += autocorrelation_3D(V,i,N2)
#
#DeltaT2=T[:N2] 
#
#
#
#
#
#
#meanAutocorrelation_Vx = autocorrelation_Vx.T/N2
#meanAutocorrelation_Vy = autocorrelation_Vy.T/N2
#meanAutocorrelation_Vz = autocorrelation_Vz.T/N2
#meanAutocorrelation= autocorrelation_V.T/N2
#
#meanAutocorrelation_Vx = meanAutocorrelation_Vx/meanAutocorrelation_Vx[0]
#meanAutocorrelation_Vy = meanAutocorrelation_Vy/meanAutocorrelation_Vy[0]
#meanAutocorrelation_Vz = meanAutocorrelation_Vz/meanAutocorrelation_Vz[0]
#
#
#print(np.shape(DeltaT2))
#print(np.shape(meanAutocorrelation_Vx))
##------------------------------------------------------------------------------
## Linear regression to find the slope of the decay
##------------------------------------------------------------------------------
#minBound = 0.01
#mask_x = meanAutocorrelation_Vx <= minBound
#mask_y = meanAutocorrelation_Vy <= minBound
#mask_z = meanAutocorrelation_Vz <= minBound
#
## Find the first non-zero element
#index_x = next((i for i, x in enumerate(mask_x) if mask_x[i]), None)
#index_y = next((i for i, x in enumerate(mask_y) if mask_y[i]), None)
#index_z = next((i for i, x in enumerate(mask_z) if mask_z[i]), None)
#
#
#
#print(DeltaT2[index_x])
#print(DeltaT2[index_y])
#print(DeltaT2[index_z])
#
#
##maxIndex_x = index_x[0]
##maxIndex_y = index_y[0]
##maxIndex_z = index_z[0]
##
##print(DeltaT2[maxIndex_x])
##print(DeltaT2[maxIndex_y])
##print(DeltaT2[maxIndex_z])
#
#Treg_x = DeltaT2[0:index_x]
#Treg_y = DeltaT2[0:index_y]
#Treg_z = DeltaT2[0:index_z]
#
#meanAutoCorr_trans_x = meanAutocorrelation_Vx[0:index_x]
#meanAutoCorr_trans_y = meanAutocorrelation_Vy[0:index_y]
#meanAutoCorr_trans_z = meanAutocorrelation_Vz[0:index_z]
#
#Xcoeff, StatsX = Poly.polyfit(Treg_x,np.log(meanAutoCorr_trans_x),1,full=True)
#Ycoeff, StatsY = Poly.polyfit(Treg_y,np.log(meanAutoCorr_trans_y ),1,full=True)
#Zcoeff, StatsZ = Poly.polyfit(Treg_z,np.log(meanAutoCorr_trans_z ),1,full=True)
##
#autoCorrFit_x = Xcoeff[0] + Xcoeff[1]*Treg_x
#autoCorrFit_y = Ycoeff[0] + Ycoeff[1]*Treg_y
#autoCorrFit_z = Zcoeff[0] + Zcoeff[1]*Treg_z
##
#plt.figure()
##ax1 = plt.semilogy(DeltaT2,meanAutocorrelation_Vx, label='Vx')
##ax2 = plt.semilogy(DeltaT2,meanAutocorrelation_Vy, label='Vy')
##ax3 = plt.semilogy(DeltaT2,meanAutocorrelation_Vz, label='Vz')
#
#
#ax1 = plt.plot(DeltaT2,meanAutocorrelation_Vx, label='Vx')
#ax2 = plt.plot(DeltaT2,meanAutocorrelation_Vy, label='Vy')
#ax3 = plt.plot(DeltaT2,meanAutocorrelation_Vz, label='Vz')
#
#
#
#plt.title('Autocorrelation in speed function of DeltaT' )
#plt.xlabel('Time (s)')
#plt.legend()
#plt.ylabel('Speed autocorrelation function') 
#plt.savefig(os.path.join(dataFolder,TrackName+'_'+'VelocityAutocorrelation_loglinear.eps'),dpi=300)  
#plt.savefig(os.path.join(dataFolder,TrackName+'_'+'VelocityAutocorrelation_loglinear.png'),dpi=300)  
#
#plt.show(block=True)
#
##
##
#plt.figure()
##ax1 = plt.plot(Treg_x,meanAutoCorr_trans_x, label='Vx')
##ax2 = plt.plot(Treg_y,meanAutoCorr_trans_y, label='Vy')
##ax3 = plt.plot(Treg_z,meanAutoCorr_trans_z, label='Vz')
##
##ax4 = plt.plot(Treg_x,np.exp(autoCorrFit_x), label='Fit Vx')
##ax5 = plt.plot(Treg_y,np.exp(autoCorrFit_y), label='Fit Vy')
##ax6 = plt.plot(Treg_z,np.exp(autoCorrFit_z), label='Fit Vz')
#
#ax1 = plt.semilogy(Treg_x,meanAutoCorr_trans_x, label='Vx')
#ax2 = plt.semilogy(Treg_y,meanAutoCorr_trans_y, label='Vy')
#ax3 = plt.semilogy(Treg_z,meanAutoCorr_trans_z, label='Vz')
#
#ax4 = plt.semilogy(Treg_x,np.exp(autoCorrFit_x), label='Fit Vx')
#ax5 = plt.semilogy(Treg_y,np.exp(autoCorrFit_y), label='Fit Vy')
#ax6 = plt.semilogy(Treg_z,np.exp(autoCorrFit_z), label='Fit Vz')
#plt.title('Squared Autocorrelation in speed function of DeltaT' )
#plt.xlabel('Time (s)')
#plt.legend()
#plt.ylabel('Squared Speed autocorrelation function') 
#plt.show()
#
#deCorrTime_x = abs(1/Xcoeff[1])
#deCorrTime_y = abs(1/Ycoeff[1])
#deCorrTime_z = abs(1/Zcoeff[1])
#
#print(50*'*')
#print('Decorrelation Time for Vx: {} s'.format(deCorrTime_x))
#print('Decorrelation Time for Vy: {} s'.format(deCorrTime_y))
#print('Decorrelation Time for Vz: {} s'.format(deCorrTime_z))
#print(50*'*')

#==============================================================================
#                               SAVE STUFF    
#==============================================================================
# Save all computed results
#--------------------------------------------------------------------------------------------------
# Open and Create a file to store the track statistics
#--------------------------------------------------------------------------------------------------

FileName = TrackName + '_Statistics.csv'

csv.register_dialect('myDialect', delimiter=',', quoting=csv.QUOTE_MINIMAL)

header = [['Vx Mean', 'Vy Mean','Vz Mean','Vx std','Vy std','Vz std','Vx max','Vy max','Vz max']]
data = [[Vx_mean, Vy_mean, Vz_mean, Vx_std, Vy_std, Vz_std, Vx_max, Vy_max, Vz_max]]
currFile = open(os.path.join(resultFolder,FileName), 'w')
			 
writer = csv.writer(currFile , dialect='myDialect')
writer.writerows(header)
writer.writerows(data)
currFile.close()


###--------------------------------------------------------------------------
###                  Probability distribution of speed
###--------------------------------------------------------------------------
#
#
#plt.figure()
#weights_x = np.ones_like(Vx)/float(len(Vx))
#weights_y = np.ones_like(Vy)/float(len(Vy))
#weights_z = np.ones_like(Vz)/float(len(Vz))
#plt.hist([Vx,Vy,Vz], bins=200,weights=[weights_x,weights_y,weights_z], label=['Vx','Vy','Vz']) #density=True)
#plt.xlabel('speed (mm.s-1)')
#plt.ylabel('probability distribution of speed')
#plt.legend()
#plt.title('Speed distribution')
#plt.axis([-2, 2, 0, 1])
#
###--------------------------------------------------------------------------
###                       Fourier Transform
###--------------------------------------------------------------------------
#
#
#
#
#def Fourier(y,t):
#    n = len(t) # length of the signal
#    Fs=n/(t[-1]-t[0])
#    print(Fs)
#    
#    k = np.arange(n)
#    T = n/Fs
#    frq = k/T # two sides frequency range
#    frq = frq[range(int(n/2))] # one side frequency range
#    
#    Y = np.fft.fft(y)/n # fft computing and normalization
#    Y = Y[range(int(n/2))]
#    
#    fig, ax = plt.subplots(2, 1)
#    ax[0].plot(t,y)
#    ax[0].set_xlabel('Time')
#    ax[0].set_ylabel('Amplitude')
#    ax[1].plot(frq,abs(Y),'r') # plotting the spectrum
#    ax[1].set_xlabel('Freq (Hz)')
#    ax[1].set_ylabel('|A(freq)|')
#    #plt.axis([0, Fs,0,100])
#
#Fourier(X,T)
#Fourier(Y,T)
#Fourier(Z,T)
#
##Fs1 = 150  # sampling rate
##Ts1 = 1/Fs1 # sampling interval
##t = np.arange(0,1,Ts1) # time vector
##ff = 5;   # frequency of the signal
##y = np.sin(2*np.pi*ff*t)
##Fourier(y,t)
#
#
#
#
