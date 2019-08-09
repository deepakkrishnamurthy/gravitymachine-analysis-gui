#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 23:25:41 2018
General PIV analysis for image pairs
@author: deepak
"""
import openpiv.tools
import openpiv.scaling
import openpiv.process
import numpy as np
import openpiv.validation
import openpiv.filters
import csv as csv
import openpiv.tools
import openpiv.process
import openpiv.scaling
import openpiv.validation
import openpiv.filters
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
import scipy.ndimage as ndimage
from roipoly import roipoly
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import pickle
plt.close("all")
from PIL import Image
import imp
import Track
imp.reload(Track)
import FigureParameters
from mpl_toolkits.axes_grid1 import make_axes_locatable
from smoothn import *
from rangeslider_functions import *
from matplotlib.patches import Circle, Wedge, Polygon
#imp.reload(rangeslider_functions)


#==============================================================================
# General Functions
#==============================================================================
def deltaT():
    return 1/33
def mmPerPixel():
    return 1/314   #for a 1440x1080 image
def pixelPermm():
    return 314

def data2RealUnits(data,scale=1.0):
    return data*scale

def smoothData(data,sigma_smooth=1.0,order_=0):
     return ndimage.gaussian_filter(data, sigma= sigma_smooth, order= order_)
 
#==============================================================================
# Find subset of points that lie inside a contour
#==============================================================================
def pointInContour(x,y,contours):
    
    H = np.shape(x)[0]
    W = np.shape(x)[1]
    mask = np.zeros_like(x,dtype='bool')
    for cnts in contours:
        for i in range(0,H):
            for j in range(0,W):
                x_,y_ = (x[i,j],y[i,j])
                dist= cv2.pointPolygonTest(cnts,(x_,y_),False)
                # Create a mask of points which lie inside the contour
                if(dist>=0):
                    mask[i,j]=1
    return mask

#==============================================================================
def velMag(u,v):
    return np.sqrt((u**2+v**2))

def calcVorticity(x,y,u,v):
    
    
    u_copy = u.copy()
    v_copy = v.copy()
    
    u[np.isnan(u)] = 0
    
    v[np.isnan(v)] = 0
    
    
    dx = x[0,1]-x[0,0]
    
    dy = y[1,0] - y[0,0]
    
    u_dy = np.gradient(u, dy, axis = 1)
    
    v_dx = np.gradient(v, dx, axis = 0)
    
    vorticity = v_dx - u_dy
    
    vorticity_smooth = smoothData(vorticity,1.5)
    
    vorticity_smooth[np.isnan(u_copy)] = np.nan
    
    return vorticity_smooth
    
    
    
#==============================================================================
#==============================================================================
# PIV Analysis
#==============================================================================
def doPIV(frame_a_color,frame_b_color, dT = 1.0, _sig2noise_min=1.5, pixel2mm = 1.0, _smoothing_param = 2.0, _win_size = 64, _overlap = 32, _searchArea = 64):
       
    frame_a = cv2.cvtColor(frame_a_color , cv2.COLOR_BGR2GRAY)
    frame_b = cv2.cvtColor(frame_b_color , cv2.COLOR_BGR2GRAY)
    win_size = _win_size
    overlap = _overlap
    searchArea = _searchArea
    u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a.astype(np.int32), frame_b.astype(np.int32), window_size = win_size, overlap = overlap, dt = dT, search_area_size = searchArea, sig2noise_method='peak2peak' )
    
    x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size = win_size, overlap = overlap )

    u,v = pivPostProcess(u,v,sig2noise,sig2noise_min = _sig2noise_min ,smoothing_param = _smoothing_param)
    #x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 100 )
    
   # openpiv.tools.save(x, y, u, v, mask, 'exp1_001.txt' )
   
    #openpiv.tools.display_vector_field('exp1_001.txt', scale=0.01, width=0.0025)
    return x,y,u,v

def pivPostProcess(u,v,sig2noise,sig2noise_min=1.5,smoothing_param=2.0):
    
    u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = sig2noise_min )

    print('-'*50)
    print('Percentage of bad vectors: {} %'.format(100*np.count_nonzero(np.isnan(u))/np.prod(u.shape)))
    print('-'*50)    
    u, v = openpiv.filters.replace_outliers( u, v, method='localmean', max_iter=10, kernel_size=2)
    
#    (u,v) =(np.flipud(u), np.flipud(v))
    
    (u,v)=(smoothData(u,sigma_smooth=1.5), smoothData(v,sigma_smooth=1.5))
    
    return u,v


def plotPIVdata(image,x,y,u,v, orgContour, Centroids = None, figname=1,show = 0,saveFileName=None):
    # Plots the PIV vector field overlaid on the raw image
    imH, imW, *rest = np.shape(image)
    if(orgContour is not None):
        maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
        x, y = (x*mmPerPixel(), y*mmPerPixel())
        u[maskInside] = np.nan
        v[maskInside] = np.nan
    U = velMag(u,v)
    
       
#    U_min = 0
#    U_max = 1.2
    
#    u,v, U = (np.flipud(u), np.flipud(v), np.flipud(U))
    y = np.flipud(y)
    
    Levels = range(0,56,5)
    
    fig = plt.figure(figname,figsize=(4,8))
#    plt.ioff()
    plt.clf()
    ax =plt.gca()
#    for centroids in Centroids:
#        plt.scatter(mmPerPixel()*centroids[0],mmPerPixel()*centroids[1], color = 'g')
        
#    cv2.drawContours(image, orgContour, -1,(0,255,0), 3)
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0,extent = [0,mmPerPixel()*imW,mmPerPixel()*imH, 0])
    ax2 = plt.contourf(x, y, U, levels = Levels, cmap = cmocean.cm.amp, alpha=1.0,linewidth=0,linestyle=None)
    
#    ax2 = plt.contourf(x, y, vorticity, cmap = cmocean.cm.curl, alpha=1.0,linewidth=0,linestyle=None)

    #ax2 = plt.pcolor(x,y,U,cmap = cmocean.cm.amp)
    #ax1 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.solar)
    #ax3 = plt.streamplot(x,y,u,v)
    
#    ax3 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.amp)
#    ax4 = plt.streamplot(x,y,u,-v,color=[1,1,1,0.75],linewidth = 1.2, density = 1.5, arrowsize=0.001)

    ax3 = plt.quiver(x[::5],y[::5],u[::5],v[::5],color=[0,1,0,0.8],scale=400, width =0.005, scale_units='inches',headwidth=4)
#    ax3 = plt.quiver(x,y,u,v,color=[0,0,0,1])

  

    cbar = plt.colorbar(ax2, ticks = Levels)
    plt.clim(0,54)
    
    
    

    cbar.set_label('Flow velocity magnitude (mm/s)')
#    cbar.set_label('Vorticity (1/s)')

    plt.axis('image')
    
    if(saveFile is not None):
        plt.savefig(saveFileName,dpi=300)
#    if(show==1):
    plt.show(block=False)
    plt.pause(0.001)
#    plt.show()
    
def readPIVdata(filename):
    
    with(open(filename,'rb')) as f:
        x, y , u, v, Contours =  pickle.load(f)
    
    return x,y,u,v, Contours
    

#==============================================================================
# Extract the image region corresponding to the organism.
#============================================================================== 
def findCentroids(contours):
    
    Centroids = []
    for ii,cnts in enumerate(contours):
        
        M = cv2.moments(cnts)
                
        ((x, y), radius) = cv2.minEnclosingCircle(cnts)
        
        objCentroid = np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
        
        Centroids.append(objCentroid)
        
    return Centroids
        
    
def findContours(image,thresh_low,thresh_high, SelectContours = 'all'):
    # Find all object contours in an image
    thresh_low = np.array(thresh_low,dtype='uint8')
    thresh_high = np.array(thresh_high,dtype='uint8')
    
    print(thresh_low)
    print(thresh_high)
    
    im_th = cv2.inRange(image, thresh_low, thresh_high)
    
    kernel3 = np.ones((3,3),np.uint8)
    kernel5 = np.ones((5,5),np.uint8)
    kernel7 = np.ones((7,7),np.uint8)
    kernel15 = np.ones((15,15),np.uint8)
    
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel5)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel7)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_OPEN, kernel7)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel15)

    
#    plt.matshow(im_th , cmap=cm.Greys_r )
#    plt.title('Thresholded Image')
#    plt.show()
    
    # Select the largest contour as the final mask
    cnts = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    print('No:of contours:{}'.format(len(cnts)))
    
   
    if(SelectContours =='largest'):
        largestContour = max(cnts, key=cv2.contourArea)
        return largestContour
    elif (SelectContours == 'all'):
        return cnts
    
def setImageThresholds(image):
    
    v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(image)
    thresh_low = (v1_min,v2_min,v3_min)
    thresh_high = (v1_max,v2_max,v3_max)
    
    return thresh_low, thresh_high
    
    
   
#==============================================================================
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx] 
#============================================================================== 

#==============================================================================
def interpolateToGrid(x,y,u,v,scaleFactor=1):
    # Takes a vector field and interpolates it onto a scaleFactor times finer grid
    x_lin = x[0,:]
    y_lin = y[:,0]
            
    f_u = scipy.interpolate.interp2d(x_lin,y_lin,u,kind = 'linear')
    f_v = scipy.interpolate.interp2d(x_lin,y_lin,v, kind = 'linear')
    
    
    dataH = np.shape(x)[0]
    dataW = np.shape(x)[1]
    #--------------------------------------------------------------------------
    # Interpolate to a finer mesh for display purposes
    #--------------------------------------------------------------------------
    x_fine_lin, y_fine_lin = (np.linspace(x.min(),x.max(),2*dataW), np.linspace(y.min(),y.max(),2*dataH))
    
    x_fine, y_fine = np.meshgrid(x_fine_lin, y_fine_lin)
    
    u_fine, v_fine = (f_u(x_fine_lin,y_fine_lin),f_v(x_fine_lin,y_fine_lin))
    
    return x_fine, y_fine, u_fine, v_fine

#def main():
    
imgFormat = ['.png','.svg']
    
dataFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/2017_06_20_PencilLeads/HighSpeedExperiments/Ds17_Processed'

dataFolder = '/Volumes/DEEPAK-SSD/GravityMachine/ControlExperiments_backup/ThermalFlowsCalib/BeforeMixing_Isothermalization/images'

findContours = False

FilesList = os.listdir(dataFolder)

#FilesList.sort()

print(FilesList)

resultRootFolder, *rest = os.path.split(dataFolder)


PIVdataFolder = os.path.join(resultRootFolder,'PIVdata')
resultFolder = os.path.join(resultRootFolder,'VelocityFieldOverlay')

croppedFramesFolder = os.path.join(resultRootFolder,'croppedFrames_bigger')
    
if(not os.path.exists(PIVdataFolder)):
    os.makedirs(PIVdataFolder)
   
if(not os.path.exists(resultFolder)):
    os.makedirs(resultFolder)


if(not os.path.exists(croppedFramesFolder)):
    os.makedirs(croppedFramesFolder)

# Read first image to set thresholds
frame_a_color = cv2.imread(os.path.join(dataFolder,FilesList[0]))

imH,imW, *rest = np.shape(frame_a_color)


#thresh_low, thresh_high = setImageThresholds(frame_a_color)

#print(thresh_low, thresh_high)
thresh_low = [0,0,255]
thresh_high = [255,255,255]
    
imWidth = 360
imHeight = 680

overwrite = True

nImages = 100

try:
    
    step = 1
    
    index = range(0,nImages,step)
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(index)))
    
    counter = 0
    
    for ii in index:
        
        image_a = FilesList[ii]
        image_b = FilesList[ii+1]
        
    
        #--------------------------------------------------------------------------
        # Load the frame-pair into memory
        #--------------------------------------------------------------------------
        frame_a_color = cv2.imread(os.path.join(dataFolder,image_a))
        frame_b_color = cv2.imread(os.path.join(dataFolder,image_b))
        
        
        
        
        #--------------------------------------------------------------------------
        # Perform the PIV computation
        #--------------------------------------------------------------------------
        saveFile = os.path.join(PIVdataFolder,'PIV_' + image_a[-13:-4]+'.pkl')
        
        if(not os.path.exists(saveFile) or overwrite):
            print('-'*50)
            print('Analyzing Frame pairs: {} and {} \n'.format(image_a,image_b))
            print('-'*50)
            x,y,u,v = doPIV(frame_a_color,frame_b_color, dT = deltaT())
            print(imW)
            
            u,v = (data2RealUnits(u,scale = mmPerPixel()), data2RealUnits(v,scale = mmPerPixel()))
        else:
    #            #--------------------------------------------------------------------------
    #            # Read the PIV data 
    #            #--------------------------------------------------------------------------
            print('-'*50)
            print('Loading: {} and {} \n'.format(image_a,image_b))
            print('-'*50)
            pklFile = saveFile
            x,y,u,v,Contours= readPIVdata(pklFile)
           
        #--------------------------------------------------------------------------
        # Threshold the image to extract the object regions
        #--------------------------------------------------------------------------
        if(findContours):
            Contours = findContours(frame_a_color,thresh_low,thresh_high,'all')
        
            Centroids = findCentroids(Contours)
            # Note that to find the mask we need to consider the Up-down flipped matrix of the positions to follow the image convention
            maskInside = pointInContour(np.flipud(x),np.flipud(y),Contours)
            
        else:
            Contours = None
        # Find the mean velocity
        v_avg = np.nanmean(v)
        
        
        frame_a_gs = cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2GRAY)
    
    
        overlayFile1 = os.path.join(resultFolder,image_a[-13:-4]+'_'+imgFormat[0])
        overlayFile2 = os.path.join(resultFolder,image_a[-13:-4]+'_'+imgFormat[1])
        
        plotPIVdata(frame_a_gs, x,y,u,v ,orgContour = Contours, Centroids = Centroids, figname=1,show = 1, saveFileName = overlayFile1)
        plotPIVdata(frame_a_gs, x,y,u,v ,orgContour = Contours, Centroids = Centroids, figname=1,show = 1, saveFileName = overlayFile2)
        
        currColor = (np.array(colors[counter][:-1]*255, dtype='int'))
              
#        mask = pointInContour(x,y,Contours)
        
        print(currColor)
        
    
     
#        if(len(Centroids)<2):
#            break
#        
##        plt.figure(3)
##        plt.imshow(frame_a_gs)
#        for ii,centroids in enumerate(Centroids):
##            plt.scatter(centroids[0],centroids[1], color = 'g')
#            
#            if(ii==0):
#                currFrame_cropped = frame_a_gs[int(centroids[1])-int((3/4)*imHeight):int(centroids[1])+int((1/4)*imHeight), int(centroids[0])-int(imWidth/2):int(centroids[0])+int(imWidth/2)]
#
#        
##        plt.imshow(currFrame_cropped)
#        
#        
#        cv2.imwrite(os.path.join(croppedFramesFolder,image_a[-8:-4]+'.tif'), currFrame_cropped)
        
        
        
        
        
#        cv2.drawContours(frame_a_color, Contours, -1, currColor , 3)
#        plt.contour(Contours)
#        plt.imshow(frame_a_color)
#        plt.pause(0.001)
#        plt.show()
    
        
        counter+=1

        
        
        #--------------------------------------------------------------------------
        # Pickle the raw Data
        #--------------------------------------------------------------------------
    
        
        
        if(not os.path.exists(saveFile)):
            with open(saveFile, 'wb') as f:  # Python 3: open(..., 'wb')
                pickle.dump((x, y , u, v, Contours), f)
    
    #    
    
except KeyboardInterrupt:
    pass
    
    
#if __name__ == '__main__':
#    main()
#    cv2.destroyAllWindows()
    