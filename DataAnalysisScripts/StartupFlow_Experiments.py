#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 21:49:18 2019
Data analysis for start-up flow experiments
Load the tracks into memory and compute the
@author: deepak
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
import scipy.ndimage as ndimage
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
import rangeslider_functions
import cv2
import PIV_Functions
import scipy.interpolate as interpolate
imp.reload(PIV_Functions)

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
rcParams.update({'font.size': 18})

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

class gravMachineTrack:

    def __init__(self, path, Tmin=0, Tmax=0):
        
        self.path = path
        
        self.openFile()
        
        self.imgFormat = '.svg'
        self.root, self.Organism = os.path.split(self.path)
        
        
        
        self.PIVfolder = os.path.join(self.path, 'PIVresults_64px')
        
        if(not os.path.exists(self.PIVfolder)):
            os.makedirs(self.PIVfolder)
        
        self.df = pd.read_csv(os.path.join(self.path, self.trackFile))
        
        self.ColumnNames = list(self.df.columns.values)
        
        print(self.ColumnNames)
        
        # X position relative to image center
        self.Xobj_name = self.ColumnNames[1]
        self.Yobj_name = self.ColumnNames[2]
        # Z position relative to image center
        self.Zobj_name = self.ColumnNames[3]
        
        self.df['Time'] = self.df['Time'] - self.df['Time'][0]
        
    
        # Crop the track based on the specified time limits
        if(Tmax==0):
            Tmax = np.max(self.df['Time'])
                    
        Tmin_index = next((i for i,x in enumerate(self.df['Time']) if x >= Tmin), None)
        Tmax_index = next((i for i,x in enumerate(self.df['Time']) if x >= Tmax), None)
          
        print(Tmin_index)
        print(Tmax_index)
                
        
        self.df = self.df[Tmin_index:Tmax_index]
        
        df_index = self.df.index.values
        
        
        df_index = df_index - df_index[0]
    
        self.df = self.df.set_index(df_index)
        
        print(self.df['ZobjWheel'])
        
        self.df['ZobjWheel'] = self.df['ZobjWheel'] - self.df['ZobjWheel'][0]
        
        self.trackLen = len(self.df)
        
        # Find the average sampling frequency
        self.T = np.linspace(self.df['Time'][0],self.df['Time'][self.trackLen-1], self.trackLen)  # Create a equi-spaced (in time) vector for the data.

        #Sampling Interval
        self.dT = self.T[1]-self.T[0]
        self.samplingFreq = 1/float(self.dT)
        # Window to use for smoothing data. 
        # IMPORTANT: We only keep variations 10 times slower that the frame rate of data capture.
        self.window_time = 50*self.dT
        
        self.computeVelocity()
        self.computeAccln()
        
#        self.computeDisplacement()
        
        self.createImageIndex()
        
        self.setColorThresholds()
        
        
        # PIV parameters
        self.window_size = 64
        self.overlap = 32
        self.searchArea = 64
        
 
        self.pixelPermm =  314*(self.imW/720)   # Pixel per mm for TIS camera (DFK 37BUX273) and 720p images
        
        self.mmPerPixel = 1/self.pixelPermm
        
        print('Pixels per mm: {}'.format(self.pixelPermm))
        
        self.findOrgDims(circle=1)
        
        
    def openFile(self):
        print('Opening dataset ...')

        self.image_dict = {}
        
        trackFileNames = []
        if os.path.exists(self.path):

            # Walk through the folders and identify ones that contain images
            for dirs, subdirs, files in os.walk(self.path, topdown=False):
               
                root, subFolderName = os.path.split(dirs)
                    
                print(subFolderName[0:6])
                if('images' in subFolderName):
                   
                   for fileNames in files:
                       key = fileNames
                       value = subFolderName
                       self.image_dict[key]=value

                if(os.path.normpath(dirs) == os.path.normpath(self.path)):
                    for fileNames in files:
                        if('.csv' in fileNames):
                            trackFileNames.append(fileNames)

            if(len(trackFileNames)==0):
                raise FileNotFoundError('CSV track was not found!')      
            elif(len(trackFileNames)>1):
                print('More than one .csv file found! Using the most recent one ...')
                
#                self.trackFile = 'track_division.csv'
                self.trackFile = 'track.csv'

                print('Loaded {}'.format(self.trackFile))
                
#                for tracks in trackFileNames:
#                    if('division' in tracks):
#                        self.trackFile = tracks
#                        print('Loaded {}'.format(self.trackFile))
#                    elif('mod' in tracks):
#                        self.trackFile = tracks
#                        print('Loaded {}'.format(self.trackFile))

            else:
                self.trackFile = trackFileNames[0]
                print('Loaded {}'.format(self.trackFile))
    
    def createImageIndex(self):
        # Create an index of all time points for which an image is available
        self.imageIndex = []
        for ii in range(self.trackLen):
            
            if(self.df['Image name'][ii] is not np.nan):
#                print(self.df['Image name'][ii])
                self.imageIndex.append(ii)
                
#        print(self.imageIndex)
                
        # Open the first image and save the image size
        imageName = self.df['Image name'][self.imageIndex[0]]
        
        image_a = cv2.imread(os.path.join(self.path,self.image_dict[imageName],imageName))
        
      
        self.imH, self.imW, *rest = np.shape(image_a)
                
            
    def findOrgDims(self, circle=0):
        # Finds the maximum dimensions of the organism 
        saveFile = 'orgDims.pkl'
        
        OrgMajDim = []
        OrgMinDim = []
        OrgDim = []
        overwrite = False
        if(not os.path.exists(os.path.join(self.path,saveFile)) or overwrite):
            
            
            fileList = self.df['Image name'][self.imageIndex[0:10]]
            # Calculate based on 100 images
            for file in fileList:
                
                image = cv2.imread(os.path.join(self.path,self.image_dict[file],file))
                
                
                orgContour = self.colorThreshold(image = image)
                
                if(orgContour is not None):
                
                    if(circle):
                        (x_center,y_center), Radius = cv2.minEnclosingCircle(orgContour)
                        center = (int(x_center), int(y_center))
                        plt.figure(1)
                        plt.clf()
                        cv2.circle(image,center, int(Radius),(0,255,0),2)
                        plt.imshow(image)
                        plt.pause(0.001)
                        plt.show(block=True)
                        
                        OrgMajDim.append(self.mmPerPixel*2*Radius)
                        OrgMinDim.append(self.mmPerPixel*2*Radius)
                        
                        OrgDim.append(self.mmPerPixel*(2*Radius))
                    else:
                        try:
                            ellipse = cv2.fitEllipse(orgContour)
                            OrgMajDim.append(self.mmPerPixel*ellipse[1][0])
                            OrgMinDim.append(self.mmPerPixel*ellipse[1][1])
                            OrgDim.append(self.mmPerPixel*(ellipse[1][1] + ellipse[1][0])/float(2))
                            
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
            
            with open(os.path.join(self.path,saveFile), 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((OrgDim_mean, OrgMajDim_mean, OrgMinDim_mean), f)
                
        else:
            with open(os.path.join(self.path,saveFile), 'rb') as f:
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
        self.Vx= np.zeros(self.trackLen)
        self.Vy= np.zeros(self.trackLen)
        self.Vz= np.zeros(self.trackLen)
        self.Vz_objLab = np.zeros(self.trackLen)
        self.Theta_dot = np.zeros(self.trackLen)
        
        for i in range(0,self.trackLen):
            
            if(i==0):
                # Forward difference at the start points
                self.Vx[i] = (self.df[self.Xobj_name][i+1]-self.df[self.Xobj_name][i])/(self.df['Time'][i+1]-self.df['Time'][i])
                self.Vy[i] = (self.df[self.Yobj_name][i+1]-self.df[self.Yobj_name][i])/(self.df['Time'][i+1]-self.df['Time'][i])
                self.Vz[i] = (self.df['ZobjWheel'][i+1]-self.df['ZobjWheel'][i])/(self.df['Time'][i+1]-self.df['Time'][i])
                
                self.Vz_objLab[i] = (self.df[self.Zobj_name][i+1]-self.df[self.Zobj_name][i])/(self.df['Time'][i+1]-self.df['Time'][i])

                self.Theta_dot[i] = (self.df['ThetaWheel'][i+1]-self.df['ThetaWheel'][i])/(self.df['Time'][i+1]-self.df['Time'][i])

            
            elif(i==self.trackLen-1):
                # Backward difference at the end points
                self.Vx[i] = (self.df[self.Xobj_name][i]-self.df[self.Xobj_name][i-1])/(self.df['Time'][i]-self.df['Time'][i-1])
                self.Vy[i] = (self.df[self.Yobj_name][i]-self.df[self.Yobj_name][i-1])/(self.df['Time'][i]-self.df['Time'][i-1])
                self.Vz[i] = (self.df['ZobjWheel'][i]-self.df['ZobjWheel'][i-1])/(self.df['Time'][i]-self.df['Time'][i-1])
                
                self.Vz_objLab[i] = (self.df[self.Zobj_name][i]-self.df[self.Zobj_name][i-1])/(self.df['Time'][i]-self.df['Time'][i-1])

                self.Theta_dot[i] = (self.df['ThetaWheel'][i]-self.df['ThetaWheel'][i-1])/(self.df['Time'][i]-self.df['Time'][i-1])

                
            else:
                # Central difference for all other points
                self.Vx[i] = (self.df[self.Xobj_name][i+1]-self.df[self.Xobj_name][i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])
                self.Vy[i] = (self.df[self.Yobj_name][i+1]-self.df[self.Yobj_name][i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])
                self.Vz[i] = (self.df['ZobjWheel'][i+1]-self.df['ZobjWheel'][i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])
                
                self.Vz_objLab[i] = (self.df[self.Zobj_name][i+1]-self.df[self.Zobj_name][i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])

                self.Theta_dot[i] = (self.df['ThetaWheel'][i+1]-self.df['ThetaWheel'][i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])

#            self.Vx.append((self.Xobj[i+1]-self.Xobj[i])/(self.Time[i+1]-self.Time[i]))
#            self.Vy.append((self.Yobj[i+1]-self.Yobj[i])/(self.Time[i+1]-self.Time[i]))
#            self.Vz.append((self.ZobjWheel[i+1]-self.ZobjWheel[i])/(self.Time[i+1]-self.Time[i])) 
            
    
        self.Vx= self.smoothSignal(self.Vx, window_time = self.window_time)
        self.Vy= self.smoothSignal(self.Vy, window_time = self.window_time)
        self.Vz= self.smoothSignal(self.Vz, window_time = self.window_time)
        
        self.Vz_objLab = self.smoothSignal(self.Vz_objLab, window_time = self.window_time)
        
        self.Theta_dot= self.smoothSignal(self.Theta_dot, window_time = self.window_time)

        
        
        
#        self.Vx, self.Vy, self.Vz = self.smoothVelocity(self.window_time)
        
        self.Speed = (self.Vx**2 + self.Vy**2 + self.Vz**2)**(1/2)
        
        self.Speed_z = (self.Vz**2)**(1/2)
        
    
    def computeAccln(self):
        
        self.Theta_ddot = np.zeros(self.trackLen)
        
        self.a_z = np.zeros(self.trackLen)
        
        for i in range(0,self.trackLen):
            
            if(i==0):
                # Forward difference at the start points
                
                self.a_z[i] = (self.Vz[i+1]-self.Vz[i])/(self.df['Time'][i+1]-self.df['Time'][i])
                self.Theta_ddot[i] = (self.Theta_dot[i+1]-self.Theta_dot[i])/(self.df['Time'][i+1]-self.df['Time'][i])

            
            elif(i==self.trackLen-1):
                # Backward difference at the end points
                self.a_z[i] = (self.Vz[i]-self.Vz[i-1])/(self.df['Time'][i]-self.df['Time'][i-1])
                self.Theta_ddot[i] = (self.Theta_dot[i]-self.Theta_dot[i-1])/(self.df['Time'][i]-self.df['Time'][i-1])
            else:
                # Central difference for all other points
                self.a_z[i] = (self.Vz[i+1]-self.Vz[i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])
                self.Theta_ddot[i] = (self.Theta_dot[i+1]-self.Theta_dot[i-1])/(self.df['Time'][i+1]-self.df['Time'][i-1])
    
        self.a_z = self.smoothSignal(self.a_z, self.window_time)
        self.Theta_ddot = self.smoothSignal(self.Theta_ddot, self.window_time)


        
        
        
    def computeDisplacement(self, x_data = None, y_data = None):
        # Compute the displacement by integrating a velocity time series.
        
        disp = scipy.integrate.cumtrapz(y = y_data, x = x_data)
        
        return disp
#        self.disp_z_computed = scipy.integrate.cumtrapz(y = self.Vz, x = self.df['Time'])
        
        

    def computeFluidVelocity(self, image_a, image_b, deltaT = 1, overwrite = False, masking = False, scaleFactor = 4):
        # Computes the mean fluid velocity, far away from objects, given a pair of images
                
    
        

        #--------------------------------------------------------------------------
        # Perform the PIV computation
        #--------------------------------------------------------------------------
        saveFile = os.path.join(self.PIVfolder,'PIV_' + image_a[:-4]+'.pkl')
        
        
        if(not os.path.exists(saveFile) or overwrite):
            #--------------------------------------------------------------------------
            # Load the frame-pair into memory
            #--------------------------------------------------------------------------
            frame_a_color = cv2.imread(os.path.join(self.path, self.image_dict[image_a], image_a))
            frame_b_color = cv2.imread(os.path.join(self.path, self.image_dict[image_b], image_b))
#            frame_a_gs = cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2GRAY)

            print('-'*50)
            print('Analyzing Frame pairs: {} and {} \n'.format(image_a,image_b))
            print('-'*50)
            x,y,u,v, sig2noise = PIV_Functions.doPIV(frame_a_color,frame_b_color, dT = deltaT, win_size = self.window_size, overlap = self.overlap, searchArea = self.searchArea)
            
            u, v = PIV_Functions.pivPostProcess(u,v,sig2noise, sig2noise_min=1.5, smoothing_param = 0)
            
            
            u,v = (PIV_Functions.data2RealUnits(data = u,scale = 1/(self.pixelPermm)), PIV_Functions.data2RealUnits(data = v,scale = 1/(self.pixelPermm)))
            

            #--------------------------------------------------------------------------
            # Threshold the image to extract the object regions
            #--------------------------------------------------------------------------
            if(masking):
                Contours = PIV_Functions.findContours(frame_a_color,self.threshLow,self.threshHigh,'largest')
            else:
                Contours = np.nan
                
#            PIV_Functions.plotPIVdata(frame_a_gs,x,y,u,v, orgContour=Contours)

            
            
            with open(saveFile, 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((x, y , u, v, Contours), f)
            
        else:
            #--------------------------------------------------------------------------
            # Read the PIV data 
            #--------------------------------------------------------------------------
            print('-'*50)
            print('Loading: {} and {} \n'.format(image_a,image_b))
            print('-'*50)
            pklFile = saveFile
            x,y,u,v,Contours = PIV_Functions.readPIVdata(pklFile)
           
        
        
        
        
        
#        Centroids = PIV_Functions.findCentroids(Contours)
        
       
        
#        plt.figure()
#        plt.imshow(maskInsideCircle)
#        plt.show()
        
#        cv2.circle(frame_a_gs,(int(x_cent), int(y_cent)),int(scale_factor*radius), color = (0,255,0))
#        cv2.imshow('frame',frame_a_gs)
#        cv2.waitKey(1)
        
       

        
        
        
        
        if(masking is True):    
#            Contours = PIV_Functions.findContours(frame_a_color,self.threshLow,self.threshHigh,'largest')

            
#            cv2.drawContours(frame_a_color, [Contours],0,(0,255,0),3)
#            cv2.imshow('frame',frame_a_color)
#            cv2.waitKey(1)
            if(Contours is not None):
                x_cent, y_cent, radius = PIV_Functions.findCircularContour(Contours)
                maskInsideCircle = PIV_Functions.pointInCircle(x,y,x_cent,y_cent,scaleFactor*radius)
                u_farfield, v_farfield = (u[~maskInsideCircle], v[~maskInsideCircle])
            else:
                 u_farfield, v_farfield = (u, v)
            
#            plt.figure(1)
#            plt.cla()
#            plt.scatter(x[maskInsideCircle],y[maskInsideCircle],10,'r')
#            plt.scatter(x[~maskInsideCircle],y[~maskInsideCircle],10,'b')
#            plt.pause(0.001)
#            plt.show()
        else:
            u_farfield, v_farfield = (u, v)
            
            
        
        # Find the mean velocity
        u_avg, v_avg = (np.nanmean(u_farfield), np.nanmean(v_farfield))
        u_std, v_std = (np.nanstd(u_farfield), np.nanstd(v_farfield))
        
        
        return u_avg, v_avg, u_std, v_std
 
      
    def FluidVelTimeSeries(self, overwrite = False):
        # Computes the Fluid velocity at each time point during which an image is available and stores the result.
        # For each pair of time-points with images:
        # Generate a mask for each image as necessary
        # Do PIV on the pair of images
        # Calculate the average velocity of the fluid in regions far from the object
        # Store the average velocity as a finction of time
        
        saveFile = 'fluidVelocityTimeSeries.pkl'
        
        savePath = os.path.join(self.path, saveFile)
        
        
        
        if(not os.path.exists(savePath) or overwrite):
        
            nImages = len(self.imageIndex)
#            nImages = 100
            
            n = min(nImages, len(self.imageIndex)-1)
            
            self.u_avg_array = np.zeros(n)
            self.v_avg_array = np.zeros(n)
            self.u_std_array = np.zeros(n)
            self.v_std_array = np.zeros(n)
            self.imageIndex_array = np.zeros(n, dtype='int')
            
            
            for ii in range(n):
                
               
                    
                imageindex_a = self.imageIndex[ii] 
                imageindex_b = self.imageIndex[ii + 1]
                
                image_a = self.df['Image name'][imageindex_a]
                image_b = self.df['Image name'][imageindex_b]
                
                
                # First check if both these images exist in memory
                try:
                    image_a_exists = os.path.exists(os.path.join(self.path, self.image_dict[image_a], image_a))
                except:
                    image_a_exists = False
                try:
                    image_b_exists = os.path.exists(os.path.join(self.path, self.image_dict[image_b], image_b))
                except:
                    image_b_exists = False
                                
                image_a_num = int(image_a[4:-4])
                image_b_num = int(image_b[4:-4])
                
                frame_gap = image_b_num - image_a_num
                
                print(frame_gap)
                
                
                
                if(image_a_exists and image_b_exists and frame_gap == 1):
                    print('Consequtive images found ...')
                
                    print(image_a)
                    print(image_b)
                    
                    dT = self.df['Time'][imageindex_b] - self.df['Time'][imageindex_a]
                    
                    self.u_avg_array[ii], self.v_avg_array[ii], self.u_std_array[ii], self.v_std_array[ii] = self.computeFluidVelocity(image_a,image_b,deltaT = dT, masking = True, scaleFactor=7, overwrite = False)
                    self.imageIndex_array[ii] = imageindex_a
                    
                # If either of those images do not exist, assume that the velocity remains constant over the missing frames
                elif(not image_a_exists or not image_b_exists):
                    print('One or more of image pair not found...')
                    print('Checking for next image index...')
                    self.u_avg_array[ii], self.v_avg_array[ii], self.u_std_array[ii], self.v_std_array[ii] = self.u_avg_array[ii-1], self.v_avg_array[ii-1], self.u_std_array[ii-1], self.v_std_array[ii-1] 
                    self.imageIndex_array[ii] = imageindex_a
                    continue
               
                
                
               
            
            
            self.u_avg_array, self.v_avg_array = (self.smoothSignal(self.u_avg_array, self.window_time),self.smoothSignal(self.v_avg_array, self.window_time))
            
            with open(savePath, 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump((self.imageIndex_array, self.u_avg_array, self.v_avg_array, self.u_std_array, self.v_std_array), f)
                
            
        else:
            with open(savePath, 'rb') as f:  # Python 3: open(..., 'wb')
                    self.imageIndex_array, self.u_avg_array, self.v_avg_array, self.u_std_array, self.v_std_array = pickle.load(f)
                
                
    def setColorThresholds(self):
        
        saveFile = 'colorThresholds.pkl'

        image_a = None
        
        imageName = self.df['Image name'][self.imageIndex[0]]
        
        image_a = cv2.imread(os.path.join(self.path,self.image_dict[imageName],imageName))
        
      
        self.imH, self.imW, *rest = np.shape(image_a)
    
            
        
        print('Image Width: {} px \n Image Height: {} px'.format(self.imW, self.imH))
        
        if(not os.path.exists(os.path.join(self.path, saveFile))):
            
#            print(os.path.join(self.path, self.image_dict[imageName],imageName))
#            v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = rangeslider_functions.getColorThreshold(os.path.join(self.path,self.image_dict[imageName],imageName))
#            threshLow = (v1_min,v2_min,v3_min)
#            threshHigh = (v1_max,v2_max,v3_max)
            
            threshLow = [0,0,95]
            threshHigh = [255, 255, 255] 
            
            with open(os.path.join(self.path,saveFile), 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((threshLow, threshHigh), f)
        else:
            print('Color thresholds available! \n Loading file {} ...'.format(os.path.join(self.root,saveFile)))
            with open(os.path.join(self.path,saveFile), 'rb') as f:
                threshLow, threshHigh = pickle.load(f)
        
           
        self.threshLow = threshLow
        self.threshHigh = threshHigh
        
        
        
        print('Color thresholds for segmentation: \n LOW: {}, HIGH : {}'.format(self.threshLow, self.threshHigh))
    #--------------------------------------------------------------------------       
    # Signal Processing Functions
    #--------------------------------------------------------------------------       
    def smoothSignal(self, data, window_time):      # Window is given in seconds
            
            avgWindow = int(window_time*self.samplingFreq)
            
    #        if(pd.__version__ is not '0.20.3'):
    #            return data.rolling(avgWindow).mean()
    #        else:
            return pd.rolling_mean(data, avgWindow, min_periods = 1, center = True)
        
        
    def correctedDispVelocity(self, overwrite_flag = False):
        
        
        self.FluidVelTimeSeries(overwrite = overwrite_flag)
        
        # Vz is the object velocity relative to the stage V_objStage
        
        V_stageLab = -self.Vz[self.imageIndex_array] + self.Vz_objLab[self.imageIndex_array]
        
        
        
        V_fluidStage = self.v_avg_array - V_stageLab
        
        self.V_objFluid = self.Vz[self.imageIndex_array] - V_fluidStage
        
        self.V_objFluid[np.isnan(self.V_objFluid)]=0
        
        self.corrected_disp =  self.computeDisplacement(x_data = self.df['Time'][self.imageIndex_array], y_data = self.V_objFluid)
        
        
        
        
    

#path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'
#file = 'track_mod.csv'

#path = '/Volumes/GRAVMACH1/StartupFlowMeasurement/Accln_100Steps_s2_1_16Steps/6'

#path = '/Volumes/GRAVMACH1/StartupFlowMeasurement/Accln_1000Steps_s2_1_16Steps/1'
            
# Star Diatom
            
#path = '/Volumes/DEEPAK-SSD/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_07/diatom_star'


# Centric diatom

path = '/Volumes/DEEPAK-SSD 1/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_06/Tow_1/Centric_diatom_3_Good'


# Noctiluca
#path = '/Volumes/GRAVMACH1 1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca/Noctilica7'
        
        
# Pyrocystic Noctiluca
#path = '/Volumes/DEEPAK-SSD/Pyro_Division_Tracks/1130div'

Tmin = 0
Tmax = 2700

track = gravMachineTrack(path, Tmin, Tmax)

overwrite_flag = False

#imageIndex_array, u_avg_array, v_avg_array, u_std_array, v_std_array = track.FluidVelTimeSeries(overwrite = overwrite_flag)


track.correctedDispVelocity(overwrite_flag)

# Create a new data frame with the corrected velocity and displacements and save it to file

#orgname = 'Star diatom'
#dataLen = len(track.imageIndex_array)
#df_corrected = pd.DataFrame({'Organism':np.repeat(orgname, dataLen,axis=0),'OrgSize':np.repeat(track.OrgDim, dataLen,axis=0),'TrackName':np.repeat(track.Organism, dataLen,axis=0),'Condition':np.repeat('No light', dataLen,axis=0),'VelocityX_noWall':track.Vx[track.imageIndex_array],'VelocityY_noWall':track.Vy[track.imageIndex_array],'VelocityZ_noWall':track.V_objFluid})
##
##
#saveFile = os.path.join(track.path,orgname+'_velocity_data.csv')
#df_corrected.to_csv(saveFile)



# Plot the Z displacement vs Time
plt.figure()
plt.plot(track.df['Time'],track.df['ZobjWheel'], color = 'b')
plt.xlim(0,np.max(track.df['Time']))
plt.ylim(np.min(track.df['ZobjWheel']),np.max(track.df['ZobjWheel']))
plt.show()


# Plot of Z velocity of stage 
plt.figure()
plt.plot(track.df['Time'],track.Vz, color = 'b')
plt.title('Stage velocity V_z')

plt.show()

# Plot of Z velocity of stage vs Z velocity of fluid
plt.figure()
plt.plot(track.df['Time'][track.imageIndex_array],track.Vz[track.imageIndex_array], color = 'b')
errorfill(track.df['Time'][track.imageIndex_array], track.v_avg_array,yerr=track.v_std_array, color = 'r')
plt.title('Stage velocity vs Fluid velocity(rad/s)')

plt.show(block=False)
#
#
#
#
# Comparison of original and corrected velocity
plt.figure()
#plt.plot(track.df['Time'],track.Vz, color = 'b', label = 'Velocity of object rel to stage')
plt.plot(track.df['Time'][track.imageIndex_array],track.V_objFluid, color = 'darkblue',linestyle='--',linewidth=2, label = 'Velocity of object rel to fluid')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (z) mm/s')
plt.legend()
plt.show(block=False)
#
#
# Comparison of original and corrected displacement
plt.figure()
#plt.plot(track.df['Time'],track.df['ZobjWheel'], color = 'b', label = 'Original displacement')
plt.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp, color = 'b',linewidth=2, label = 'Corrected displacement', linestyle='-')

plt.xlabel('Time (s)')
plt.ylabel('Displacement (z) mm')
#plt.legend()
plt.show(block=False)




#------------------------------------------------------------------------------------
# Plot the corrected displacements, velocities and cell sizes with a common Time axis
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Load the cell size data
#------------------------------------------------------------------------------
#path1 = '/Volumes/DEEPAK-SSD/Pyro_Division_Tracks/1121'  # cell 2 tracked over long time
#
#path2 = '/Volumes/DEEPAK-SSD/Pyro_Division_Tracks/1130div' # cell 1 tracked over long times
#
#file1 = '1121_cell_division_data_Full_v3.csv'
#file2 = '1130div_cell_division_data_Full_v3.csv'
#trackData1 = pd.read_csv(os.path.join(path1, file1))
#
#trackData2 = pd.read_csv(os.path.join(path2, file2))
#
#
#
## 1121
#Time_2 = trackData1.loc[trackData1['Cell number']==2,'Time'] 
#Area_2 = trackData1.loc[trackData1['Cell number']==2,'Area']
#Area_21 = trackData1.loc[trackData1['Cell number']==1,'Area']
#Time_21 = trackData1.loc[trackData1['Cell number']==1,'Time']
#
## 1130
#Time_1 = trackData2.loc[trackData2['Cell number']==1,'Time']
#Area_1 = trackData2.loc[trackData2['Cell number']==1,'Area']
#Area_12 = trackData2.loc[trackData2['Cell number']==2,'Area']
#Time_12 = trackData2.loc[trackData2['Cell number']==2,'Time']
#
#
#T_split2 = 6750+1357 # 1121
#T_split1 = 6750 #1130
#Time_2 = Time_2 - T_split2
#Time_21 = Time_21 - T_split2
#Time_1 = Time_1 - T_split1
#Time_12 = Time_12 - T_split1
##
##Area_dim = Area*(1/314)**2
#
##Radius = (Area_dim/np.pi)**(1/2)        # Radius in mm
#
##cmap = cmocean.cm.matter
#cmap = plt.get_cmap('Paired')
#
#color = cmap(np.linspace(0,1,4))
#
## Plot of area in pixels
#plt.figure()
#
##plt.plot(Time_12, Area_12, color = color[0],label = 'Track 1, Cell 2', alpha = 0.8,linewidth=3)
#plt.plot(Time_1, Area_1, color = color[1],label = 'Track 1, Cell 1',alpha = 0.8,linewidth=3)
#plt.plot(Time_21, Area_21, color = color[2],label = 'Track 2, Cell 1',alpha = 0.8,linewidth=3)
#plt.plot(Time_2, Area_2, color = color[3],label = 'Track 2, Cell 2',alpha = 0.8,linewidth=3)
#plt.xlabel('Time (s)')
#plt.ylabel('Area (px^2)')
#plt.legend()
##plt.xlim(230,830)
#plt.ylim(500,1750)
#
#plt.show()
#
#
## Plot of Cell radius in um
#
#Area2Radius = 1000*(1/np.pi)**(1/2)*(1/314)
#
#Radius_1 = (Area_1)**(1/2)*Area2Radius
#Radius_2 = (Area_2)**(1/2)*Area2Radius
#Radius_21 = (Area_21)**(1/2)*Area2Radius
#Radius_12 = (Area_12)**(1/2)*Area2Radius
#
#Radius_1 = pd.rolling_mean(Radius_1,30,center=True)
#Radius_2 = pd.rolling_mean(Radius_2,30,center=True)
#Radius_12 = pd.rolling_mean(Radius_12,30,center=True)
#Radius_21 = pd.rolling_mean(Radius_21,30,center=True)
##------------------------------------------------------------------------------
#track.V_objFluid = abs(track.V_objFluid)
#V_objFluid_smooth = pd.rolling_mean(track.V_objFluid,30,center=True)
#
#fig, (ax0,ax1, ax2) = plt.subplots(figsize=(8,12),nrows=3,ncols=1,sharex=True)
#
## Plot of vertical displacement vs time
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp, color = 'b', label = 'Corrected displacement', linestyle='-', linewidth=2)
#ax0.vlines(292,np.min(track.corrected_disp),np.max(track.corrected_disp),'r',linestyle='--')
#ax0.set_ylim(np.min(track.corrected_disp), np.max(track.corrected_disp))
#
##ax0.set_ylabel('Displacement (z) mm')
#
## Plot of vertical velocity vs time
#ax1.plot(track.df['Time'][track.imageIndex_array],track.V_objFluid, color = 'darkblue', label = 'Corrected displacement', linestyle='-', linewidth=2, alpha =0.5)
#ax1.plot(track.df['Time'][track.imageIndex_array],V_objFluid_smooth, color = 'k', label = 'Corrected displacement', linestyle='-', linewidth=2)
#ax1.vlines(292,np.min(track.V_objFluid),np.max(track.V_objFluid),'r',linestyle='--')
##ax1.set_ylabel('Sedimentation speed mm/s')
#ax1.set_ylim(np.min(track.V_objFluid), 0.12)
#
## Plot of Cell size vs time
#ax2.plot(Time_1, 2*Radius_1, color = color[0],label = 'Track 1, Cell 1',alpha = 1,linewidth=2, zorder=1, linestyle=':')
#ax2.plot(Time_12, 2*Radius_12 , color = color[2],label = 'Track 1, Cell 2', alpha = 1,linewidth=2,zorder=20,linestyle='--')
#ax2.plot(Time_21, 2*Radius_21, color = color[1],label = 'Track 2, Cell 1',alpha = 1,linewidth=2,zorder=10,linestyle='-')
#ax2.plot(Time_2, 2*Radius_2, color = color[3],label = 'Track 2, Cell 2',alpha = 1,linewidth=2,zorder=4,linestyle='-.')
#ax2.set_xlabel('Time (s)')
##ax2.set_ylabel('Cell diameter (um)')
#ax2.set_yticks([75, 100, 125, 150])
#ax2.vlines(292,70,150,'r',linestyle='--')
#ax2.set_ylim(70,150)
#
#ax2.set_xlim(0,1000)
#
#ax2.legend(fontsize=10, loc =4)
#
#ratio = 0.35
#for ax in [ax0, ax1, ax2]:
#    xmin, xmax = ax.get_xlim()
#    ymin, ymax = ax.get_ylim()
#    print((xmax-xmin)/(ymax-ymin))
#    ax.set_aspect(abs((xmax-xmin)/(ymax-ymin))*ratio, adjustable='box-forced')
#
#plt.show(block=False)
##
#
# Detect the changes in the sinking speeds and highlight them on the plot

# Fit a linear fit to the vertical displacement

p = np.polyfit(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp, deg=1)

linearFit = track.df['Time'][track.imageIndex_array[:-1]]*p[0]+p[1]

#disp_smoothed = pd.rolling_mean(track.corrected_disp, window=500)

fig, ax0 = plt.subplots()

ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp, color = 'b', label = 'Corrected displacement', linestyle='-', linewidth=2)
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],linearFit, color = 'r', label = 'Linear fit', linestyle='-', linewidth=2)
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],disp_smoothed, color = 'r', label = 'Rolling mean', linestyle='-', linewidth=2)

ax0.set_ylabel('Displacement (z) mm')

plt.show()

Residue = track.corrected_disp - linearFit

Time_loc = track.df['Time'][track.imageIndex_array[:-1]]

fig, ax0 = plt.subplots()

ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],Residue, color = 'b', label = 'Residual', linestyle='-', linewidth=2)
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp - disp_smoothed, color = 'b', label = 'Residual', linestyle='-', linewidth=2)

ax0.set_ylabel('Displacement (z) mm')

plt.show()


Residue = pd.rolling_mean(Residue, window=10)


# Pickle the peak locations for future use

saveFile = 'peak_locs.pkl'

overwrite = False

if(not os.path.exists(os.path.join(path, saveFile)) or overwrite == True):
    

    # Detect the peaks in the Residual time series
    peaks= scipy.signal.find_peaks(Residue, distance=None,width=None,prominence=(0.1,20))
    
    peaks = peaks[0]
    
    peaks_neg= scipy.signal.find_peaks(-Residue, distance=None,width=1,prominence=(0.1,20))
    
    peaks_neg = peaks_neg[0]
    
    peak_indicator = []
    peak_neg_indicator = []
       
    for j in peaks:
        peak_indicator.append(j)
        
    for j in peaks_neg:
        peak_neg_indicator.append(j)
        
    missingPeakloc = 78152
    
    Time_index = Time_loc.keys()
    
#    Time_index = track.df['Time'].keys()
    
    index = int(np.squeeze(np.where(Time_index==missingPeakloc)))
    
    print(index)    
    
    peak_neg_indicator.append(index)
    peak_neg_indicator.sort()
    print(len(peak_indicator))
    print(len(peak_neg_indicator))
    
    with open(os.path.join(path,saveFile),'wb') as f:
        pickle.dump((peak_indicator, peak_neg_indicator), f)
        
else:
    
    with open(os.path.join(path, saveFile),'rb') as f:
        peak_indicator, peak_neg_indicator = pickle.load(f)
    


    
    
fig, ax0 = plt.subplots()

ax0.plot(Time_loc, Residue, color = 'b', label = 'Residual', linestyle='-', linewidth=2)
ax0.vlines(Time_loc.iloc[peak_indicator],np.min(Residue), np.max(Residue), color='r')
ax0.vlines(Time_loc.iloc[peak_neg_indicator],np.min(Residue), np.max(Residue), color='g')
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp - disp_smoothed, color = 'b', label = 'Residual', linestyle='-', linewidth=2)

ax0.set_ylabel('Displacement (z) mm')

plt.show()


# Calculate the velocity during slow and fast sinking compute statistics

Time_loc = np.array(Time_loc)
mask = np.zeros(len(track.V_objFluid), dtype='bool')

Blink_durations = []
Blink_intervals = []
for jj in range(0,len(peak_neg_indicator)-1):  

    mask[peak_indicator[jj] : peak_neg_indicator[jj+1]] = 1
    Blink_durations.append(Time_loc[peak_neg_indicator[jj+1]] - Time_loc[peak_indicator[jj]])
    Blink_intervals.append(Time_loc[peak_indicator[jj+1]] - Time_loc[peak_neg_indicator[jj]])


fig, (ax0,ax1) = plt.subplots(figsize=(12,16),nrows=2,sharex=True)

ax0.plot(Time_loc, track.corrected_disp , color = 'b', label = 'Residual', linestyle='-', linewidth=2)

for jj in range(0,len(peak_neg_indicator)-1):
    ax0.fill_between(Time_loc[peak_indicator[jj] : peak_neg_indicator[jj+1]], track.corrected_disp[peak_indicator[jj] : peak_neg_indicator[jj+1]], y2 = np.min(track.corrected_disp), color = 'r', alpha = 0.3)
#ax0.vlines(Time_loc.iloc[peak_indicator],np.min(track.corrected_disp), track.corrected_disp[peak_indicator], color='r')
#ax0.vlines(Time_loc.iloc[peak_neg_indicator],np.min(track.corrected_disp), track.corrected_disp[peak_neg_indicator], color='g')
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp - disp_smoothed, color = 'b', label = 'Residual', linestyle='-', linewidth=2)

ax0.set_ylabel('Displacement (z) mm')
#ax0.set_ylim(np.min(track.corrected_disp), np.max(track.corrected_disp))
ax0.set_ylim(-20,0)

ax1.plot(track.df['Time'][track.imageIndex_array], track.V_objFluid , color = 'darkblue', label = 'Residual', linestyle='-', linewidth=2)

for jj in range(0,len(peak_neg_indicator)-1):
    ax1.fill_between(Time_loc[peak_indicator[jj] : peak_neg_indicator[jj+1]], y1 = np.max(track.V_objFluid), y2 = np.min(track.V_objFluid), color = 'r', alpha = 0.3)
#ax0.vlines(Time_loc.iloc[peak_indicator],np.min(track.corrected_disp), track.corrected_disp[peak_indicator], color='r')
#ax0.vlines(Time_loc.iloc[peak_neg_indicator],np.min(track.corrected_disp), track.corrected_disp[peak_neg_indicator], color='g')
#ax0.plot(track.df['Time'][track.imageIndex_array[:-1]],track.corrected_disp - disp_smoothed, color = 'b', label = 'Residual', linestyle='-', linewidth=2)

ax1.set_ylabel('Velocity (z) mm/s')
#ax1.set_xlim(40, 400)
#ax1.set_ylim(np.min(track.V_objFluid), np.max(track.V_objFluid))


plt.show()
#    
#
## Velocity distribution and statistics
#
Vel_mean = np.nanmean(track.V_objFluid)
Vel_std = np.nanstd(track.V_objFluid)

#Vel_mean = np.nanmean(track.Vz)
#Vel_std = np.nanstd(track.Vz)


plt.figure(figsize=(4.5,4))
ax0 = sns.distplot(track.V_objFluid[~np.isnan(track.V_objFluid)],  kde = True , color = 'b', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})
#ax0 = sns.distplot(track.Vz,  kde = True , color = 'b', norm_hist = True, hist_kws={"histtype": "bar","edgecolor":'w', "linewidth": 0.2, "alpha": 0.5, "label":'Vz'})



V_fast_mean = np.nanmean(track.V_objFluid[mask])
    
V_fast_std = np.nanstd(track.V_objFluid[mask])

V_slow_mean = np.nanmean(track.V_objFluid[~mask])
    
V_slow_std = np.nanstd(track.V_objFluid[~mask])


mean_blink_durations = np.nanmean(Blink_durations)

std_blink_durations = np.nanstd(Blink_durations)

mean_blink_intervals = np.nanmean(Blink_intervals)

std_blink_intervals = np.nanstd(Blink_intervals)

    

# Align the vertical velocity traces at the transition points to observe the mean behavior
T_len = 200


slow_fast = pd.DataFrame({'Time':[], 'Transition type':[],'Vertical velocity':[]})
fast_slow = pd.DataFrame({'Time':[], 'Transition type':[],'Vertical velocity':[]})

halfSize = int(T_len/2)


Time_loc_interp = np.linspace(Time_loc[0], Time_loc[-1],len(Time_loc))

func_V = interpolate.interp1d(Time_loc, track.V_objFluid[:-1], kind = 'linear')

V_fluid_interp = func_V(Time_loc_interp)

plt.figure()

for index in peak_indicator:
    
#    if(index - halfSize > 0 and index + halfSize < len(Time_loc)):
        
    T_aligned = Time_loc_interp[index - halfSize : index + halfSize] - Time_loc_interp[index]
    V_aligned = V_fluid_interp[index - halfSize : index + halfSize]
    
    transition_type = np.repeat(['Slow-fast'],len(T_aligned))
    
    slow_fast = slow_fast.append(pd.DataFrame({'Time':T_aligned, 'Transition type':transition_type, 'Vertical velocity':V_aligned}))
      
    plt.scatter(T_aligned, V_aligned,20, alpha = 0.5)
    

plt.show()
        
plt.figure()
for index in peak_neg_indicator:
    
#    if(index - halfSize > 0 and index + halfSize < len(Time_loc)):
        
    T_aligned = Time_loc_interp[index - halfSize : index + halfSize] - Time_loc_interp[index]
    V_aligned = V_fluid_interp[index - halfSize : index + halfSize]
    
    transition_type = np.repeat(['Fast-slow'],len(T_aligned))
    
    fast_slow = fast_slow.append(pd.DataFrame({'Time':T_aligned, 'Transition type':transition_type, 'Vertical velocity':V_aligned}))
      
    plt.scatter(T_aligned, V_aligned,20, alpha = 0.5)
    
    
plt.show()

        
        
        
# Plot the aligned velocity traces
        
plt.figure()
sns.lineplot(x='Time', y = 'Vertical velocity', data = slow_fast)
plt.show()
    
plt.figure()
sns.lineplot(x='Time', y = 'Vertical velocity', data = fast_slow)
plt.show()    

    


#        
#    peak_indicator_neg=[0 for i in range(len(Time))]
#    
#    for j in peaks_neg:
#        peak_indicator_neg[j] = 1
#
#    peak_indicator = np.array(peak_indicator, dtype='bool')
#    peak_indicator_neg = np.array(peak_indicator_neg, dtype='bool')
#    indexArray = np.array([i for i in range(len(Time))],dtype='int')


## Plot the Thetadot vs Time
#plt.figure()
#plt.plot(track.df['Time'],track.Theta_dot, color = 'b')
#plt.title('Angular velocity (rad/s)')
#
#plt.show(block=False)


#Rcenter = 95
#
#plt.figure()
#plt.plot(track.df['Time'][imageIndex_array],-Rcenter*track.Theta_dot[imageIndex_array], color = 'b')
#errorfill(track.df['Time'][imageIndex_array], (u_avg_array**2 + v_avg_array**2)**(1/2),yerr=v_std_array, color = 'r')
#plt.title('Stage velocity vs Fluid velocity (rad/s)')
#
#plt.show(block=False)
#
#
#plt.figure()
#plt.plot(track.df['Time'],track.Theta_ddot, color = 'r',linestyle='--')
#plt.show(block=False)

#plt.figure()
#plt.plot(track.df['Time'],track.df['ZobjWheel'], color = 'k')
#plt.scatter(track.df['Time'][:-1],track.disp_z_computed,10,color='r')
#
#plt.show()

    
