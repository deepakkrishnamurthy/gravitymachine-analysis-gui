#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 15:30:04 2018
Track class for gravity machine data
@author: deepak
"""
import csv as csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as markers
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
import math
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import cycler
import cv2
import rangeslider_functions
import seaborn as sns
plt.close("all")
font = cv2.FONT_HERSHEY_SIMPLEX


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
rcParams.update({'font.size': 16})

#============================================================================== 
def mmPerPixel(resolution_width):
    return 1./628/(resolution_width/1440)   #for a 1440x1080 image
def pixelPermm(resolution_width):
    return 628*resolution_width/1440
#==============================================================================
class GravMachineTrack:
    
   
    def __init__(self, path=None, file=None, Tmin = 0, Tmax = 0):
        
        
        # The case where the Path and File are specified and we can load an actual track
        if(path is not None and file is not None):
            self.channelWidth = 3        # Channel Width in mm
            self.channelLength = 15      # Channel Length in mm
            self.path = path
            self.imagePath = os.path.join(path,'images000')
#            self.imagePath = os.path.join(path,'images00000')
            self.imgFormat = '.svg'
            self.root, self.Organism = os.path.split(self.path)
            self.threshLow = [0,0,55]
            self.threshHigh = [255,255,255]
            # Max major dimension of the organism. Need to implement an automated way of detecting this from images and storing the value.
            # Starfish (in mm)
    #        self.maxOrgDim = 1.06
            # Dendraster
    #        self.maxOrgDim = 0.4
            
            # Seacucumber
            
            self.savePath = '/Users/deepak/Dropbox/GravityMachine/GravityMachineManuscript/OrganismPlots'
            dataFolder, self.TrackName = os.path.split(self.path)
            Data=[]
            try:
                reader = csv.reader(open(os.path.join(path,file),newline=''))
            except:
                print('Using trackname: track.csv')
                file = 'track.csv'
                reader = csv.reader(open(os.path.join(path,file),newline=''))

                
            for row in reader:
                Data.append(row)
                
            
            self.Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,len(Data))]) 
            
            if(Tmax==0):
                Tmax = np.max(self.Time)
                
            self.Tmin_index = next((i for i,x in enumerate(self.Time) if x >= Tmin), None)
            self.Tmax_index = next((i for i,x in enumerate(self.Time) if x >= Tmax), None)
          
            print(self.Tmin_index)
            print(self.Tmax_index)
            
    
            self.Time = self.Time[self.Tmin_index:self.Tmax_index]
            
            self.trackLen=len(self.Time)
            
            
            
            self.Tmin_index += 1
            self.Tmax_index += 1
            
            
            self.Xobj=np.array([float(Data[i][1]) for i in range(self.Tmin_index,self.Tmax_index)])             # Xpos in motor full-steps
            self.Yobj=np.array([float(Data[i][2]) for i in range(self.Tmin_index,self.Tmax_index)])             # Ypos in motor full-steps
            self.Zobj=np.array([float(Data[i][3]) for i in range(self.Tmin_index,self.Tmax_index)])             # Zpos is in encoder units
            self.ThetaWheel=np.array([float(Data[i][4]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.ZobjWheel=np.array([float(Data[i][5]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.ManualTracking=np.array([int(Data[i][6]) for i in range(self.Tmin_index,self.Tmax_index)], dtype = 'bool')   # 0 for auto, 1 for manual
            self.ImageName=np.array([Data[i][7] for i in range(self.Tmin_index,self.Tmax_index)])
            self.focusMeasure=np.array([float(Data[i][8]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.focusPhase=np.array([float(Data[i][9]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.liqLensFreq = np.array([float(Data[i][10]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.liqLensAmp = np.array([float(Data[i][11]) for i in range(self.Tmin_index,self.Tmax_index)])
            self.liqLensGain = np.array([float(Data[i][12]) for i in range(self.Tmin_index,self.Tmax_index)])
            
#            self.lightExperiment = np.array([float(Data[i][14]) for i in range(self.Tmin_index,self.Tmax_index)])
#            self.LED_intensity = np.array([float(Data[i][15]) for i in range(self.Tmin_index,self.Tmax_index)])

#            self.LED_R = np.array([float(Data[i][11]) for i in range(self.Tmin_index,self.Tmax_index)])	
#            self.LED_G = np.array([float(Data[i][12]) for i in range(self.Tmin_index,self.Tmax_index)])	
#            self.LED_B = np.array([float(Data[i][13]) for i in range(self.Tmin_index,self.Tmax_index)])
            
    
            
    #        self.Xobj=np.array([float(Data[i][1]) for i in range(1,self.trackLen)])             # Xpos in motor full-steps
    #        self.Yobj=np.array([float(Data[i][2]) for i in range(1,self.trackLen)])             # Ypos in motor full-steps
    #        self.Zobj=np.array([float(Data[i][3]) for i in range(1,self.trackLen)])             # Zpos is in encoder units
    #        self.ThetaWheel=np.array([float(Data[i][4]) for i in range(1,self.trackLen)])
    #        self.ZobjWheel=np.array([float(Data[i][5]) for i in range(1,self.trackLen)])
    #        self.ManualTracking=np.array([int(Data[i][6]) for i in range(1,self.trackLen)])   # 0 for auto, 1 for manual
    #        self.ImageName=np.array([Data[i][7] for i in range(1,self.trackLen)])
    #        self.focusMeasure=np.array([float(Data[i][8]) for i in range(1,self.trackLen)])
    #        self.focusPhase=np.array([float(Data[i][9]) for i in range(1,self.trackLen)])
    #        self.MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,self.trackLen)])
            
    #        if(Tmax != 0):
    #            self.cropTrack(Tmin, Tmax)
            
            # Only for Starfish 6 dataset
#            self.Yobj = self.removeOutliers(self.Yobj,334,355)
           
            
#            self.setAxesLimits()
#            
#            self.regularizeTrack()
#            
#            self.smoothTrack(self.window_time)
##    #        self.smoothTrack(1/self.samplingFreq)
##            
#            self.computeVelocity()
##            
#            self.setColorThresholds()
##            
#            self.findOrgDimensions(circle=1)
##            
#            self.TrackAtWall()
            
            # Print a success Message
            print(50*'=')
            print(' \n Successfully Loaded track {} from Tmin {} to Tmax {}. \n'.format(self.Organism,np.min(self.Time),np.max(self.Time)))
            print(50*'=')
        else:
            # Create an empty track to use for testing purposes
            self.T = []
            self.X = []
            self.Y = []
            self.Z = []
         
        
        
        
        
    def regularizeTrack(self):
        
        self.T = np.linspace(self.Time[0],self.Time[-1],self.trackLen)  # Create a equi-spaced (in time) vector for the data.

        #Sampling Interval
        self.dT = self.T[1]-self.T[0]
        self.samplingFreq = 1/float(self.dT)
        # Window to use for smoothing data. 
        # IMPORTANT: We only keep variations 10 times slower that the frame rate of data capture.
        self.window_time = 10*self.dT
        
#        print(25*'*')
#        print('Sampling Interval: {} s'.format(self.dT))
#        print('Sampling Frequency: {} Hz'.format(self.samplingFreq))
#        print(25*'*')
#        
#        print('Min Time Index: {}'.format(self.Tmin_index))
#        print('Max Time Index: {}'.format(self.Tmax_index))
#        print('no:of data points: {}'.format(self.trackLen))
#        print(25*'*')

        
        func_X = interpolate.interp1d(self.Time,self.Xobj, kind = 'linear')
        func_Y = interpolate.interp1d(self.Time,self.Yobj, kind = 'linear')
        func_Z = interpolate.interp1d(self.Time,self.ZobjWheel, kind = 'linear')
        
        self.X=func_X(self.T)     # Interpolated object positions
        self.Y=func_Y(self.T)     # Interpolated object positions
        self.Z=func_Z(self.T)     # Interpolated object positions
        
    #--------------------------------------------------------------------------
    #                       Boundaries equilibration
    #--------------------------------------------------------------------------
    def setAxesLimits(self):
        
        self.xmin=self.Xobj.min()
        self.xmax=self.Xobj.max()
        
        self.ymin=self.Yobj.min()
        self.ymax=self.Yobj.max()
        
#        print(self.ymin,self.ymax)
        
        self.zmin=self.ZobjWheel.min()
        self.zmax=self.ZobjWheel.max()
        
        print('Half Channel Length: {}.'.format(self.channelLength/float(2)))
        
        if self.xmax-self.xmin > self.channelLength or (self.xmin<-self.channelLength/float(2) or self.xmax> self.channelLength/float(2)):
            delta_x= -np.mean(self.Xobj)
            print(delta_x)
            self.Xobj+=delta_x
            self.xmin = self.Xobj.min()
            self.xmax = self.Xobj.max()
            if(self.xmin < -self.channelLength/float(2)):
                delta_x = -(self.xmin + self.channelLength/float(2))
                self.Xobj += delta_x
            elif(self.xmax > self.channelLength/float(2)):
                delta_x = -(self.xmax - self.channelLength/float(2))
                self.Xobj += delta_x
            
            
        
        if (self.ymax-self.ymin > self.channelWidth or (self.ymin<0 or self.ymax > self.channelWidth)):
            delta_y= -(np.mean(self.Yobj) - self.channelWidth/float(2))
            self.Yobj += delta_y
            self.ymin = self.Yobj.min()
            self.ymax = self.Yobj.max()
           
            
            if(self.ymin < 0):
                delta_y = -(self.ymin)
                self.Yobj += delta_y
            elif(self.ymax > self.channelWidth):
                delta_y = -(self.ymax - self.channelWidth)
                self.Yobj += delta_y
            
            
            
            self.xmin = self.Xobj.min()
            self.xmax = self.Xobj.max()
            self.ymin = self.Yobj.min()
            self.ymax = self.Yobj.max()
            print('Y min: {}'.format(self.ymin))
            print('Y max: {}'.format(self.ymax))
            
            print('X min: {}'.format(self.xmin))
            print('X max: {}'.format(self.xmax))
            
        self.xrange=int(np.ceil(self.xmax)-np.floor(self.xmin)+2)
        self.yrange=int(np.ceil(self.ymax)-np.floor(self.ymin)+2)
        self.zrange=int(np.ceil(self.zmax)-np.floor(self.zmin)+2)
        
        self.X_wall_min = min(self.xmin, -self.channelLength/float(2))
        self.X_wall_max = max(self.xmax, self.channelLength/float(2))
        self.Y_wall_min = min(self.ymin, 0)
        self.Y_wall_max = max(self.ymax, self.channelWidth)
        
        print('Location of X wall (min): {}'.format(self.X_wall_min))
        print('Location of X wall (max): {}'.format(self.X_wall_max))
        print('Location of Y wall (min): {}'.format(self.Y_wall_min))
        print('Location of Y wall (max): {}'.format(self.Y_wall_max))
        
    def TrackAtWall(self):
        self.atWall = np.array((self.X_smooth < (self.X_wall_min+self.OrgDim/float(2)))|(self.X_smooth > (self.X_wall_max - self.OrgDim/float(2)))|(self.Y_smooth < (self.Y_wall_min+self.OrgDim/float(2)))|(self.Y_smooth > (self.Y_wall_max - self.OrgDim/float(2))), dtype='bool')
        
    def setColorThresholds(self):
        saveFile = 'colorThresholds.pkl'
        ii=0
        image_a = None
        while(image_a is None):
            if(self.ImageName[ii]):
                imageName = self.ImageName[ii]
                print('Sample image: {}'.format(imageName))
                image_a = cv2.imread(os.path.join(self.imagePath,self.ImageName[ii]))
                
                ii += 1
            else:
                ii += 1
           
      
        self.imH, self.imW, *rest = np.shape(image_a)
    
            
        
        print('Image Width: {} px \n Image Height: {} px'.format(self.imW, self.imH))
        
        if(not os.path.exists(os.path.join(self.root, saveFile))):
            
            print(os.path.join(self.imagePath,self.ImageName[ii]))
            v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = rangeslider_functions.getColorThreshold(os.path.join(self.imagePath,imageName))
            threshLow = (v1_min,v2_min,v3_min)
            threshHigh = (v1_max,v2_max,v3_max)
            
            with open(os.path.join(self.root,saveFile), 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((threshLow, threshHigh), f)
        else:
            print('Loading file {} ...'.format(os.path.join(self.root,saveFile)))
            with open(os.path.join(self.root,saveFile), 'rb') as f:
                threshLow, threshHigh = pickle.load(f)
                
        self.threshLow = threshLow
        self.threshHigh = threshHigh
        
        print('Color thresholds for segmentation: \n LOW: {}, HIGH : {}'.format(self.threshLow, self.threshHigh))
            
        
        
    def findOrgDimensions(self, circle=0):
        # Finds the maximum dimensions of the organism 
        saveFile = 'orgDims.pkl'
        
        OrgMajDim = []
        OrgMinDim = []
        OrgDim = []
        overwrite = False
        if(not os.path.exists(os.path.join(self.root,saveFile)) or overwrite):
            
            fileList = os.listdir(self.imagePath)
            # Calculate based on 100 images
            for ii,file in enumerate(fileList[:100]):
                image = cv2.imread(os.path.join(self.imagePath,file))
                
                
            
                
                orgContour = self.colorThreshold(image = image)
                
                if(orgContour is not None):
                
                    if(circle):
                        (x_center,y_center), Radius = cv2.minEnclosingCircle(orgContour)
                        center = (int(x_center), int(y_center))
#                        plt.figure(1)
#                        plt.clf()
#                        cv2.circle(image,center, int(Radius),(0,255,0),2)
#                        plt.imshow(image)
#                        plt.pause(0.001)
#                        plt.show(block=True)
                        
                        OrgMajDim.append(mmPerPixel(self.imW)*2*Radius)
                        OrgMinDim.append(mmPerPixel(self.imW)*2*Radius)
                        
                        OrgDim.append(mmPerPixel(self.imW)*(2*Radius))
                    else:
                        try:
                            ellipse = cv2.fitEllipse(orgContour)
                            OrgMajDim.append(mmPerPixel(self.imW)*ellipse[1][0])
                            OrgMinDim.append(mmPerPixel(self.imW)*ellipse[1][1])
                            OrgDim.append(mmPerPixel(self.imW)*(ellipse[1][1] + ellipse[1][0])/float(2))
                            
                            plt.figure(1)
                            plt.clf()
                            cv2.ellipse(image,box=ellipse,color=[0,1,0])
                            plt.imshow(image)
                            plt.pause(0.001)
                            plt.show(block=True)
                        except:
                            OrgMajDim.append(np.nan)
                            OrgMinDim.append(np.nan)
                            OrgDim.append(np.nan)
                            
                else:
                    continue
                            
                        
                        
                    
                    
                    
                    

                    
                    
            
            
            OrgDim_mean = np.nanmax(np.array(OrgDim))
            OrgMajDim_mean = np.nanmax(np.array(OrgMajDim))
            OrgMinDim_mean = np.nanmax(np.array(OrgMinDim))
            
            with open(os.path.join(self.root,saveFile), 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((OrgDim_mean, OrgMajDim_mean, OrgMinDim_mean), f)
                
        else:
            with open(os.path.join(self.root,saveFile), 'rb') as f:
                OrgDim_mean, OrgMajDim_mean, OrgMinDim_mean = pickle.load(f)
        
        self.OrgDim = OrgDim_mean
        self.OrgMajDim = OrgMajDim_mean
        self.OrgMinDim = OrgMinDim_mean
        
        print('*'*50)
        print('Organism dimension {} mm'.format(self.OrgDim))
        print('Organism Major dimension {} mm'.format(self.OrgMajDim))
        print('Organism Minor dimension {} mm'.format(self.OrgMinDim))
        print('*'*50)

        
    def colorThreshold(self,image):
    
        thresh_low = np.array(self.threshLow,dtype='uint8')
        thresh_high = np.array(self.threshHigh,dtype='uint8')
        
   
        
        im_th = cv2.inRange(image, thresh_low, thresh_high)
        
        kernel3 = np.ones((3,3),np.uint8)
        kernel5 = np.ones((5,5),np.uint8)
        kernel7 = np.ones((7,7),np.uint8)
        kernel15 = np.ones((15,15),np.uint8)
        
        
        im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel5)
        
        im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel7)
        
        im_th = cv2.morphologyEx(im_th, cv2.MORPH_OPEN, kernel7)
        
        im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel15)
    
        
    #    plt.matshow (im_th , cmap=cm.Greys_r )
    #    plt.show()
        
        # Select the largest contour as the final mask
        cnts = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        print('No:of contours:{}'.format(len(cnts)))
        
        if(len(cnts)>0):
            largestContour = max(cnts, key=cv2.contourArea)
        
            M = cv2.moments(largestContour)
            
            # Approximate the contour to 1% of its arcLength
            epsilon = 0.01*cv2.arcLength(largestContour,True)
            approxContour = cv2.approxPolyDP(largestContour,epsilon,True)
                    
            
    #        orgCentroid = np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
            
    #        ellipse = cv2.fitEllipse(approxContour)
                
                
                # in mm
        
            return approxContour
        
        else:
            return None
        
    def computeVelocity(self):
        
        self.Vx=[]
        self.Vy=[]
        self.Vz=[]
        
        for i in range(self.trackLen-1):
            self.Vx.append((self.X_smooth[i+1]-self.X_smooth[i])/(self.T[i+1]-self.T[i]))
            self.Vy.append((self.Y_smooth[i+1]-self.Y_smooth[i])/(self.T[i+1]-self.T[i]))
            self.Vz.append((self.Z_smooth[i+1]-self.Z_smooth[i])/(self.T[i+1]-self.T[i])) 
            
#            self.Vx.append((self.Xobj[i+1]-self.Xobj[i])/(self.Time[i+1]-self.Time[i]))
#            self.Vy.append((self.Yobj[i+1]-self.Yobj[i])/(self.Time[i+1]-self.Time[i]))
#            self.Vz.append((self.ZobjWheel[i+1]-self.ZobjWheel[i])/(self.Time[i+1]-self.Time[i])) 
            
    
        self.Vx=np.array(self.Vx)
        self.Vy=np.array(self.Vy)
        self.Vz=np.array(self.Vz)
        
#        self.Vx, self.Vy, self.Vz = self.smoothVelocity(self.window_time)
        
        self.Speed = (self.Vx**2 + self.Vy**2 + self.Vz**2)**(1/2)
        
        self.Speed_z = (self.Vz**2)**(1/2)
        
    def smoothSignal(self, data, window_time):      # Window is given in seconds
        
        avgWindow = int(window_time*self.samplingFreq)
        
#        if(pd.__version__ is not '0.20.3'):
#            return data.rolling(avgWindow).mean()
#        else:
        return pd.rolling_mean(data, avgWindow, min_periods = 1, center = True)
    
    def smoothTrack(self, window_time):      # Window is given in seconds
        
        self.X_smooth = self.smoothSignal(self.X,window_time)
        self.Y_smooth = self.smoothSignal(self.Y,window_time)
        self.Z_smooth = self.smoothSignal(self.Z,window_time)
        
        return self.X_smooth, self.Y_smooth, self.Z_smooth
    
    def smoothVelocity(self, window_time):      # Window is given in seconds
        
        return self.smoothSignal(self.Vx,window_time), self.smoothSignal(self.Vy,window_time), self.smoothSignal(self.Vz,window_time)
    
    # Analysis Functions
    def find_freq(self,data):
        # Starfish
#        peaks=signal.find_peaks(data,distance=100,width=100,prominence=(5,20))
        # Dendraster
        peaks = signal.find_peaks(-data,distance=30,width=30,prominence=(0.6, 4))
        freq=len(peaks[0])/(self.T[-1]-self.T[0])
        return freq,peaks[0]
    
    def removeOutliers(self,data, Tmin, Tmax):
        
        Tmin_index = next((i for i,x in enumerate(self.Time) if x > Tmin), None)
        Tmax_index = next((i for i,x in enumerate(self.Time) if x > Tmax), None)
#        mean_data = np.nanmean(data)
#        stdev_data = np.nanstd(data)
#        mask = np.abs(data-mean_data)>=nStdev*stdev_data 
        data[Tmin_index:Tmax_index] = np.nan
        
        indexArray = np.array(range(0,len(data)))
        print(50*'*')
        print(indexArray)
        print(Tmin_index)
        print(Tmax_index)
        print(data[Tmin_index:Tmax_index])
        print(50*'*')
        subIndexArray = indexArray[Tmin_index:Tmax_index]
        
        
        f = interpolate.interp1d(indexArray[~np.isnan(data)],data[~np.isnan(data)], kind = 'linear')
        
        interpValues = f(indexArray)
        
        print(50*'*')
        print('Interpolated values')
        print(interpValues)
        print(np.shape(interpValues))
        print(np.shape(data))
      
        print(data[Tmin_index:Tmax_index])
        print(50*'*')
        
        
        data = interpValues
        
        return data
        
#--------------------------------------------------------------------------
#                            PLOT Functions
#--------------------------------------------------------------------------    
    def plotTrackWalls(self,plotPeaks=0, walls=0, labels = 0, save = 0):
        #--------------------------------------------------------------------------
        labelStatus = {0:'OFF',1:'ON'}

#        f1 = plt.figure(figsize=plt.figaspect(1)*2)
        f1 = plt.figure(figsize=(8,12),dpi=150)
        grid = plt.GridSpec(self.xrange+self.yrange+self.zrange, 1, wspace=1, hspace=8)
        #--------------------------------------------------------------------------
        # Z
        #--------------------------------------------------------------------------
        ax7=plt.subplot(grid[self.xrange+self.yrange:])
        plt.plot(self.T,self.Z, color = 'b', lineWidth=1)
        if(walls):
            plt.scatter(self.T[self.atWall],self.Z_smooth[self.atWall],10, color = 'r')
        
#        plt.xlabel('T (s)')
#        plt.ylabel('Z (mm)')
        plt.xlim( self.T[0],self.T[-1])
#        plt.ylim( np.floor(self.Z.min()),np.ceil(self.Z.max())+1)
        plt.ylim( 0,np.ceil(self.Z.max())+1)

        
        if plotPeaks is not 0:
          
            indexArray = np.array([i for i in range(len(self.T))],dtype='int')
            
            for ii in range(len(self.peaks)):
                plt.fill_between(self.T[self.peaks[ii]:self.peaks_neg[ii]],self.Z[self.peaks[ii]:self.peaks_neg[ii]],y2 =0,color = 'r',alpha = 0.5)
            
            # Vertical lines for the start of the blink
            for ii in indexArray[self.peak_indicator]:
                plt.vlines(self.T[ii],np.floor(self.Z.min())-1,self.Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='g')
        
            # Vertical lines for end of the blink
            for ii in indexArray[self.peak_indicator_neg]:
                plt.vlines(self.T[ii],np.floor(self.Z.min())-1,self.Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='r')
#        
        if(not labels):
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.set_xticklabels([])
       
        #--------------------------------------------------------------------------
        # X
        #--------------------------------------------------------------------------
        ax5=plt.subplot(grid[:self.xrange],sharex=ax7)
        plt.plot(self.T,self.X, color = 'r',lineWidth=1)
        if(walls):
            plt.scatter(self.T[self.atWall],self.X_smooth[self.atWall],10, color = 'r')
#        plt.ylabel('X (mm)')
        p5 = patches.Rectangle((self.T[0]-self.channelWidth, -self.channelLength/float(2)), self.T[-1]-self.T[0]+2*self.channelWidth, 2*self.channelLength,fill=False,linestyle='--')
        ax5.add_patch(p5)
        plt.xlim( self.T[0],self.T[-1])
        plt.ylim( np.floor(self.X.min())-1,np.ceil(self.X.max())+1)
        plt.setp(ax5.get_xticklabels(), visible=False)
#        plt.title('Trajectory projection')
        if(not labels):
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.set_xticklabels([])
        
        #--------------------------------------------------------------------------
        # Y
        #--------------------------------------------------------------------------
        ax6=plt.subplot(grid[self.xrange:self.xrange+self.yrange],sharex=ax7)
        plt.plot(self.T,self.Y, color = 'g',lineWidth=1)
        if(walls):
            plt.scatter(self.T[self.atWall],self.Y_smooth[self.atWall],10, color = 'r')
        p6 = patches.Rectangle((self.T[0]-self.channelWidth, 0), self.T[-1]-self.T[0]+2*self.channelWidth, self.channelWidth, fill=False,linestyle='--')
        ax6.add_patch(p6)
        
        
        plt.xlim( self.T[0],self.T[-1])
#        plt.ylabel('Y (mm)')
        plt.setp(ax6.get_xticklabels(), visible=False)
        
        plt.ylim( np.floor(self.Y.min())-1,np.ceil(self.Y.max())+1)
        
        #plt.savefig(path+'Trajectory_in_Time.png',dpi=300)
        
        if(not labels):
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.set_xticklabels([])
#        plt.savefig(os.path.join(self.savePath,self.TrackName+'_TrueScale_Trajectory_Blinks_Walls'+self.imgFormat),dpi=300)
         
        if(save):
            plt.savefig(os.path.join(self.savePath,self.TrackName+'_EqualScale_Trajectory_Walls'+labelStatus[labels]+self.imgFormat),dpi=300)

        
        plt.show()
            

    def plot3DComponents(self,signalX = None,signalY=None,signalZ=None, plotPeaks=0, walls = 0, labels=0, save = 0):
        labelStatus = {0:'OFF',1:'ON'}
        #--------------------------------------------------------------------------
        f1 = plt.figure(figsize=(8,6))
##        --------------------------------------------------------------------------
#        # X
#        #--------------------------------------------------------------------------
        T_low = 186
        T_high = 196
#        if(signalX is not None):
#            ax5 = plt.subplot(311)
#            plt.plot(self.T,signalX, color = 'r',lineWidth=1)
#            if(walls):
#                plt.scatter(self.T[self.atWall],signalX[self.atWall],10, color = 'r')
#            p5 = patches.Rectangle((self.T[0]-self.channelWidth, -self.channelLength/float(2)), self.T[-1]-self.T[0]+2*self.channelWidth, 2*self.channelLength,fill=False,linestyle='--')
#            ax5.add_patch(p5)
#            plt.ylabel('X')
#         
#            plt.xlim( T_low, T_high)
#            plt.ylim( np.floor(signalX.min())-1,np.ceil(signalX.max())+1)
#            plt.setp(ax5.get_xticklabels(), visible=False)
#            
#            if(not labels):
#                ax = plt.gca()
#                ax.set_yticklabels([])
#                ax.set_xticklabels([])
        
#        
#        #--------------------------------------------------------------------------
#        # Y
#        #--------------------------------------------------------------------------
#        if(signalY is not None):
#            ax6=plt.subplot(312)
#            plt.plot(self.T,signalY,color = 'g',lineWidth=1)
#            if(walls):
#                plt.scatter(self.T[self.atWall],signalY[self.atWall],10, color = 'k')
#            p6 = patches.Rectangle((self.T[0]-self.channelWidth, 0), self.T[-1]-self.T[0]+2*self.channelWidth, self.channelWidth, fill=False,linestyle='--')
#            ax6.add_patch(p6)
#            plt.ylabel('Y')
#         
#            plt.xlim( T_low, T_high)
#            plt.ylim( np.floor(signalY.min())-1,np.ceil(signalY.max())+1)
#            plt.setp(ax6.get_xticklabels(), visible=False)
#            if(not labels):
#                ax = plt.gca()
#                ax.set_yticklabels([])
#                ax.set_xticklabels([])
#        plt.savefig(path+'Trajectory_in_Time.png',dpi=300)
#    
        #--------------------------------------------------------------------------
        # Z
        #--------------------------------------------------------------------------
        if(signalZ is not None):
#            ax7=plt.subplot(313)
    
            plt.plot(self.Time/3600,signalZ,color = 'b', linewidth=2)
            
    #        plt.fill_between(self.T,0,signalZ,color='b',alpha=0.2)
#            plt.scatter(self.T, signalZ,10,color='b', alpha=0.5)
            if(walls):
                plt.scatter(self.T[self.atWall],signalZ[self.atWall],10, color = 'k')
                
            if plotPeaks is not 0:
              
                indexArray = np.array([i for i in range(len(self.T))],dtype='int')
                
                for ii in range(len(self.peaks)):
                    plt.fill_between(self.T[self.peaks[ii]:self.peaks_neg[ii]],self.Z[self.peaks[ii]:self.peaks_neg[ii]],y2 =0,color = 'r',alpha = 0.5)
                
                # Vertical lines for the start of the blink
    #a            for ii in indexArray[self.peak_indicator]:
    #                plt.vlines(self.T[ii],np.floor(self.Z.min())-1,self.Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='g')
            
                # Vertical lines for end of the blink
    #            for ii in indexArray[self.peak_indicator_neg]:
    #                plt.vlines(self.T[ii],np.floor(self.Z.min())-1,self.Z[ii],linewidth=1,linestyles='-',alpha=1.0,color='r')
    #        
    
       
    #        plt.ylabel('Z')
    #        plt.xlabel('Time (s)')
            
#            plt.xlim( T_low, T_high)
#            plt.ylim(14.4,16.1)
    
#            plt.xlim( self.T[0],self.T[-1])
#
#            plt.ylim(0,signalZ.max()+1)
            ax = plt.gca()
            
            if(not labels):
                
                ax.set_yticklabels([])
                ax.set_xticklabels([])
            
#        plt.minorticks_on()
        if(save):
#            plt.savefig(os.path.join(self.savePath,self.TrackName+'_BlinksZoomed_'+labelStatus[labels]+self.imgFormat),dpi=150)

            plt.savefig(os.path.join(self.savePath,self.TrackName+'_Z_Trajectory'+labelStatus[labels]+self.imgFormat),dpi=300)
#           plt.savefig(os.path.join(self.savePath,self.TrackName+'_Z_trajectory_peaks'+'.png'),dpi=150)

        plt.show()
    
    
    def plotTrackXZ(self,Tmin,Tmax):
        
        Tmin_index = next((i for i,x in enumerate(self.T) if x > Tmin), None)
        Tmax_index = next((i for i,x in enumerate(self.T) if x > Tmax), None)

#        f,ax = plt.subplots()
#        plt.plot(self.X_smooth[Tmin_index:Tmax_index],self.Z_smooth[Tmin_index:Tmax_index],color='k',linewidth=1,alpha=0.5,zorder=1)
#        ax1 = plt.scatter(self.X_smooth[Tmin_index:Tmax_index],self.Z_smooth[Tmin_index:Tmax_index],25, c = self.Speed[Tmin_index:Tmax_index], cmap = cmocean.cm.speed, marker = 'o',zorder=2)
#        plt.scatter(self.X_smooth[Tmin_index],self.Z_smooth[Tmin_index], 100, marker = 'x', color = 'k',zorder=3)
#        cbar = plt.colorbar(ax1)
#        plt.ylabel('Z (mm)')
#        plt.xlabel('X (mm)')
#        
#        
#        scalebar = AnchoredSizeBar(ax.transData,
#                           0.25, '250 um', 'lower left', 
#                           pad=0.1,
#                           color='black',
#                           frameon=False,
#                           size_vertical=0.01)
#
#        ax.add_artist(scalebar)
#        plt.axis('equal')
#        ax.axes.get_xaxis().set_visible(False)
#        ax.axes.get_yaxis().set_visible(False)
#        plt.show()
        
        print('Min Speed : {} mm/s '.format(self.Speed[Tmin_index:Tmax_index].min()))
        print('Max Speed : {} mm/s '.format(self.Speed[Tmin_index:Tmax_index].max()))
        f,ax = plt.subplots()
        plt.plot(self.X_smooth[Tmin_index:Tmax_index],self.Z_smooth[Tmin_index:Tmax_index],color='k',linewidth=1,alpha=0.5,zorder=1)
        ax1 = plt.scatter(self.X_smooth[Tmin_index:Tmax_index],self.Z_smooth[Tmin_index:Tmax_index],25, c = self.Speed[Tmin_index:Tmax_index], cmap = cmocean.cm.speed, marker = 'o',vmin=0,vmax=2,zorder=2)
        plt.scatter(self.X_smooth[Tmin_index],self.Z_smooth[Tmin_index], 100, marker = 'o',zorder=3, facecolor = 'None', edgecolor = 'k',linewidth=2)
        plt.scatter(self.X_smooth[Tmax_index],self.Z_smooth[Tmax_index], 150, marker = 'X', color = 'r',zorder=3)

        cbar = plt.colorbar(ax1)
        
#        plt.ylabel('Z (mm)')
#        plt.xlabel('X (mm)')
        scalebar = AnchoredSizeBar(ax.transData,
                           0.25,'','upper left', 
                           pad=0.1,
                           color='black',
                           frameon=False,
                           size_vertical=0.01)
        ax.add_artist(scalebar)
        ax.set_aspect(1/5)
        
        
        ax.set_xticklabels([])
        ax.set_yticklabels([])
#        ax.axes.get_xaxis().set_visible(False)
#        ax.axes.get_yaxis().set_visible(False)
#        plt.savefig(os.path.join(self.savePath,self.TrackName+'_Trajectory_aspect_5_{}_{}'.format(int(Tmin),int(Tmax))+self.imgFormat),dpi=300)
        plt.show()
        
    def plot_XZ_fixedWindow(self,TimePoint,TimeDuration, save = 0):
       
        window_size_X = 5
        window_size_Z = 5
        Time_index = next((i for i,x in enumerate(self.T) if x > TimePoint), None)

        T_min = next((i for i,x in enumerate(self.T) if x > TimePoint - TimeDuration/2), None)
        T_max = next((i for i,x in enumerate(self.T) if x > TimePoint + TimeDuration/2), None)
        
        x_min = np.min(self.X_smooth[T_min:T_max])
        x_max = np.max(self.X_smooth[T_min:T_max])
        z_min = np.min(self.Z_smooth[T_min:T_max])
        z_max = np.max(self.Z_smooth[T_min:T_max])
        
        diff_x = abs(x_max - x_min) - window_size_X
        diff_z = abs(z_max - z_min) - window_size_Z
        
        x_min += diff_x/2
        x_max -= diff_x/2
        
        z_min += diff_z/2
        z_max -= diff_z/2
        
        
        plt.figure(1)
#        ax1 = plt.plot(self.X_smooth[mask],self.Z_smooth[mask],color='k',linewidth=1,alpha=0.5,zorder=1)
        ax2 = plt.scatter(self.X_smooth[T_min:T_max],self.Z_smooth[T_min:T_max],25, c = self.Speed[T_min:T_max], cmap = cmocean.cm.amp, marker = 'o',zorder=2, alpha = 1, edgecolors=None, linewidths=0)
        plt.scatter(self.X_smooth[T_min],self.Z_smooth[T_min], 100, marker = 'o',zorder=3, facecolor = 'None', edgecolor = 'k',linewidth=2)
        plt.scatter(self.X_smooth[T_max],self.Z_smooth[T_max], 150, marker = 'X', color = 'r',zorder=3)
        
#        plt.scatter(self.X_smooth[Time_index],self.Z_smooth[Time_index], 100, marker = 'o',zorder=3, facecolor = 'None', edgecolor = 'k',linewidth=2)
        
        plt.axis('equal')
        plt.xlim(x_min, x_max)
        plt.ylim(z_min, z_max)
        
#        plt.xlim(self.X_smooth[Time_index] - window_size_X/2,self.X_smooth[Time_index] + window_size_X/2)
#        plt.ylim(self.Z_smooth[Time_index] - window_size_Z/2,self.Z_smooth[Time_index] + window_size_Z/2)
        
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        scalebar = AnchoredSizeBar(ax.transData,
                           0.5, '', 'lower left', 
                           pad=0.1,
                           color='black',
                           frameon=False,
                           size_vertical=0.01)
#        cbar = plt.colorbar(ax2, ax = ax)

        ax.add_artist(scalebar)
#        ax.set_aspect(1/5)
        
        
        ax.axis('off')
#        ax.set_xticklabels([])
#        ax.set_yticklabels([])
#        ax.axes.get_xaxis().set_visible(False)
#        ax.axes.get_yaxis().set_visible(False)
        plt.savefig( os.path.join(self.savePath,self.TrackName+'_Trajectory_Time_{}_Duration_{}'.format(int(TimePoint), int(TimeDuration))+self.imgFormat),dpi=300, transparent = True)
        plt.show()
        
        fig, ax = plt.subplots()
        cbar = plt.colorbar(ax2, ax = ax)
        ax.remove()
        if(save):
            plt.savefig( os.path.join(self.savePath,self.TrackName+'ColorBar_Trajectory_Time_{}_Duration_{}'.format(int(TimePoint), int(TimeDuration))+self.imgFormat),dpi=300, transparent = True)
        plt.show()
        
    def plotVelocity(self,Vx,Vy,Vz):
        #--------------------------------------------------------------------------
        f1 = plt.figure()
        #--------------------------------------------------------------------------
        # X
        #--------------------------------------------------------------------------
        ax5=plt.subplot(311)
        plt.plot(self.T[:-1],Vx, color = 'r')
        
        plt.ylabel('Vx (mm/s)')
     
        plt.xlim( self.T[0],self.T[-1])
        
        plt.setp(ax5.get_xticklabels(), visible=False)
        
        plt.title('Trajectory projection')
        
        #--------------------------------------------------------------------------
        # Y
        #--------------------------------------------------------------------------
        ax6=plt.subplot(312)
        plt.plot(self.T[:-1],Vy, color = 'r')
     
        plt.xlim( self.T[0],self.T[-1])
        plt.ylabel('Vy (mm/s)')
        
        plt.ylim( np.floor(self.ymin)-1,np.ceil(self.ymax)+1)
        
        #plt.savefig(path+'Trajectory_in_Time.png',dpi=300)
    
        #--------------------------------------------------------------------------
        # Z
        #--------------------------------------------------------------------------
        ax7=plt.subplot(313)
        plt.plot(self.T[:-1],Vz, color = 'r')
        
        
        plt.xlabel('T (s)')
        plt.ylabel('Vz (mm/s)')
        plt.xlim( self.T[0],self.T[-1])
        
        plt.show(block=False)
        
    def find_peaks(self,data, distance = None, width = None, prominence = None):
        peaks=signal.find_peaks(data, distance= distance,width= width,prominence= prominence)
        return peaks[0] 
        
    def loadPeaks(self, peaks_ind_pos, peaks_ind_neg):
        self.peaks = []
        self.peaks_neg = []
        
        for ii in range(self.trackLen):
            
            if(peaks_ind_pos[ii]):
                self.peaks.append(ii)
            if(peaks_ind_neg[ii]):
                self.peaks_neg.append(ii)
                
        
        
        
        
    def findBlinks(self, timeWindow = 10):
        
        X_smooth, Y_smooth, Z_smooth = self.smoothTrack(timeWindow)
        
        Z_fast = self.Z - Z_smooth
        
        
#        plt.figure()
#        plt.plot(self.Time,Z_fast,color='k')
        
        #Starfish
        self.peaks = self.find_peaks(Z_fast, prominence = (5,40))
        self.peaks_neg = self.find_peaks(-Z_fast, prominence = (5,40))
        
        # Dendraster
#        self.peaks = self.find_peaks(Z_fast, width=(0,3000),prominence=(0.4, 10))
#        self.peaks_neg = self.find_peaks(-Z_fast, width=(0,3000),prominence=(0.4, 10))
        
        peak_indicator=[0 for i in range(len(self.Time))]
        
        for j in self.peaks:
            peak_indicator[j]= 1
            
        peak_indicator_neg=[0 for i in range(len(self.Time))]
        
        for j in self.peaks_neg:
            peak_indicator_neg[j] = 1
    
        self.peak_indicator = np.array(peak_indicator, dtype='bool')
        self.peak_indicator_neg = np.array(peak_indicator_neg, dtype='bool')
    
        print('Number of Positive Peaks: {}'.format(len(self.peaks)))
        print('Number of Negative Peaks: {}'.format(len(self.peaks_neg)))
        
        print(self.T)
        
        print(Z_fast)
      
        
#        plt.figure()
#        plt.plot(self.T,Z_fast)
#        plt.scatter(self.T[self.peak_indicator],Z_fast[self.peak_indicator],10,color='r')
#        plt.scatter(self.T[self.peak_indicator_neg],Z_fast[self.peak_indicator_neg],20,color='g')
        
        return self.peaks, self.peaks_neg, Z_fast
    
    def plotAlignedBlinks(self,labels=0):
        labelStatus = {0:'OFF',1:'ON'}

     #======================================================================
#    # Aligned plots of blinks
#    #======================================================================
        Twindow = 40
        nWindow = math.ceil(int(Twindow*self.samplingFreq)/2.)*2
        T_blink = np.zeros(nWindow)
        
        nBlinks = len(self.peaks)
        print('No:of blinks: {}'.format(nBlinks))
        color = plt.cm.inferno(np.linspace(0, 1,nBlinks))
            
    #    color = cmocean.cm.algae(np.linspace(0, 1,nBlinks))
    
        plt.rcParams['axes.prop_cycle'] = cycler.cycler('color', color)
        
        Z_blink = np.zeros((nBlinks,nWindow),dtype='float')
        plt.figure(3)
        for i,peakIndex in enumerate(self.peaks):
            
            lower_index = peakIndex - int((1/2)*nWindow)
            upper_index = peakIndex + int((1/2)*nWindow)
            if(lower_index>=0 and upper_index<self.trackLen):
                T_blink = self.T[lower_index:upper_index] - self.T[peakIndex]
                Z_blink[i,:] = self.Z[lower_index:upper_index] - self.Z[peakIndex]
                
#                ax1 = plt.plot(T_blink, Z_blink[i,:], alpha = 0.8, linewidth = 4)
                ax1 = plt.scatter(T_blink, Z_blink[i,:], 10, marker ='o',alpha = 0.8, linewidth=0)

            
            
        plt.xlabel('Time (s)')
        plt.ylabel('Z (mm)')
        if(not labels):
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.set_xticklabels([])
#        plt.savefig(os.path.join(self.savePath,self.TrackName+'_AlignedBlinks'+'_labels_'+labelStatus[labels]+self.imgFormat),dpi=150)

#        plt.savefig(os.path.join(resultFolder,'Dendraster3_AlignedBlinks'+self.imgFormat),dpi=300)
        plt.show()
        
#        print(np.shape(Z_blink))
#        print(np.shape(T_blink))
#        with open(os.path.join(resultFolder,TrackName+'_aligned_blinks' + '.pkl'), 'wb') as f:  # Python 3: open(..., 'wb')
#                    pickle.dump((T_blink, Z_blink), f) 
#    
        
        # Plot the mean behavior across all blinks combined.
        
        
        # Create a pandas dataframe of all the blinks
        
        
        
        df = pd.DataFrame({'Time': [], 'Z (mm)':[]})
        
        for ii in range(len(self.peaks)):
            df = df.append(pd.DataFrame({'Time':T_blink, 'Blink Number':np.repeat(ii, len(T_blink),axis=0),'Z (mm)':np.transpose(Z_blink[ii,:])}))
            
            
        palette = sns.color_palette("Blues", len(self.peaks))
        
        
        print(df)
        
        plt.figure()
        
        
        ax = sns.lineplot(x = 'Time',y = 'Z (mm)', data = df, lw = 3,ci = 95, palette = palette, legend = False)
        
        ax.set_aspect(1)
        
        plt.show()


        
        return df
    
    def makeMovie(self, ImageFolder, saveFolder):
        
        
        for ii in range(self.trackLen):
            
            if(self.ImageName[ii]):
                
                image_a = self.ImageName[ii]
                
                print(image_a)
                
                frame_a = cv2.imread(os.path.join(ImageFolder, image_a))
                
                cv2.imshow('frame1',frame_a)
                
                frame_gs = cv2.cvtColor(frame_a,cv2.COLOR_BGR2GRAY)
                
                if(self.LED_intensity[ii] > 0):
                    text = 'Light ON'
                    color = (0,255,255)
                else:
                    text = 'Light OFF'
                    color = (255,255,255)
                    
                currTime = self.Time[ii]
                
                # Enhance the local contrast of the image.
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12,12))
                frame_clahe = clahe.apply(frame_gs)
                
                frame_color = cv2.cvtColor(frame_clahe, cv2.COLOR_GRAY2BGR)   
                
                cv2.putText(frame_color, str(np.round(currTime, decimals = 2))+'s', (30, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.putText(frame_color, text, (720 - 200, 50), font, 1, color, 2, cv2.LINE_AA)
                

                cv2.imshow('frame',frame_color)
                
                cv2.imwrite(os.path.join(saveFolder,image_a),frame_color)
                
                k = cv2.waitKey(10)
                
                if(k==27):
                    break
                
        
        cv2.destroyAllWindows()
                    
                
        

                
                
        
        
        
        
            