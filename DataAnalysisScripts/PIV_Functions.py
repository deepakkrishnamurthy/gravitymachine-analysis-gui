#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:30:03 2019
# PIV Functions

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
import smoothn
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
#==============================================================================
# General Funtions
#==============================================================================
def data2RealUnits(data = None,scale=1.0):
    return data*scale

def smoothData(data,sigma_smooth=1.0,order_=0):
     return ndimage.gaussian_filter(data, sigma= sigma_smooth, order= order_)
 
#==============================================================================
# Image Processing Functions
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
        if(len(cnts)>0):
            largestContour = max(cnts, key=cv2.contourArea)
            # Approximate the contour to 1% of its arcLength
            epsilon = 0.001*cv2.arcLength(largestContour,True)
            approxContour = cv2.approxPolyDP(largestContour,epsilon,True)
            return approxContour
        
        else:
            return None
    elif (SelectContours == 'all'):
        return cnts
    
def findCircularContour(Contour):
    
            
    ((x, y), radius) = cv2.minEnclosingCircle(Contour)
    
    return x,y,radius
    
   

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

def pointInCircle(x,y,x_cent,y_cent,radius):
    
    H = np.shape(x)[0]
    W = np.shape(x)[1]
    mask = np.zeros_like(x,dtype='bool')
   
    for i in range(0,H):
        for j in range(0,W):
            x_,y_ = (x[i,j],y[i,j])
            dist= ((x_ - x_cent)**2 + (y_ - y_cent)**2)**(1/2)
            # Create a mask of points which lie inside the contour
            if(dist<radius):
                mask[i,j]=1
    return mask
    

#==============================================================================
# PIV Analysis
#==============================================================================
def doPIV(frame_a_color,frame_b_color, dT = 1.0, win_size = 64, overlap = 32, searchArea = 64):
       
    frame_a = cv2.cvtColor(frame_a_color , cv2.COLOR_BGR2GRAY)
    frame_b = cv2.cvtColor(frame_b_color , cv2.COLOR_BGR2GRAY)

    u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a.astype(np.int32), frame_b.astype(np.int32), window_size = win_size, overlap = overlap, dt = dT, search_area_size = searchArea, sig2noise_method='peak2peak' )
    
    x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size = win_size, overlap = overlap )

    return x,y,u,v, sig2noise

def pivPostProcess(u,v,sig2noise,sig2noise_min=1.5,smoothing_param = 0):
    
    u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = sig2noise_min )

    print('-'*50)
    print('Percentage of bad vectors: {} %'.format(100*np.count_nonzero(np.isnan(u))/np.prod(u.shape)))
    print('-'*50)    
    u, v = openpiv.filters.replace_outliers( u, v, method='localmean', max_iter=10, kernel_size=2)
    
#    (u,v) =(np.flipud(u), np.flipud(v))
    
    if(smoothing_param != 0):
    
        (u,v)=(smoothData(u,sigma_smooth=1.5), smoothData(v,sigma_smooth=1.5))
    
    return u,v


def plotPIVdata(image,x,y,u,v, orgContour = None, Centroids = None, pixelPermm = 1,figname=1,show = 0,saveFileName=None):
    mmPerPixel = 1/pixelPermm
    # Plots the PIV vector field overlaid on the raw image
    imH, imW, *rest = np.shape(image)
    
    
    if(orgContour is not None):
        maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
        u[maskInside] = np.nan
        v[maskInside] = np.nan
        
    x, y = (x*mmPerPixel, y*mmPerPixel)
    
    U = velMag(u,v)
    
    
    y = np.flipud(y)
    
    fig = plt.figure(figname)
    plt.clf()
    ax =plt.gca()

    if(orgContour is not None):        
        cv2.drawContours(image, [orgContour], -1,(255,0,0), 3)
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0,extent = [0,mmPerPixel*imW,mmPerPixel*imH, 0])
    ax2 = plt.contourf(x, y, U, cmap = cmocean.cm.amp, alpha=1.0,linewidth=0,linestyle=None)
#    
    ax3 = plt.quiver(x,y,u,v,color=[0,1,0,0.8])
##    ax3 = plt.quiver(x,y,u,v,color=[0,0,0,1])
#
    cbar = plt.colorbar(ax2)
#
    cbar.set_label('Flow velocity magnitude (mm/s)')
#
    plt.axis('image')
    
    if(saveFileName is not None):
        plt.savefig(saveFileName,dpi=300)
        
    plt.show(block=False)
    plt.pause(0.001)

    
def readPIVdata(filename):
    
    with(open(filename,'rb')) as f:
        x, y , u, v, Contours =  pickle.load(f)
    
    return x,y,u,v, Contours


#==============================================================================
# Derived quantities
#=============================================================================
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
