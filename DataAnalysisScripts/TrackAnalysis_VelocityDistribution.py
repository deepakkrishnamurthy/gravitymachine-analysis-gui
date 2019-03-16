#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 21:37:43 2018
Track analysis for gravity machine
1. Calculates Velocity distributions of an ensemble of tracks
@author: deepak
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
import scipy.ndimage as ndimage
import smoothn
from roipoly import roipoly
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from matplotlib.lines import Line2D
import pickle
plt.close("all")
from PIL import Image
import imp
import Track
imp.reload(Track)
import numpy as np
import csv_tool as csv
import pandas as pd
import seaborn as sns
import matplotlib.colors as Colors

#==============================================================================
#                              Plot Parameters and Functions 
#==============================================================================
from matplotlib import rcParams
from matplotlib import rc
#rcParams['axes.titlepad'] = 20 
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
### for Palatino and other serif fonts use:
##rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=False)
#plt.rc('font', family='serif')

rc('font', family='sans-serif') 
rc('font', serif='Helvetica') 
rc('text', usetex='false') 
rcParams.update({'font.size': 22})

def squared_displacement(data,i,n):
    # n is the track len over which an ensemble is calculated
    return (data[i:i+n]-data[i])**2

def squared_vector_3d(X,Y,Z,i,n):
    
    return (X[i:i+n] - X[i])**2 + (Y[i:i+n] - Y[i])**2 + (Z[i:i+n] - Z[i])**2 



    

#def main():
    
    
#------------------------------------------------------------------------------
# Data convention:
#------------------------------------------------------------------------------
# 1. Each track is an element of a Dictionary
# 2. A set of tracks are grouped according to a condition    
# 2. Comparison across multiple datasets is done by joining together different dictionaries as a list
    

rootFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/'

#    subFolders = {0:'Dendraster_starved_11Days_nofood',1:'Dendraster_starved_11Days_withfood',2:'Dendraster_well_fed_11Days_nofood'}

Conditions = ['No light']
#Conditions = ['Day','Night']


OrganismNames = ['SeaCucumber','Dendraster','BrittleStar','AcornWorm','SeaUrchin','Starfish','Snail','Polychaete','Noctiluca','Volvox','Pyrocystis']

dataFolder = {}
TrackNames = {} 
#--------------------------------------------------------------------------
# Starfish
#--------------------------------------------------------------------------
dataFolder['Starfish'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'
TrackNames['Starfish'] = {0:['StarFish1', 0,162],1:['StarFish6', 0,600],2:['StarFish7', 60,0],3:['StarFish9', 0,290]}
#--------------------------------------------------------------------------
# Dendraster
#--------------------------------------------------------------------------
dataFolder['Dendraster'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood'
TrackNames['Dendraster'] = {0:['Dendraster1', 87,417], 1:['Dendraster2', 0,0], 2:['Dendraster3', 0,0]}

#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_withfood'

#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_well_fed_11Days_nofood'

#--------------------------------------------------------------------------
# Sea cucumber
#--------------------------------------------------------------------------
dataFolder['SeaCucumber'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber'
TrackNames['SeaCucumber']  = {0:['seacucmber4_auto_verylong_goodtrack', 0,0], 1:['seacucmber9_Auto', 0,0]}

#    TrackNames = {0:['seacucmber4_auto_verylong_goodtrack', 0,0]}


#--------------------------------------------------------------------------
# Sea Urchin
#--------------------------------------------------------------------------
dataFolder['SeaUrchin'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin'

TrackNames['SeaUrchin'] = {0: ['SeaUrchin5',0,0],1: ['SeaUrchin7',0,500],2: ['SeaUrchin8',0,0]}

#--------------------------------------------------------------------------
# Acorn Worm
#--------------------------------------------------------------------------
dataFolder['AcornWorm'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight'
TrackNames['AcornWorm'] = {0: ['AcornWorm2',0,0],1: ['AcornWorm3',0,0],2: ['AcornWorm4',0,0],3: ['AcornWorm7',50,140]}
#    --------------------------------------------------------------------------
# Brittle Star
#--------------------------------------------------------------------------
dataFolder['BrittleStar'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar'
TrackNames['BrittleStar'] = {0:['BrittleStar9_Long_Good_Ytracking',0,0],1:['BrittleStar1',0,0],2:['BrittleStar10_Ytracking_Good',0,0],3:['BrittleStar12_Ytracking_Good',0,0]}
#--------------------------------------------------------------------------
# Snail
#--------------------------------------------------------------------------
dataFolder['Snail'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail'
TrackNames['Snail'] = {0:['snail1',0,575],1:['snail2',0,0],2:['snail4',0,0],3:['snail6',0,0],4:['snail8',0,0],5:['snail10',0,0],6:['snail13',0,0]}
#--------------------------------------------------------------------------
# Noctilica
#--------------------------------------------------------------------------
dataFolder['Noctiluca'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca'
TrackNames['Noctiluca'] = {0:['Noctilica6',50,0],1:['Noctilica7',0,1000]}
#--------------------------------------------------------------------------
# Polychaetes
#--------------------------------------------------------------------------
dataFolder['Polychaete'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D'
TrackNames['Polychaete'] = {0:['Polychaete1',0,112],1:['Polychaete2',0,113], 2:['Polychaete3',0,37], 3:['Polychaete4',0,55], 4:['Polychaete6',0,113]}

dataFolder['Polychaete_night'] = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Polychaete'
TrackNames['Polychaete_night'] = {0:['Poly1',20,80],1:['Poly2',0,116], 2:['Poly3',0,0], 3:['Poly4',0,93], 4:['Poly5',0,34]}
#--------------------------------------------------------------------------
# Volvox
#--------------------------------------------------------------------------
dataFolder['Volvox'] ='/Volumes/GRAVMACH1/GravityMachine/ControlExperiments/VolvoxControls_GravityMachine_2018_10_28'
TrackNames['Volvox'] = {0:['Volvox10_1',0,0], 1:['Volvox2', 0, 130],2:['Volvox4', 100, 330 ], 3:['Volvox8', 0, 65],4:['Volvox1', 0,40],5:['Volvox13', 0,0],6:['Volvox20_phototaxis',40,70],7:['Volvox22', 0,16],8:['Volvox23', 0, 64]}
#--------------------------------------------------------------------------
# Pyrocystis
#--------------------------------------------------------------------------
dataFolder['Pyrocystis'] = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21'
TrackNames['Pyrocystis'] = {0:['nnn1',0,3600]}
#TrackNames = [{0:['Polychaete1',0,112],1:['Polychaete2',0,113], 2:['Polychaete3',0,37], 3:['Polychaete4',0,55], 4:['Polychaete6',0,113]},{0:['Poly1',20,80],1:['Poly2',0,116], 2:['Poly3',0,0], 3:['Poly4',0,93], 4:['Poly5',0,34]}]
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Polychaete'
#TrackNames2 = {}

#    *rest,orgName = os.path.split(dataFolder)
#    saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'

# Load the set of tracks we want to analyze
#    TrackNames = {0:['Dendraster1', 87,417],1:['Dendraster2', 0,0],2:['Dendraster3',0,0]}

#    TrackNames = {0:['Dendraster1', 0,600],1:['Dendraster2', 0,200],2:['Dendraster3',0,0]}
#    TrackNames = {0:['StarFish1', 0,162],1:['StarFish6', 0,600],2:['StarFish7', 60,0],3:['StarFish9', 0,290]}


TrackFile = 'track_mod.csv'


Velocities_X = np.array([])
Velocities_Y = np.array([])
Velocities_Z = np.array([])

Velocities_X_notWall = np.array([])
Velocities_Y_notWall = np.array([])
Velocities_Z_notWall = np.array([])

dataFrame_noWalls = pd.DataFrame({'Organism':[],'OrgSize':[],'TrackName':[],'Condition':[],'VelocityX_noWall':[],'VelocityY_noWall':[],'VelocityZ_noWall':[]})
dataFrame_full = pd.DataFrame({'Organism':[],'OrgSize':[],'TrackName':[],'Condition':[],'VelocityX':[],'VelocityY':[],'VelocityZ':[]})

totalTrackLen = 0

TrackArray = []

saveFile_noWalls = 'Organism_Velocities_Collected_noWalls.csv'
saveFile_full = 'Organism_Velocities_Collected_full.csv'

save_root = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'

save_path_noWalls = os.path.join(save_root, saveFile_noWalls)

save_path_full = os.path.join(save_root, saveFile_full)

overwrite = False

if(not os.path.exists(save_path_noWalls) or not os.path.exists(save_path_full) or overwrite):




    for Organism, Tracks in TrackNames.items():
                    
        print('Current organism : {}'.format(Organism))
        
        for ii, currTrack in Tracks.items():
            print(currTrack)
            path = os.path.join(dataFolder[Organism], currTrack[0])
            # Load the track into memory
            Track_curr = Track.GravMachineTrack(path, TrackFile, currTrack[1],currTrack[2])
            
            
    #        plt.figure()
    #        plt.plot(Track_curr.Time,Track_curr.ZobjWheel,'bo-')
    #        plt.plot(Track_curr.T,Track_curr.Z,'r-')
    #        plt.show()
    
            
            
    #        Track_curr.plotTrackWalls(walls=1)
    #        Track_curr.plotVelocity(Track_curr.Vx,Track_curr.Vy,Track_curr.Vz)
    #        Track_curr.plot3DComponents(Track_curr.X_smooth,Track_curr.Y_smooth,Track_curr.Z_smooth, walls = 1)
            Track_curr.T = Track_curr.T - Track_curr.T[0]
            Track_curr.Z = Track_curr.Z - Track_curr.Z[0]
            
            
    #            plt.plot(Track_curr.T, Track_curr.Z, linewidth = 2, linestyle = linestyle, color = plt_colors[ii])
    #            plt.fill_between(Track_curr.T,Track_curr.Z,color = plt_colors[ii],alpha=0.2)
            
            AutoTracking = np.array(~Track_curr.ManualTracking[:-1], dtype= 'bool')
            #--------------------------------------------------------------------------
            # Velocity distributions
            #--------------------------------------------------------------------------
    #        Velocities_X = np.hstack((Velocities_X,np.array(Track_curr.Vx[AutoTracking])))
    #        Velocities_Y = np.hstack((Velocities_Y,np.array(Track_curr.Vy[AutoTracking])))
    #        Velocities_Z = np.hstack((Velocities_Z,np.array(Track_curr.Vz[AutoTracking])))
            
    #            Velocities_X_dict[kk] = np.hstack(Velocities_X_dict[kk], np.array(Track_curr.Vx[AutoTracking]))
    #            Velocities_Z_dict[kk] = np.hstack(Velocities_Z_dict[kk], np.array(Track_curr.Vz[AutoTracking]))
    
    #        Velocities_X_notWall = np.hstack((Velocities_X_notWall,np.array(Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking])))
    #        Velocities_Y_notWall = np.hstack((Velocities_Y_notWall,np.array(Track_curr.Vy[~Track_curr.atWall[:-1]&AutoTracking])))
    #        Velocities_Z_notWall = np.hstack((Velocities_Z_notWall,np.array(Track_curr.Vz[~Track_curr.atWall[:-1]&AutoTracking])))
            #--------------------------------------------------------------------------
            #--------------------------------------------------------------------------
            # We only save velocities when the tracking is automated
            #--------------------------------------------------------------------------
            Vx = Track_curr.Vx[AutoTracking]
            Vy = Track_curr.Vx[AutoTracking]
            Vz = Track_curr.Vz[AutoTracking]
            #--------------------------------------------------------------------------
            # We only save velocities when the tracking is automated and far from walls
            #--------------------------------------------------------------------------
            Vx_noWalls = Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking]
            Vy_noWalls = Track_curr.Vy[~Track_curr.atWall[:-1]&AutoTracking]
            Vz_noWalls = Track_curr.Vz[~Track_curr.atWall[:-1]&AutoTracking]
    
            
            # Save the Ensemble velocity distributions in a CSV file for future use
            dataLen = len(Vx)
            dataLen_noWalls = len(Vx_noWalls)
            
                
    #        dataFrame_noWalls = dataFrame_noWalls.append(pd.DataFrame({'Organism':np.repeat(['Polychaete'],len(Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking]),axis = 0),'Condition': np.repeat(condition, len(Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking]),axis = 0),'VelocityX_noWall':Track_curr.Vx[~Track_curr.atWall[:-1]&AutoTracking],'VelocityY_noWall':Track_curr.Vy[~Track_curr.atWall[:-1]&AutoTracking],'VelocityZ_noWall':Track_curr.Vz[~Track_curr.atWall[:-1]&AutoTracking]}))
            dataFrame_full = dataFrame_full.append(pd.DataFrame({'Organism':np.repeat(Organism,dataLen,axis = 0),'OrgSize': np.repeat(Track_curr.OrgDim,dataLen,axis = 0),'TrackName':np.repeat(currTrack[0],dataLen,axis=0),'Condition':np.repeat(Conditions,dataLen,axis=0),'VelocityX':Vx,'VelocityY':Vy,'VelocityZ':Vz}))

            dataFrame_noWalls = dataFrame_noWalls.append(pd.DataFrame({'Organism':np.repeat(Organism,dataLen_noWalls,axis = 0),'OrgSize': np.repeat(Track_curr.OrgDim,dataLen_noWalls,axis = 0),'TrackName':np.repeat(currTrack[0],dataLen_noWalls,axis=0),'Condition':np.repeat(Conditions,dataLen_noWalls,axis=0),'VelocityX_noWall':Vx_noWalls,'VelocityY_noWall':Vy_noWalls,'VelocityZ_noWall':Vz_noWalls}))
            
    
        
    #        totalTrackLen += (max(Track_curr.Time) - min(Track_curr.Time))
    
    # Save the dataFrame as a CSV file
    dataFrame_noWalls.to_csv(save_path_noWalls)
    dataFrame_full.to_csv(save_path_full)

    
else:
    
    dataFrame_noWalls = pd.read_csv(save_path_noWalls)
    dataFrame_full = pd.read_csv(save_path_full)
#--------------------------------------------------------------------------
# PLOTS
#--------------------------------------------------------------------------
Organism1 = 'Snail'
#Organism2 = 'Star Diatom'

#saveSubFolder = os.path.join(save_root, Organism)
#
#if(not os.path.exists(saveSubFolder)):
#    os.makedirs(saveSubFolder)

my_pal = {'VelocityZ_noWall': 'b' ,'VelocityX_noWall': 'r'}
color_list = sns.color_palette("RdBu_r", 7)
#my_pal = {'VelocityZ_noWall': color_list[0] ,'VelocityX_noWall': color_list[6]}

xlim1 = -2
xlim2 = 2
decimals = 1
##--------------------------------------------------------------------------
## Distplot of the velocity distributions
##--------------------------------------------------------------------------
#plt.figure(figsize=(4.5,4))
#ax0 = sns.distplot(dataFrame_noWalls.loc[dataFrame_noWalls["Organism"] == Organism,"VelocityZ_noWall"],  kde = True , color = my_pal["VelocityZ_noWall"], norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})
#ax1 = sns.distplot(dataFrame_noWalls.loc[dataFrame_noWalls["Organism"] == Organism,"VelocityX_noWall"],  kde = True , color = my_pal["VelocityX_noWall"], norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vx'})  
#
#
#        
#
#plt.xlim([xlim1, xlim2])
#plt.xticks(np.round(np.linspace(xlim1,xlim2,5), decimals=decimals))
#plt.title(Organism)
##plt.savefig(os.path.join(saveSubFolder,Organism+'VelocityDistribution_FINAL.svg'))
#plt.show()
#
#
##--------------------------------------------------------------------------
## Boxplot of the mean velocity
##--------------------------------------------------------------------------
#df = dataFrame_noWalls.loc[dataFrame_noWalls["Organism"]==Organism,["VelocityX_noWall", "VelocityZ_noWall"]]
#
#plt.figure(figsize=(4.5,4))
#ax0 = sns.boxplot(x = "variable",y = "value",data = df.melt(), width = 0.2, palette=my_pal,boxprops=dict(alpha=0.5),showfliers=False)
#plt.title(Organism)
##plt.savefig(os.path.join(saveSubFolder,Organism+'Vx_BoxPlot_FINAL.svg'))
#plt.show()

##--------------------------------------------------------------------------
## Distplot of the velocity distributions for Full velocity
##--------------------------------------------------------------------------
plt.figure(figsize=(4.5,4))
ax0 = sns.distplot(dataFrame_full.loc[dataFrame_full["Organism"] == Organism1,"VelocityZ"],  kde = True , color = 'b', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})
#ax0 = sns.distplot(dataFrame_full.loc[dataFrame_full["Organism"] == Organism2,"VelocityZ"],  kde = True , color = 'k', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})

ax1 = sns.distplot(dataFrame_full.loc[dataFrame_full["Organism"] == Organism1,"VelocityX"],  kde = True , color = 'r', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vx'})  

plt.xlim([xlim1, xlim2])
plt.xticks(np.round(np.linspace(xlim1,xlim2,5), decimals=decimals))
#plt.savefig(os.path.join(saveSubFolder,Organism+'VelocityDistribution_FINAL.svg'))
plt.show()

my_pal = {'VelocityZ': 'b' ,'VelocityX': 'r'}
#
##--------------------------------------------------------------------------
## Boxplot of the mean velocity
##--------------------------------------------------------------------------
#df = dataFrame_full.loc[dataFrame_full["Organism"]==Organism,["VelocityX", "VelocityZ"]]
#
#plt.figure(figsize=(4.5,4))
#ax0 = sns.boxplot(x = "variable",y = "value",data = df.melt(), width = 0.2, palette=my_pal,boxprops=dict(alpha=0.5),showfliers=False)
#plt.title(Organism)
##plt.savefig(os.path.join(saveSubFolder,Organism+'Vx_BoxPlot_FINAL.svg'))
#plt.show()


# Plot the organism sizes

#plt.figure()
#ax = sns.scatterplot(x = "Organism", y = "OrgSize", data = dataFrame_noWalls)
#plt.title('Sizes of organisms')
#plt.show()


# Now plot the velocity distribution from the dataframe
#custom_line = [Line2D([0], [0], color='gold', lw=4, alpha = 0.5), Line2D([0], [0], color='k', lw=4, alpha = 0.5) ]
#
#
#
#my_pal = {'Day': 'darkorange'a ,'Night': 'midnightblue'}
#plt.figure()
#
## Day
##ax2 = sns.distplot(dataFrame["VelocityX_noWall"],  kde = True , color = 'r', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5})
#
#ax3 = sns.distplot(dataFrame.loc[dataFrame["Condition"] == 'Night',"VelocityZ_noWall"],  kde = True , color = 'midnightblue', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Night'})
#ax4 = sns.distplot(dataFrame.loc[dataFrame["Condition"] == 'Day',"VelocityZ_noWall"],  kde = True , color = 'darkorange', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Day'})
##plt.legend((ax3, ax4))
##plt.legend(custom_line, ['Day', 'Night'])
#
#
#plt.show()
#
#
#
#plt.figure()
#
#ax = sns.boxplot(x = "Condition", y = "VelocityZ_noWall",data = dataFrame, width = 0.3, palette= my_pal,boxprops=dict(alpha=0.5))
#ax1 = sns.swarmplot(x = "Condition", y = "VelocityZ_noWall",data = dataFrame, color=".25")
#plt.show()

    
 
    



#    print(TrackArray[0].Time)
#    print(len(TrackNames))
#    # Save some useful data so it can be easily read back
#    saveFile = orgName+'_TrackStatistics.csv'
#    csv_register = csv.CSV_Register(header=[['nTracks', 'Total Track Time','Mean Velocity Z','Std Velocity Z','Mean Velocity X','Std Velocity X']])
#    csv_register.file_directory = os.path.join(saveFolder, saveFile)
#    csv_register.start_write()
#    data = [len(TrackNames), totalTrackLen, np.nanmean(Velocities_Z_notWall), np.nanstd(Velocities_Z_notWall), np.nanmean(Velocities_X_notWall),np.nanstd(Velocities_X_notWall)] 
#    csv_register.write_line([data])
#    csv_register.close()


   





#    print(np.shape(Velocities_X))



#    fig = plt.figure()
#    
#    
#    plt.subplot(131)
#    nX, binsX, patches = plt.hist(Velocities_X, bins = 'auto', facecolor = 'r')
#    plt.xlabel('X Velocity (mm/s)')
#    plt.ylabel('Probability')
#    plt.subplot(132)
#    nY, binsY, patches = plt.hist(Velocities_Y, bins = 'auto', facecolor = 'g')
#    plt.xlabel('Y Velocity (mm/s)')
#    plt.ylabel('Probability')
#    plt.subplot(133)
#    nZ, binsZ, patches = plt.hist(Velocities_Z, bins = 'auto', facecolor = 'b')
#    plt.xlabel('Z Velocity (mm/s)')
#    plt.ylabel('Probability')
#    
#    plt.show()
#    
#    print(np.shape(Velocities_X))
#    print(np.shape(Velocities_Y))
#    print(np.shape(Velocities_Z))

#xlim_low = -2
#xlim_high = 2
#
#color_X = list(cm.bwr(0))
#color_Z = list(cm.bwr(255))
#
##    color_X[-1] = 0.7
#
#   
#
#fig = plt.figure(figsize=(5,8), dpi = 150)
#
#
#nX, binsX, patches = plt.hist(Velocities_X,bins = 'auto',range = (-4,4), density = True, facecolor = color_X,alpha = 0.9, stacked= True, label ='X')  
#nZ, binsZ, patches = plt.hist(Velocities_Z, bins = 'auto', range = (-4,4), density = True, facecolor = color_Z, alpha = 0.7, stacked = True, label ='Z')
#plt.xlabel('Velocity (mm/s)')
##    plt.ylabel('Probability density')
##    plt.title('Full track')
##    plt.axis('square')
#plt.ylim(0,max(np.max(nZ),np.max(nX))+0.1)
#plt.xlim(xlim_low,xlim_high)
#plt.legend()
##    plt.savefig(os.path.join(saveFolder,orgName+'_VelocityDistribution_Full.svg'))
#
#plt.show()
#
#fig = plt.figure(figsize=(5,8), dpi = 150)
#
#nX, binsX, patches = plt.hist(Velocities_X_notWall,bins = 'auto',range = (-4,4), density = True, facecolor = color_X, alpha = 0.9,stacked= True,label ='X')
#nZ, binsZ, patches = plt.hist(Velocities_Z_notWall, bins = 'auto', range = (-4,4), density = True, facecolor = color_Z, alpha = 0.7, stacked = True,label ='Z')
#plt.xlabel('Velocity (mm/s)')
##    plt.ylabel('Probability density')
##    plt.title('Track segments away from walls')
#plt.ylim(0,max(np.max(nZ),np.max(nX))+0.1)
#plt.xlim(xlim_low,xlim_high)
#plt.legend()
##    plt.savefig(os.path.join(saveFolder,orgName+'_VelocityDistribution_noWalls.svg'))
#plt.show()
    
  


    
   
    
    
    
#if __name__ == '__main__':
#    main()
    
