# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 14:45:49 2018
Mean-Squared-Displacement Analyzer for multiple tracks
@author: deepak90
"""
import numpy as np
import Track
import os
import imp
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
from cycler import cycler

imp.reload(Track)

def squaredDisp(data):
    
    return (data - data[0])**2

def errorfill(x, y, yerr, color=None, alpha_fill=0.3, ax=None, label = None):
    ax = ax if ax is not None else plt.gca()
    if color is None:
        color = 'k'
#        color = ax._get_lines.color_cycle.next()
    if np.isscalar(yerr) or len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = yerr
    ax.plot(x, y, color=color, label = label)
    ax.fill_between(x, ymax, ymin, color=color, alpha=alpha_fill)

class msdanalyzer:
    
    def __init__(self, Tracks = None, nDims = 3, testFlag = 0):
        # Tracks is a list of gravity machine tracks
        self.precision = 12
        self.nDims = 3
        if(testFlag == 1 or Tracks is None):
            self.maxDelay = 5
            self.timeWindow = 1
            # Length of the delays window over which we calculate MSD
            self.tLen = 100
            self.genTestTraj()
            
        else:
            self.Tracks = Tracks
            self.nTracks = len(Tracks)
             # Maximum delay over which we want to calculate correlations
            self.maxDelay = 50
            self.timeWindow = 5
            self.getMinDiff()
            self.getCommonDelays()
       
        
    def genTestTraj(self):
        
        Tracks = []
        
        self.nTracks = 100
        
        boxSize = 2
        
        timeSteps = 1000
        DiffCoeff = 1e-3
        dT = 0.05
        
        k = (DiffCoeff*dT)**(1/2)
        
        TimeArray = np.array(range(0,timeSteps))*dT
        
        for ii in range(self.nTracks):
            
            
            X0 = boxSize*np.random.rand(self.nDims)
            dX = k*np.random.randn(self.nDims,timeSteps)
            
            dX[:,0] = X0;
            
            X = np.cumsum(dX,1)
            
            Tracks.append(Track.GravMachineTrack())
            Tracks[ii].T = TimeArray
            Tracks[ii].X = X[0,:]
            Tracks[ii].Y = X[1,:]
            Tracks[ii].Z = X[2,:]
            
        
        self.Tracks = Tracks
        
        self.delaysCommon = np.linspace(0,self.maxDelay,self.tLen)
#        print(Tracks[0].T)
            
        
    def getMinDiff(self):
        
        
        minDiff = 10
        maxDiff = 0
        for ii in range(self.nTracks):
            TimeArray = self.Tracks[ii].T
#            time = np.hstack((time, TimeArray))
            
            diff = np.diff(TimeArray)
#            print('Track {}, Time Array : {}'.format(ii,TimeArray))
            
            minDiff = min(np.min(diff), minDiff)
            maxDiff = max(np.max(diff), maxDiff)
           
        
#        time = np.unique(time)
        
#        print(np.shape(time))
        
#        time = np.round(time, decimals = self.precision)
        
#        self.time = time
        self.minDiff = minDiff
        self.maxDiff = maxDiff
        
#        print(self.minDiff)
#        print(self.maxDiff)
        
    def getCommonDelays(self):
        # This generates a common time array so many different tracks with different sampling rates can be avearaged
        
        self.tLen = int(self.maxDelay/float(self.minDiff))
        self.delaysCommon = np.linspace(0,self.maxDelay,self.tLen)
        self.delayIndex = np.array(range(0,len(self.delaysCommon)))
        
    def DispAtCommonTimes(self):
        
        Disp_X = []
        Disp_Y = []
        Disp_Z = []
        
       
        maxTrackLen = 0
        
        for ii in range(self.nTracks):


            currTrack = self.Tracks[ii]
            
            TimeArray = np.arange(0,currTrack.T[-1],self.minDiff)
            
            print('...Analyzing Track {} of Duration {} s'.format(ii, np.max(currTrack.T)))
            TimeArray = currTrack.T
            
            func_X = interpolate.interp1d(currTrack.T,currTrack.X, kind = 'linear')
            func_Y = interpolate.interp1d(currTrack.T,currTrack.Y,kind = 'linear')
            func_Z = interpolate.interp1d(currTrack.T,currTrack.Z,kind = 'linear')
            
            Disp_X.append(func_X(TimeArray))
            Disp_Y.append(func_Y(TimeArray))
            Disp_Z.append(func_Z(TimeArray))
            
            maxTrackLen = max(maxTrackLen, len(TimeArray))
            
        return maxTrackLen, Disp_X, Disp_Y, Disp_Z
    
    
    def computeMeanDisp(self):
        maxTrackLen, Disp_X, Disp_Y, Disp_Z = self.DispAtCommonTimes()
        
        nSubTracks = len(Disp_X)
        
        print('Total number of subtracks : {}'.format(nSubTracks))
        
        Disp_matrix_X = np.zeros((nSubTracks,maxTrackLen))
        Disp_matrix_Y = np.zeros((nSubTracks,maxTrackLen))
        Disp_matrix_Z = np.zeros((nSubTracks,maxTrackLen))
        
#        print(np.shape(MSD_matrix_X))
        
       
        for ii in range(nSubTracks):
            
#            print(np.shape(SquaredDisp_X[ii]))
            Disp_matrix_X[ii,:len(Disp_X[ii])] =  Disp_X[ii]
            Disp_matrix_Y[ii,:len(Disp_Y[ii])] =  Disp_Y[ii]
            Disp_matrix_Z[ii,:len(Disp_Z[ii])] =  Disp_Z[ii]
            
        
        Weights = np.sum(Disp_matrix_X!=0, axis = 0)
            
        Disp_matrix_X[Disp_matrix_X==0] = np.nan
        Disp_matrix_Y[Disp_matrix_Y==0] = np.nan
        Disp_matrix_Z[Disp_matrix_Z==0] = np.nan
        
        
        
        
        
        
        self.meanDisp_X = np.nanmean(Disp_matrix_X,axis = 0)
        self.meanDisp_Y = np.nanmean(Disp_matrix_Y,axis = 0)
        self.meanDisp_Z = np.nanmean(Disp_matrix_Z,axis = 0)
        
        self.meanDisp_XY = np.nanmean(Disp_matrix_X + Disp_matrix_Y, axis = 0)
        
        self.stdDisp_X = np.nanstd(Disp_matrix_X,axis = 0)
        self.stdDisp_Y = np.nanstd(Disp_matrix_Y,axis = 0)
        self.stdDisp_Z = np.nanstd(Disp_matrix_Z,axis = 0)
        
        self.stdDisp_XY = np.nanstd(Disp_matrix_X + Disp_matrix_Y, axis = 0)
        
    
    def computeSqDisp(self):
        
        
        SquaredDisp_X = []
        SquaredDisp_Y = []
        SquaredDisp_Z = []
        
        
        for ii in range(self.nTracks):
            
            
            currTrack = self.Tracks[ii]
        
            print('...Analyzing Track {} of Duration {} s'.format(ii, np.max(currTrack.T)))
            TimeArray = currTrack.T
            
            func_X = interpolate.interp1d(currTrack.T,currTrack.X, kind = 'linear')
            func_Y = interpolate.interp1d(currTrack.T,currTrack.Y,kind = 'linear')
            func_Z = interpolate.interp1d(currTrack.T,currTrack.Z,kind = 'linear')
            
            
            
            
            T_start = TimeArray[0]
            startIndex = 0
            counter = 0
            while (T_start < np.max(TimeArray)-self.maxDelay):
                
                T_subTrack = T_start + self.delaysCommon
                
                
                X_subTrack = func_X(T_subTrack)
                Y_subTrack = func_Y(T_subTrack)
                Z_subTrack = func_Z(T_subTrack)
                
                startIndex += next((i for i,x in enumerate(TimeArray[startIndex:] - TimeArray[startIndex]) if x >= self.timeWindow), None)

                
                T_start = TimeArray[startIndex]
                
                
                
                SquaredDisp_X.append(squaredDisp(X_subTrack))
                SquaredDisp_Y.append(squaredDisp(Y_subTrack))
                SquaredDisp_Z.append(squaredDisp(Z_subTrack))
                
                counter += 1
                
            print('no:of Subtracks from Track {}: {}'.format(ii, counter))
        
        return SquaredDisp_X, SquaredDisp_Y, SquaredDisp_Z
    
    
    def computeMSD(self):
        
        SquaredDisp_X, SquaredDisp_Y, SquaredDisp_Z = self.computeSqDisp()
        
        
        nSubTracks = len(SquaredDisp_X)
        
        print('Total number of subtracks : {}'.format(nSubTracks))
        
        MSD_matrix_X = np.zeros((nSubTracks,self.tLen))
        MSD_matrix_Y = np.zeros((nSubTracks,self.tLen))
        MSD_matrix_Z = np.zeros((nSubTracks,self.tLen))
        
#        print(np.shape(MSD_matrix_X))
        
       
        for ii in range(nSubTracks):
            
#            print(np.shape(SquaredDisp_X[ii]))
            MSD_matrix_X[ii,:len(SquaredDisp_X[ii])] =  SquaredDisp_X[ii]
            MSD_matrix_Y[ii,:len(SquaredDisp_Y[ii])] =  SquaredDisp_Y[ii]
            MSD_matrix_Z[ii,:len(SquaredDisp_Z[ii])] =  SquaredDisp_Z[ii]
            
#        subTracks = np.array(range(nSubTracks))
        
#        print(len(subTracks))
#        print(len(self.delaysCommon))
#        print(np.shape(MSD_matrix_X))
#        plt.figure(4)
#        ax = plt.contourf(self.delaysCommon,subTracks,MSD_matrix_X==0)
#        plt.colorbar(ax)
#        plt.axis('image')
#        plt.show()
            
        Weights = np.sum(MSD_matrix_X!=0, axis = 0)
        
        
#        plt.figure(4)
#        plt.plot(self.delaysCommon, Weights, color = 'r')
#        plt.show()
#        
#        print(np.shape(Weights))
#        print(np.shape(MSD_matrix_X))
        
        MSD_matrix_X[MSD_matrix_X==0] = np.nan
        MSD_matrix_Y[MSD_matrix_Y==0] = np.nan
        MSD_matrix_Z[MSD_matrix_Z==0] = np.nan
        
        
        
        
        
        
        self.MSD_X = np.nanmean(MSD_matrix_X,axis = 0)
        self.MSD_Y = np.nanmean(MSD_matrix_Y,axis = 0)
        self.MSD_Z = np.nanmean(MSD_matrix_Z,axis = 0)
        
        self.MSD_XY = np.nanmean(MSD_matrix_X + MSD_matrix_Y, axis = 0)
        
        self.stdev_X = np.nanstd(MSD_matrix_X,axis = 0)
        self.stdev_Y = np.nanstd(MSD_matrix_Y,axis = 0)
        self.stdev_Z = np.nanstd(MSD_matrix_Z,axis = 0)
        
        self.stdev_XY = np.nanstd(MSD_matrix_X + MSD_matrix_Y, axis = 0)
        
        
            
            
        
                
#------------------------------------------------------------------------------
        # Plotting functions
#------------------------------------------------------------------------------
    def plotMSD(self, figname = 1, saveFolder = None, orgName = None):
        
        
#        f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
        
        plt.figure(1, figsize = (8,6))
        ax1 = plt.gca()
        errorfill(self.delaysCommon, self.MSD_XY, self.stdev_XY, ax = ax1, color = 'r', label = 'Horizontal (XY)')

        ax3 = plt.gca()
        
        errorfill(self.delaysCommon, self.MSD_Z, self.stdev_Z, ax = ax3, color = 'b', label = 'Vertical (Z)')
#        
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('MSD')
        plt.xlim(0,np.max(self.delaysCommon))
        plt.legend(loc='upper left')
        if(saveFolder is not None and orgName is not None):
            plt.savefig(os.path.join(saveFolder,orgName+'_MSD_Linear.svg'),bbox_inches='tight',dpi=150)

        plt.show()
        
        
        # 
        time = np.linspace(10,100,100)
        A = 1
        B=0.01
        X_linear = B*time
        X_quad = A*(time**2)
        
        
        plt.figure(2, figsize = (4,3))
        ax1 = plt.gca()
        ax1.plot(self.delaysCommon, self.MSD_XY, color = 'r', label = 'Horizontal (XY)')
        ax1.set_yscale('log')
        ax1.set_xscale('log')
        
        ax3 = plt.gca()
        
        ax3.plot(self.delaysCommon, self.MSD_Z, color = 'b', label = 'Vertical')#        ax3.set_yscale('log')
        ax3.plot(time,X_linear,'k-')
        ax3.plot(time,X_quad, 'k--')
        ax3.set_yscale('log')
        ax3.set_xscale('log')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('MSD')
        
        plt.xlim(0,np.max(self.delaysCommon))
#        plt.legend(loc='upper left')
        if(saveFolder is not None and orgName is not None):

            plt.savefig(os.path.join(saveFolder,orgName+'_MSD_Log.svg'),bbox_inches='tight',dpi=150)

        plt.show()
        
        
        
        
  
        
        
        

def main():
    
  
    #--------------------------------------------------------------------------
    # Dendraster
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood'
#    TrackNames = {0:['Dendraster1',87,417], 1:['Dendraster2',0,0], 2:['Dendraster3',0,0]}     
        
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_withfood'
#    TrackNames = {0:['Dendraster1',87,417], 1:['Dendraster2',0,0], 0:['Dendraster3',0,0]}     

#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_well_fed_11Days_nofood'
#    TrackNames = {0:['Dendraster1',0,600], 1:['Dendraster2',0,200], 2:['Dendraster3',0,0]}     

    #--------------------------------------------------------------------------
    # Sea cucumber
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber'
    
#    TrackNames = {0:['seacucmber4_auto_verylong_goodtrack', 0,0], 1:['seacucmber9_Auto', 0,0]}
    
#    TrackNames = {0:['seacucmber4_auto_verylong_goodtrack', 0,0]}
    
    
    #--------------------------------------------------------------------------
    # Sea Urchin
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin'

#    TrackNames = {0: ['SeaUrchin5',0,0],1: ['SeaUrchin7',0,500],2: ['SeaUrchin8',0,0]}

    #--------------------------------------------------------------------------
    # Acorn Worm
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight'
#    TrackNames = {0: ['AcornWorm2',0,0],1: ['AcornWorm3',0,0],2: ['AcornWorm4',0,0],3: ['AcornWorm7',0,0]}
#    --------------------------------------------------------------------------
    # Brittle Star
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar'
    
#    TrackNames = {0:['BrittleStar1',0,0],1:['BrittleStar9_Long_Good_Ytracking',0,0],2:['BrittleStar10_Ytracking_Good',0,0],3:['BrittleStar12_Ytracking_Good',0,0]}
    #--------------------------------------------------------------------------
    # Snail
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail'
    
#    TrackNames = {0:['snail1',0,575],1:['snail2',0,0],2:['snail4',0,0],3:['snail6',0,0],4:['snail8',0,0],5:['snail10',0,0],6:['snail13',0,0]}
    #--------------------------------------------------------------------------
    # Starfish
    #--------------------------------------------------------------------------
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish'
#    TrackNames = {0:['StarFish1', 0,162],1:['StarFish6', 0,600],2:['StarFish7', 60,0],3:['StarFish9', 0,290]}

    
    # Polychaete
    
    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D'
    TrackNames = {0:['Polychaete1',0,112],1:['Polychaete2',0,113], 2:['Polychaete3',0,37], 3:['Polychaete4',0,55], 4:['Polychaete6',0,113]}

    
    
#    dataFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca'
#    
#    TrackNames = {0:['Noctilica6',50,0],1:['Noctilica7',0,1000]}
#    
    TrackFile = 'track_mod.csv'
    
    *rest,orgName = os.path.split(dataFolder)
    saveFolder = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/EnsembleTrackStatistics'
    
    
    
    
    TrackArray = []
    
    for ii, currFolder in TrackNames.items():
        path = os.path.join(dataFolder, TrackNames[ii][0])
        
        TrackArray.append(Track.GravMachineTrack(path, TrackFile, TrackNames[ii][1],TrackNames[ii][2]))

    
    
    msd1 = msdanalyzer(TrackArray)
    
    
#    msd1 = msdanalyzer(testFlag=0)
    
    msd1.computeMSD()
    
    msd1.plotMSD(figname = 1, saveFolder = saveFolder,orgName = orgName)
    
    
    
    
    
    
if __name__ == '__main__':
    main()    
        

        
        
