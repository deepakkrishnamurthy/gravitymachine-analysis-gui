#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 23:57:29 2018
Code to perform a non-linear least-squares fit on 2D PIV data
@author: deepak
Main steps:
    1. Load the raw image
    2. Extract the contour and orientation of the object
    3. Load the PIV dataset
    4. Perform least-squares fit to extract the different coefficients
    5. Plot the raw image super-imposed with different multipole contributions.
"""
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
import rangeslider_functions
import sys
import time
import cv2
from decimal import Decimal
from scipy.optimize import least_squares
import ProgressBar
plt.close("all")

def callback(value):
	pass
# Track bars for selecting the image
def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-c", "--picamera", type=int, default=-1,
    help="whether or not the Raspberry Pi camera should be used")
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter. RGB or HSV')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    args = vars(ap.parse_args())

    if not xor(bool(args['image']), bool(args['webcam'])):
        ap.error("Please specify only one image source")

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please speciy a correct filter.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

def getColorThreshold(image, filterName = 'HSV'):
   
    
    range_filter = filterName.upper()

   
    

    if range_filter == 'RGB':
        frame_to_thresh = image.copy()
    else:
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    

    setup_trackbars(range_filter)

    while True:
        

        if range_filter == 'RGB':
            frame_to_thresh = image.copy()
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)

        key = cv2.waitKey(100) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)
            
    return v1_min, v2_min, v3_min, v1_max, v2_max, v3_max

def colorThreshold(image,thresh_low,thresh_high):
    
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

    
#    plt.matshow (im_th , cmap=cm.Greys_r )
#    plt.show()
    
    # Select the largest contour as the final mask
    cnts = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    print('No:of contours:{}'.format(len(cnts)))
    
   
    largestContour = max(cnts, key=cv2.contourArea)
    
    M = cv2.moments(largestContour)
    
    # Approximate the contour to 1% of its arcLength
    epsilon = 0.01*cv2.arcLength(largestContour,True)
    approxContour = cv2.approxPolyDP(largestContour,epsilon,True)
            
    ((x, y), radius) = cv2.minEnclosingCircle(largestContour)
    
    orgCentroid = np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
    
    cv2.circle(im_th,(orgCentroid[0],orgCentroid[1]),int(4*radius),color=255,thickness=-1)
    
    cnts_circle = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]

    print('No:of contours in circle masked image:{}'.format(len(cnts_circle)))
    
    circleContour = max(cnts_circle, key=cv2.contourArea)
    
    
    
    return im_th, approxContour, circleContour, orgCentroid 


def velMag(u,v):
    return np.sqrt((u**2+v**2))
def unitvector(vector):
    mag = np.inner(vector,vector)**(1/2)
    return vector/mag

def Stokeslet(r, p, r_c, A_st):
# Compute the Stokeslet velocity field due to a Stokeslet of strength A_st and orientation p at location r
    r1 = r - r_c
    R = np.inner(r1,r1)**(1/2)
    r_hat = unitvector(r1)
    p_hat = unitvector(p)

    v = (A_st*(R**-1))*(np.eye(2) + np.tensordot(r_hat,r_hat,axes=0)).dot(p_hat)
    return v

    

def Stresslet(r, p, r_c,  A_str):
    r1 = r - r_c
    R = np.inner(r1,r1)**(1/2)
    r_hat = unitvector(r1)
    p_hat = unitvector(p)
    v = (A_str*(R**-2))*(1 - 3*(np.inner(p_hat, r_hat)**2))*r_hat
    return v
    
def SourceDoublet(r, p, r_c, A_sd):
    r1 = r - r_c
    R = np.inner(r1,r1)**(1/2)
    r_hat = unitvector(r1)
    p_hat = unitvector(p)
    v = (A_sd*(R**-3))*(np.eye(2)/3 - np.tensordot(r_hat,r_hat,axes=0)).dot(p_hat)
    return v
    
def velocityFit(r, p, r_c, U, A_st, A_str, A_sd):
    
    p = np.array(unitvector(p))
    
    v_fit = -U*p - Stokeslet(r, p, r_c, A_st) - Stresslet(r, p, r_c,  A_str) - SourceDoublet(r, p, r_c,  A_sd)
    
    return v_fit
 
def velocityFit_1(r, p, r_c, U, A_st, A_str, A_sd):
    
    U = np.array(U)
    p = np.array(unitvector(p))
    
    v_fit = -U - Stokeslet(r, p, r_c, A_st) - Stresslet(r, p, r_c,  A_str) - SourceDoublet(r, p, r_c,  A_sd)
    
    return v_fit
def computeFittedVelocity(x_exp,y_exp, p, r_c, U, A_st, A_str, A_sd):
    
    u_fit, v_fit = (np.zeros_like(x_exp), np.zeros_like(x_exp))
    x_fit, y_fit = (np.zeros_like(x_exp), np.zeros_like(x_exp))
    p = unitvector(p)
    for ii in range(np.shape(x_exp)[0]):
        for jj in range(np.shape(x_exp)[1]):
            
            
            r = np.array([x_exp[ii,jj], y_exp[ii,jj]])
            x_fit[ii,jj], y_fit[ii,jj] = r
#            u_fit[ii,jj], v_fit[ii,jj] = velocityFit(r = r, p = p, r_c = r_c, U = U, A_st = A_st, A_str = A_str, A_sd = A_sd)
            u_fit[ii,jj], v_fit[ii,jj] = velocityFit_1(r = r, p = p, r_c = r_c, U = U, A_st = A_st, A_str = A_str, A_sd = A_sd)

      

    return u_fit, v_fit

def readPIVdata(filename):
    with(open(filename,'rb')) as f:
        x, y , u, v, orgContour, circleContour =  pickle.load(f)
    
    return x,y,u,v,orgContour, circleContour

def readVelocityFitData(filename):
    with(open(filename,'rb')) as f:
        p_x, p_y, r_c_x, r_c_y, Ux_0, Uy_0, A_st, A_str, A_sd, relError =  pickle.load(f)
    
    return p_x, p_y, r_c_x, r_c_y, Ux_0, Uy_0, A_st, A_str, A_sd, relError
    
#==============================================================================
# Plotting Functions
#==============================================================================
def plotScalarField(x,y,U, figname = 1):

        
    f = plt.figure(figname)
    f.clf()
    ax1 = plt.contourf(x, y, U)
    cbar = plt.colorbar(ax1)
    cbar.ax.set_ylabel('Magnitude')
    plt.axis('image')
    plt.pause(0.001)
    plt.show()
    
def plotVelocityField(x,y,u,v,figname=1):
    U = velMag(u,v)
        
    f = plt.figure(figname)
    
    ax1 = plt.contourf(x, y, U)
    plt.quiver(x[::2],y[::2],u[::2],v[::2])
#    plt.streamplot(x,y,u,v,color = 'r')
    cbar = plt.colorbar(ax1)
    cbar.ax.set_ylabel('Magnitude')
    plt.axis('image')
    plt.show()
    
def ImageVelocitySupPlot(x,y,u,v, image):
    U = velMag(u,v)
        
    f = plt.figure()
    
    ax1 = plt.contourf(x, y, U)
    plt.quiver(x[::2],y[::2],u[::2],v[::2])
    plt.streamplot(x,y,u,v,color = 'r')
    cbar = plt.colorbar(ax1)
    cbar.ax.set_ylabel('Magnitude')
    plt.axis('image')
    plt.show()
    
def plotPIVdata(image,x,y,u,v, U, orgContour,figname=1,saveFileName='PIVdata.tif'):
    # Plots the PIV vector field overlaid on the raw image
    

    fig = plt.figure(1)
    plt.clf()
     
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0)
    ax2 = plt.contourf(x, y, np.flipud(U), cmap = cmocean.cm.amp, alpha=1.0,linewidth=0,linestyle=None) 
#    ax4 = plt.streamplot(x,y,u,-v,color='blue',linewidth = 1, density = 1.5, arrowsize=0.1)

    ax3 = plt.quiver(x[::2],y[::2],np.flipud(u[::2]),np.flipud(v[::2]),color='k')
#    plt.scatter(x_centroid[0], x_centroid[1])
    cbar = plt.colorbar(ax2)
    cbar.ax.set_ylabel('Flow velocity magnitude (mm/s)')
    plt.xlabel('X')
    plt.ylabel('Z')
    #    cbar.set_label('Speed')
    plt.axis('image')
    plt.pause(0.001)
#    
#    plt.savefig(saveFileName,dpi=300)
#    plt.show(block=False)
    plt.show()
#==============================================================================
# Vector Operations
#==============================================================================
def vectorNorm(vect):
    # Calculates the vector norm of the residual between two vectors when the shape of the vectors is MxN
    vect = np.array(vect) 
    vect_flat = vect.flatten()
    Norm = np.inner(vect_flat, vect_flat)**(1/2)
        
    return Norm
    
def interpolateToGrid(x,y,u,v,scaleFactor=1):
    # Takes a vector field and interpolates it onto a scaleFactor times finer grid
    x_lin = x[0,:]
    y_lin = y[:,0]
            
    f_u = interpolate.interp2d(x_lin,y_lin,u,kind = 'linear')
    f_v = interpolate.interp2d(x_lin,y_lin,v, kind = 'linear')
    
    
    dataH = np.shape(x)[0]
    dataW = np.shape(x)[1]
    #--------------------------------------------------------------------------
    # Interpolate to a finer mesh for display purposes
    #--------------------------------------------------------------------------
    x_fine_lin, y_fine_lin = (np.linspace(x.min(),x.max(),2*dataW), np.linspace(y.min(),y.max(),2*dataH))
    
    x_fine, y_fine = np.meshgrid(x_fine_lin, y_fine_lin)
    
    u_fine, v_fine = (f_u(x_fine_lin,y_fine_lin),f_v(x_fine_lin,y_fine_lin))
    
    return x_fine, y_fine, u_fine, v_fine

#==============================================================================
def mmPerPixel(resolution_width):
    return 1./628/(resolution_width/1440)   #for a 1440x1080 image
#==============================================================================
def pixelPermm(resolution_width):
    return 628*resolution_width/1440
#==============================================================================
# Find centroid of a contour
#==============================================================================
def findCentroid(contour):
    M = cv2.moments(contour)
    return np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
#==============================================================================
# Find subset of points that lie inside a contour
#==============================================================================
def pointInContour(x,y,contour):
    
    H = np.shape(x)[0]
    W = np.shape(x)[1]
    # Note that the mask must respect the corrdinate shift between image and normal coordinates
    mask = np.zeros_like(x,dtype='bool')
    for i in range(0,H):
        for j in range(0,W):
            x_,y_ = (x[i,j],y[i,j])
            dist= cv2.pointPolygonTest(contour,(x_,y_),False)
            # Create a mask of points which lie inside the contour
            if(dist>=0):
                mask[i,j]=1
    return mask
#==============================================================================
def computeVelocityError(fit_params , **kwargs):
    #--------------------------------------------------------------------------
    # Unpack the kwargs
    #--------------------------------------------------------------------------
    if kwargs is not None:
        for key, value in kwargs.items():
            if(key is 'U_exp'):
                U_exp = value
            elif(key is 'V_exp'):
                V_exp = value
            elif(key is 'X_exp'):
                X_exp = value
            elif(key is 'Y_exp'):
                Y_exp = value
            elif(key is 'mask'):
                mask = value
                    
          
#            elif(key is 'P_x'):
#                p_x = value
#            elif(key is 'P_y'):
#                p_y = value
    #--------------------------------------------------------------------------
    # Note that fit parameters is an ND array
    #--------------------------------------------------------------------------
    # Unpack the fit parameters 
    #--------------------------------------------------------------------------
    p_x, p_y, r_c_x, r_c_y, Ux, Uy , A_st, A_str, A_sd = fit_params
   
    p = np.array([p_x, p_y])
    
    p = unitvector(p)
    
    r_c = np.array([r_c_x, r_c_y])
    
    U = [Ux, Uy]
    
#    X_exp = np.flipud(X_exp)
#    Y_exp = np.flipud(Y_exp)
#    U_exp = np.flipud(U_exp)
#    V_exp = np.flipud(V_exp)
        
    U_exp_flat = np.array([U_exp[~mask].flatten(), V_exp[~mask].flatten()]).flatten()
           
    
#    print('Number of vector elements: {}'.format(np.shape(V_exp)[0]*np.shape(V_exp)[1]))
    
    u_fit, v_fit = computeFittedVelocity(x_exp = X_exp, y_exp = Y_exp, p = p,r_c = r_c, U = U, A_st = A_st, A_str = A_str, A_sd = A_sd)
    
    U_fit_flat = np.array([u_fit[~mask].flatten(), v_fit[~mask].flatten()]).flatten()

    
    V_error_flat = U_fit_flat - U_exp_flat
               
#    print('*'*50)
#    print('Relative error: {}: %'.format(100*vectorNorm(V_error_flat)/vectorNorm(U_exp_flat)))
#    print('*'*50)
#    print(fit_params)
   
    return V_error_flat

def testVelocityField(objDia=0.2,r_centroid = [0,0], p=[0,1],U_trans = [0, 0],A_st = 1e-2,A_str = 0,A_sd = 0):
    #==============================================================================
    # Test dataset (generates an artificial velocity field)
    #==============================================================================
    r_centroid = np.array(r_centroid)
    p = np.array(unitvector(p))
    
   
    
    nX = 50
    nY = 50
    
    x_array = np.linspace(-1,1,nX)
    y_array = np.linspace(-1,1,nY)
    
    [X_grid, Y_grid] = np.meshgrid(x_array, y_array)
    
    mask = (X_grid-r_centroid[0])**2 + (Y_grid - r_centroid[1])**2 <= np.pi*objDia**2/4
    
    u, v = (np.zeros_like(X_grid), np.zeros_like(X_grid))
    
    u, v = computeFittedVelocity(X_grid,Y_grid,p = p,r_c = r_centroid, U = U_trans, A_st= A_st, A_str = A_str, A_sd = A_sd)
#    for ii in range(nX):
#        for jj in range(nY):
#            r = [X_grid[ii,jj], Y_grid[ii,jj]]
##            u[ii,jj], v[ii,jj] = -Stokeslet(r, p, r_centroid, A_st)  - Stresslet(r, p, r_centroid, A_str) - SourceDoublet(r, p, r_centroid, A_sd)
#            u[ii,jj], v[ii,jj] = computeFittedVelocity(X_grid,Y_grid,[0,1],[0,0], 0, 1, 0, 0)
#            u[ii,jj], v[ii,jj] = Stresslet(r, p, r_centroid, A_str)
#            u[ii,jj], v[ii,jj] = SourceDoublet(r, p, r_centroid, A_sd)
    
#    u,v = (u + np.random.randn(np.shape(u)[0], np.shape(u)[1]), v + np.random.randn(np.shape(v)[0], np.shape(v)[1]) )
    
    u[mask] = np.nan
    v[mask] = np.nan
    
    return X_grid,Y_grid,u,v, mask
    
    
     

def main():
    
    imgType = ['.png','.svg']
    # Choose test flag as 0 or 1. 1: Generates a test velocity field for code verification.
    testFlag = 0
    
    if testFlag == 1:
        objDia = 0.2
        r_centroid = [0,0]
        U = [0, -1]
        p = [0,1]
        A_st = 1
        A_str = -10
        A_sd = 0
        x_test, y_test , u_test ,v_test, mask = testVelocityField(objDia, r_centroid, p, U, A_st, A_str, A_sd)
        
        
        plotVelocityField(x_test,y_test,u_test,v_test)
       
        
#        #--------------------------------------------------------------------------
#        # Fitting the test velocity field
#        #--------------------------------------------------------------------------
#        # Initial guess values
#        Ux_0 = 0
#        Uy_0 = 1
#        r_c_x, r_c_y = [0, 0]
#        p_x, p_y = [0, 1]
#    
#        A_st = 1e-2
#        A_str = 2e-2
#        A_sd = 3e-2
#        fit_params_0 = [p_x, p_y, r_c_x, r_c_y, Ux_0, Uy_0, A_st, A_str, A_sd] 
#       
#        fit_params_min = [-1, -1, r_c_x - objDia/2,  r_c_y - objDia/2, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf ]
#        fit_params_max = [1, 1,  r_c_x + objDia/2, r_c_y + objDia/2, np.inf, np.inf, np.inf, np.inf, np.inf ]
#                      
#        
#        res_1 = least_squares(computeVelocityError, fit_params_0, bounds = (fit_params_min, fit_params_max), kwargs = {'X_exp':x_test, 'Y_exp':y_test, 'U_exp':u_test, 'V_exp':v_test, 'mask':mask}, max_nfev = 100)
#        p_x_fit, p_y_fit, r_x_fit, r_y_fit, Ux_trans_fit, Uy_trans_fit, A_st_fit, A_str_fit, A_sd_fit = res_1.x 
#        
#        
#        p_x_fit, p_y_fit = unitvector([p_x_fit, p_y_fit])
#        U_trans_fit = [Ux_trans_fit, Uy_trans_fit]
#        print(50*'*')
#        print('centroid location: ({},{}) '.format(r_x_fit, r_y_fit))
#
#        print('Translational velocity: {} mm/s'.format(U_trans_fit))
#        print('Organism orientation vector : ({}, {})'.format(p_x_fit, p_y_fit))
#        print('A_st (Stokeslet): {:.3e} mm^2/s'.format(A_st_fit))
#        print('A_str (Stresslet): {:.3e} mm^3/s'.format(A_str_fit))
#        print('A_sd (Source Doublet): {:.3e} mm^4/s'.format(A_sd_fit))
#        print(50*'*')
#
#        residualVect = res_1.fun
#        
#        print(50*'=')
#        print('Converged in {} iterations with Status {}'.format(res_1.nfev, res_1.status))
#        print(50*'=')
#    
#    
#        # Compute the "Fitted" velocity field
#        u_fit, v_fit = computeFittedVelocity(x_test, y_test, p =[p_x_fit, p_y_fit],r_c = [r_x_fit, r_y_fit], U = U_trans_fit, A_st = A_st_fit, A_str = A_str_fit, A_sd = A_sd_fit)
#        # Find norm of residual vector
#        
#
#        
#        
#        u_fit[mask] = np.NaN
#        v_fit[mask] = np.NaN
#        
#        velErrorMag = velMag(u_fit - u_test, v_fit - v_test)
#        
#        U_exp_mag = velMag(u_test, v_test)
#        
#        plotVelocityField(x_test, y_test, u_fit, v_fit,figname=2)
#     
#        
#        plotScalarField(x_test, y_test, 100*velErrorMag/U_exp_mag, figname=3)
        
    #==============================================================================
    # If not doing the verification, point to an experimental dataset.
    #==============================================================================
    else:
    
    
      
    #==============================================================================
        # Specify the experimental dataset path
        #--------------------------------------------------------------------------
#        Exp_dataPath = '/Volumes/GRAVMACH1 2/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
#        Exp_dataPath = '/Volumes/GRAVMACH1 1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'
        
        #--------------------------------------------------------------------------
        # Starfish
        #--------------------------------------------------------------------------
#        Exp_dataPath = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'
        
    #    data_path = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Seacucumber4_T_744_Registered_GS'
    #    data_path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail2'
        
        #--------------------------------------------------------------------------
        # Dendraster
        Exp_dataPath = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'

#        Exp_dataPath = '/Volumes/GRAVMACH1 2/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail4'
        
        
        # Noctiluca
#        Exp_dataPath  = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca/Noctilica7'

        # Acorn Worm
#        Exp_dataPath = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm4'

        
        imageFolder = 'images'
        
        rootFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/PIV_Results'
    #    dataFolder = 'seacucmber9_Auto_108_110'
#        dataFolder = 'StarFish6highfreq_IMG_17726_18757'
    #    dataFolder = 'snail2_10_15'
#        dataFolder = 'seacucmber9_Auto_IMG_29198_31246'
#        dataFolder = 'Dendraster3_IMG_6480_6502'
#        dataFolder ='Dendraster3_IMG_4329_4377'
#        dataFolder = 'snail4_IMG_11853_12155'
#        dataFolder = 'Noctilica7_IMG_10783_11267'
#        dataFolder = 'AcornWorm3_IMG_5622_5653'
#        dataFolder = 'AcornWorm4_IMG_2679_2826'
#        dataFolder = 'Dendraster3_IMG_4331_4342'
#        dataFolder = 'Dendraster3_IMG_4329_4377'
#        dataFolder = 'Dendraster3_IMG_2391_2497'
#        dataFolder = 'StarFish6_IMG_18322_18348'
        PIVfolder = 'PIVdata'
        
        #--------------------------------------------------------------------------
        # Create a folder to save the fitted velocity field components
        #--------------------------------------------------------------------------
        resultFolder = os.path.join(rootFolder,dataFolder,'VelocityFit')
        if(not os.path.exists(resultFolder)):
            os.makedirs(resultFolder)
            
        labFrameFolder = os.path.join(rootFolder,dataFolder,'labFrame')
        if(not os.path.exists(labFrameFolder)):
            os.makedirs(labFrameFolder)
        
        #--------------------------------------------------------------------------
        # List all PIV data files in the folder
        
        
        for file in os.listdir(os.path.join(rootFolder,dataFolder,PIVfolder)):
            print(file[:-4])
        
        nData = len(os.listdir(os.path.join(rootFolder,dataFolder,PIVfolder)))
        
        x_cent_array = np.zeros((2,nData))
        p_array = np.zeros((2,nData))
        U_array = np.zeros((2,nData))
        A_st_array = np.zeros((nData))
        A_str_array = np.zeros((nData))
        A_sd_array = np.zeros((nData))
        relError_array = np.zeros((nData))
        relError_mag_array = np.zeros((nData))
        indexArray = []
        objDia_array = np.zeros((nData))
        
        #--------------------------------------------------------------------------
          # Whether to compute the fits again even if they exist
        #--------------------------------------------------------------------------
        computeNew = 0
            
#         Read the raw images and PIV data for the image sequence    
            
#        for ii,image_index in enumerate(index_array):
        for ii,file in enumerate(os.listdir(os.path.join(rootFolder,dataFolder,PIVfolder))):
                 
            ProgressBar.update_progress(ii/float(nData))
            #--------------------------------------------------------------------------
            # read the raw image
            #--------------------------------------------------------------------------
            print(25*'=')
            print('Analyzing File: {}'.format(file))
            print(25*'=')
            
            image_index = int(file[8:-4])
            indexArray.append(image_index)
            img_name = 'IMG_'+str(image_index)
            print(os.path.join(Exp_dataPath,imageFolder,img_name+'.tif'))
            frame_color = cv2.imread(os.path.join(Exp_dataPath,imageFolder,img_name+'.tif'))
            #        frame_color = cv2.imread(os.path.join(data_path,img_name+'.tif'))
            
            #--------------------------------------------------------------------------
            # Choose the color threshold
            #--------------------------------------------------------------------------
            imH,imW, *rest = np.shape(frame_color)
             
            #        #    flag = 0 
            #        #    if(flag is not 1):
            #        #         v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(frame_color)
            #        #         thresh_low = (v1_min,v2_min,v3_min)
            #        #         thresh_high = (v1_max,v2_max,v3_max)
            #        #         flag = 1
            #        thresh_low = [0, 0, 80]
            #        thresh_high = [255, 255, 255]
            #--------------------------------------------------------------------------
            # Read the PIV data and Display it
            #--------------------------------------------------------------------------
            
            pklFile = os.path.join(rootFolder,dataFolder,PIVfolder,file)
            x,y,u,v,orgContour, circleContour = readPIVdata(pklFile)
            
            # Convert from drawing to image coordinates
            y = np.flipud(y)
            
            print('X[0,0] {}'.format(x[0,0]))
            print('Y[0,0] {}'.format(y[0,0]))
            print('X[imW,imH] {}'.format(x[-1,-1]))
            print('Y[imW,imH] {}'.format(y[-1,-1]))
            
            #--------------------------------------------------------------------------
            # Convert the data to real units
            #--------------------------------------------------------------------------
            x_real,y_real = (mmPerPixel(imW)*x, mmPerPixel(imW)*y)
                
            x_fine, y_fine, u_fine, v_fine = interpolateToGrid(x,y,u,v,scaleFactor=2)
            
            # Note that the PIV data places the upper left corner as Ymax
            maskInside = pointInContour(x,y, orgContour)
            maskInside_fine = pointInContour(x_fine,y_fine, orgContour)
            rx_0, ry_0 = findCentroid(orgContour)
            rx_0, ry_0 = (mmPerPixel(imW)*rx_0, mmPerPixel(imW)*ry_0)
            
            u[maskInside] = np.nan
            v[maskInside] = np.nan
            
            u_fine[maskInside_fine] = np.nan
            v_fine[maskInside_fine] = np.nan
            
            U = velMag(u,v)
            U_fine = velMag(u_fine,v_fine)
            #--------------------------------------------------------------------------
            # Measure the major and minor object dimensions
            #--------------------------------------------------------------------------
            ellipse = cv2.fitEllipse(orgContour)
            print(ellipse)
            
            # in mm
            objDia = mmPerPixel(imW)*(ellipse[1][0]+ellipse[1][1])/2
            
            objDia_array[ii] = objDia
            
            print('Diameter of object: {} microns'.format(1000*objDia))
            #--------------------------------------------------------------------------
            # Plot the experimental velocity field
            #--------------------------------------------------------------------------
#            plotPIVdata(frame_color, x_fine,y_fine, u_fine, v_fine, U_fine, orgContour, figname = 1)
#            plotPIVdata(frame_color, x,y,u,v,U, orgContour, figname = 1)

         
            
            #--------------------------------------------------------------------------
            # velocity fit file
            #--------------------------------------------------------------------------
            saveFile = os.path.join(resultFolder,'velocityFit_' + img_name+'.pkl')
         
            #--------------------------------------------------------------------------
            # If the data doesnt exist then compute it.
            #--------------------------------------------------------------------------
            if(not os.path.exists(saveFile) or computeNew == 1):
                
    #                
    #                
    #                
    #    
            #==============================================================================
            #   The Fitting Block starts here
            #==============================================================================
            #     Non-linear least-squares fit
            #==============================================================================
            #     Fit parameters [p_x, p_y, r_c_x, r_c_y, U, A_st, A_str, A_sd]
            #    --------------------------------------------------------------------------
            #     Initial guess values
            #    --------------------------------------------------------------------------
          
            
                px_0, py_0 = [0, 1]
                print('Organism orientation vector : ({}, {})'.format(px_0, py_0))
                
            
                Ux_0, Uy_0 = [0, 0]
                A_st_0 = 0
                A_str_0 = 0
                A_sd_0 = 0
                
                 
                if(ii>0):
                    if(r_x_fit < rx_0 - objDia/2 or r_x_fit > rx_0 + objDia/2 or r_y_fit < ry_0 - objDia/2 or r_y_fit > ry_0 + objDia/2 ):
                        r_x_fit, r_y_fit = (rx_0, ry_0)
                    fit_params_0 = [p_x_fit, p_y_fit, r_x_fit, r_y_fit, Ux_trans_fit, Uy_trans_fit, A_st_fit, A_str_fit, A_sd_fit]
                else:
                    fit_params_0 = [px_0, py_0, rx_0, ry_0, Ux_0, Uy_0, A_st_0, A_str_0, A_sd_0]
                    
                print(50*'*')
                print('Initial Guess Values')
             
                print(fit_params_0)
                print(50*'*')
                
                
                fit_params_min = [-1, -1, rx_0 - objDia/2,  ry_0 - objDia/2,-np.inf, -np.inf, -np.inf, -np.inf, -np.inf ]
                fit_params_max = [1, 1,  rx_0 + objDia/2, ry_0 + objDia/2,np.inf, np.inf, np.inf, np.inf, np.inf ]
    
#                fit_params_min = [0, 0, -np.inf,  -np.inf, -np.inf, -np.inf, -np.inf, -np.inf ]
#                fit_params_max = [1, 1,  np.inf, np.inf , np.inf, np.inf, np.inf, np.inf ]
    
                #--------------------------------------------------------------------------
                # Fitting with the organism orientation as a free parameter
                #--------------------------------------------------------------------------
                
                res_1 = least_squares(computeVelocityError, fit_params_0, bounds = (fit_params_min, fit_params_max), kwargs = {'X_exp':x_real, 'Y_exp':y_real, 'U_exp':u, 'V_exp':v, 'mask':maskInside}, max_nfev = 100)
                print(res_1.x)
                residualVect = res_1.fun 
                #--------------------------------------------------------------------------
                #  Find norm of residual vector
                #--------------------------------------------------------------------------
                residualNorm = vectorNorm(residualVect)
                
                U_flat = np.array([u[~np.isnan(u)].flatten(), v[~np.isnan(v)].flatten()]).flatten()
                
                U_norm = vectorNorm(U_flat)
                
                
                relError = residualNorm/U_norm                
    
                print(50*'=')
                print('Converged in {} iterations with Status {}'.format(res_1.nfev, res_1.status))
                print('Relative error{} %'.format(relError*100))
                print(50*'=')
               
                
                
                p_x_fit, p_y_fit, r_x_fit, r_y_fit, Ux_trans_fit, Uy_trans_fit, A_st_fit, A_str_fit, A_sd_fit = res_1.x 
            
                p_x_fit, p_y_fit = unitvector([p_x_fit, p_y_fit])
                
            
                with open(os.path.join(resultFolder,'velocityFit_' + img_name+'.pkl'), 'wb') as f:  # Python 3: open(..., 'wb')
                            pickle.dump((p_x_fit, p_y_fit, r_x_fit, r_y_fit, Ux_trans_fit, Uy_trans_fit, A_st_fit, A_str_fit, A_sd_fit, relError), f)
    #            
                #--------------------------------------------------------------------------
                # If the data already exists then read it into memory
                #--------------------------------------------------------------------------
            else:
                p_x_fit, p_y_fit, r_x_fit, r_y_fit, Ux_trans_fit, Uy_trans_fit, A_st_fit, A_str_fit, A_sd_fit, relError = readVelocityFitData(saveFile)
                
             
                
            
            #--------------------------------------------------------------------------
            # Store the fitted data in an array for plotting purposes
            #--------------------------------------------------------------------------
            x_cent_array[:,ii] = [r_x_fit, r_y_fit]
            p_array[:,ii] = unitvector([p_x_fit, p_y_fit])
            U_array[:,ii] = [Ux_trans_fit, Uy_trans_fit]
            A_st_array[ii] = A_st_fit
            A_str_array[ii] = A_str_fit
            A_sd_array[ii] = A_sd_fit
            relError_array[ii] = relError
    #            
            print(50*'*')
            print('centroid location: ({},{}) '.format(r_x_fit, r_y_fit))
            print('Translational velocity: ({}, {}) mm/s'.format(Ux_trans_fit,Uy_trans_fit))
            print('Organism orientation vector : ({}, {})'.format(p_x_fit, p_y_fit))
            print('A_st (Stokeslet): {:.3e} mm^2/s'.format(A_st_fit))
            print('A_str (Stresslet): {:.3e} mm^3/s'.format(A_str_fit))
            print('A_sd (Source Doublet): {:.3e} mm^4/s'.format(A_sd_fit))
            print(50*'*')
            
            
            # Plot and compare the experimental and fitted velocity fields
            # Compute the "Fitted" velocity field
            u_fit, v_fit = computeFittedVelocity(x_real, y_real, p =[p_x_fit, p_y_fit],r_c = [r_x_fit, r_y_fit], U = [Ux_trans_fit, Uy_trans_fit], A_st = A_st_fit, A_str = A_str_fit, A_sd = A_sd_fit)
            # Find norm of residual vector
            
#            U_flat = np.array([u[~np.isnan(u)].flatten(), v[~np.isnan(v)].flatten()]).flatten()
                
#            U_norm = vectorNorm(U_flat)
                
#            U_fit_flat = np.array([u_fit[~np.isnan(u)].flatten(), v_fit[~np.isnan(v)].flatten()]).flatten()
            
#            residualNorm = vectorNorm(U_fit_flat)
#            relError = residualNorm/U_norm 
#            
#            relError_array[ii] = relError
            
            
            u_fit[maskInside] = np.NaN
            v_fit[maskInside] = np.NaN
            
            U_fit = velMag(u_fit,v_fit)
            
            velErrorMag = velMag(u_fit - u, v_fit - v)
            
            U_exp_mag = velMag(u, v)
            
            
            # Stores the average of the point-wise error in magnitude
            relError_mag_array[ii] = np.nanmean(velErrorMag/U_exp_mag)
            
#            --------------------------------------------------------------------------
#             Plot the experimental velocity, fit velocity and the error
#            --------------------------------------------------------------------------
            # Only display the data with relative error that satisfies this condition
            
            errorBound = 1.0
            if(relError <= errorBound):
                cv2.drawContours(frame_color, [orgContour], 0, (0,255,0), 2)        
                fig = plt.figure(1)
                
                    
                fig.clf()
                plt.subplot(121)

                plt.imshow(frame_color)
                
#                ax1 = plt.contourf(x,np.flipud(y),U)
#                plt.quiver(x,np.flipud(y),u,v)
                
                ax1 = plt.contourf(x,y,U)
                plt.quiver(x,y,u,v)
                plt.scatter(pixelPermm(imW)*rx_0,pixelPermm(imW)*ry_0, color='b')

            #            ax1 = plt.contourf(x,y,U)
            #            plt.quiver(x,y,u,v)
                
                
                cbar = plt.colorbar(ax1)
                
                cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
#                plt.axis('image')
                plt.title('Experimental velocity field')
                
                plt.subplot(122)
            #            cv2.drawContours(frame_color, [orgContour], 0, (0,255,0), 3)    
                plt.imshow(frame_color)
#                ax2 = plt.contourf(x,y,U_fit)
                ax2 = plt.contourf(x,y,U_fit)
#                plt.scatter(pixelPermm(imW)*r_x_fit,pixelPermm(imW)*(imH*mmPerPixel(imW)-r_y_fit), color='b')
#                plt.scatter(pixelPermm(imW)*rx_0,pixelPermm(imW)*(imH*mmPerPixel(imW)-ry_0), color='b')
                plt.scatter(pixelPermm(imW)*r_x_fit,pixelPermm(imW)*r_y_fit, color='b')

                
                plt.quiver(x,y,u_fit, v_fit)
#                plt.quiver(x,y,np.flipud(u_fit), np.flipud(v_fit))
                
                plt.arrow(pixelPermm(imW)*rx_0,pixelPermm(imW)*(ry_0), 50*p_x_fit, 50*-p_y_fit, head_width=5, head_length=5, fc='r', ec='r')    

#                plt.arrow(pixelPermm(imW)*r_x_fit,pixelPermm(imW)*(imH*mmPerPixel(imW)-r_y_fit), 50*p_x_fit, 50*-p_y_fit, head_width=5, head_length=5, fc='r', ec='r')    
                plt.title('Fitted velocity field')
                
                cbar = plt.colorbar(ax2)
                cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
#                plt.axis('image')
                plt.pause(0.001)
                
                plt.show(block=True)
                
                plotScalarField(x_real, y_real, velErrorMag/U_exp_mag, figname = 2)
#            --------------------------------------------------------------------------
            
            
            u_lab, v_lab = (u_fine + Ux_trans_fit, v_fine + Uy_trans_fit )
            U_lab = velMag(u_lab, v_lab)
            
#            plt.figure(6)
#            plt.ioff()
#            plt.clf()
##            plt.subplot(121)
##            plt.imshow(frame_color)
##                
##            ax1 = plt.contourf(x_fine,y_fine,U_fine,cmap = cmocean.cm.amp)
##            plt.quiver(x_fine[::2],y_fine[::2],u_fine[::2],v_fine[::2])
##            cbar = plt.colorbar(ax1)
##            cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
##            plt.title('Organism Reference frame')
##            
##            plt.subplot(122)
#            frame_gs = cv2.cvtColor(frame_color , cv2.COLOR_BGR2GRAY)
#
#            plt.imshow(frame_gs, cmap = plt.get_cmap('gray'),extent = [0,mmPerPixel(imW)*imW,mmPerPixel(imW)*imH, 0])
#            
#            x_real_fine, y_real_fine = (mmPerPixel(imW)*x_fine,mmPerPixel(imW)*y_fine)
#            ax1 = plt.contourf(x_real_fine,y_real_fine,U_lab,cmap = cmocean.cm.amp)
#            plt.quiver(x_real_fine[::2],y_real_fine[::2],u_lab[::2],v_lab[::2])
#            ax4 = plt.streamplot(x_real_fine,y_real_fine,u_lab,-v_lab,color=[1,1,1,0.75],linewidth = 1.2, density = 1.5, arrowsize=0.001)
#
#            cbar = plt.colorbar(ax1)
#            cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
#            plt.title('Lab Reference frame')
#            plt.pause(0.001)
#            plt.savefig(os.path.join(labFrameFolder,img_name+'labRefFrame'+imgType[0]),dpi=300)
#            plt.savefig(os.path.join(labFrameFolder,img_name+'labRefFrame'+imgType[1]),dpi=300)
            
            
#            key = cv2.waitKey(1000) & 0xFF
#            # if the 'q' key is pressed, stop the loop
#            if key == ord("q"):
#                break
            
    
            plt.draw()
            
            
        
#        indexMax = next((i for i,x in enumerate(indexArray) if x >= 6000), None)
        
        indexArray = np.array(indexArray)
        errorFilter = np.array(relError_array <= errorBound, dtype= 'bool')
        
        print(np.shape(errorFilter))
        
        print(np.shape(indexArray))
        print(np.shape(relError_array))
        
        # Plot the fitted parameters as a function of the Index/Time
        # Relative error of the fit
        plt.figure(3)
        plt.scatter(indexArray[errorFilter], 100*relError_array[errorFilter],20, color ='r',marker = 's')
        plt.xlabel('Image Index')
        plt.ylabel('Relative error (%)')
        plt.title('Relative error')
        plt.show()
        
        # Centroid
        
        plt.figure(4)
        plt.subplot(121)
        ax1 = plt.scatter(indexArray[errorFilter],p_array[0,errorFilter],20,color='r', marker ='o',label=' Orientation X ')
        ax2 = plt.scatter(indexArray[errorFilter],p_array[1,errorFilter],20,color='g', marker ='^', label = 'Orientation Y')
        plt.xlabel('Image Index')
        plt.ylabel('Centroid position (mm)')
        plt.title('Orientation')
#        plt.legend(handles=[ax1, ax2])
        
        # Orientation vector
        plt.subplot(122)
        ax1 = plt.scatter(indexArray[errorFilter],x_cent_array[0,errorFilter],20,color='r', marker ='o',label='X centroid')
        ax2 = plt.scatter(indexArray[errorFilter],x_cent_array[1,errorFilter], 20,color='g', marker ='^', label = 'Y centroid')
        plt.xlabel('Image Index')
        plt.ylabel('Centroid position (mm)')
        plt.title('Centroid position')
#        plt.legend(handles=[ax1, ax2])
        
        plt.show()
        
        
        # Translation veclocity
        plt.figure(5)
        plt.subplot(221)
        ax1 = plt.scatter(indexArray[errorFilter],U_array[0,errorFilter],20,color='r')
        ax2 = plt.scatter(indexArray[errorFilter],U_array[1,errorFilter],20,color='g')

        plt.xlabel('Image Index')
        plt.ylabel('Translational velocity (mm/s')
        plt.title('Translational velocity')
        
        # Stokeslset strength
        plt.subplot(222)
        ax1 = plt.scatter(indexArray[errorFilter],A_st_array[errorFilter],20,color='r')
        plt.xlabel('Image Index')
        plt.ylabel('Stokeslet strength (mm^2/s')
        plt.title('Stokeslet strength')
        
        # Stresslet Strength
        plt.subplot(223)
        ax1 = plt.scatter(indexArray[errorFilter],A_str_array[errorFilter],20,color='g')
        plt.xlabel('Image Index')
        plt.ylabel('Stresslet strength (mm^3/s')
        plt.title('Stresslet strength')
        
        # Source Dipole Strength
        plt.subplot(224)
        ax1 = plt.scatter(indexArray[errorFilter],A_sd_array[errorFilter],20,color='b')
        plt.xlabel('Image Index')
        plt.ylabel('Source Dipole strength (mm^4/s')
        plt.title('Source Dipole strength')
        
        plt.show()
        
        objDia_mean, objDia_std = (np.nanmean(objDia_array), np.nanstd(objDia_array))
        
        Ux_trans_mean, Ux_trans_std = (np.nanmean(U_array[0,errorFilter]), np.nanstd(U_array[0,errorFilter]))
        Uy_trans_mean, Uy_trans_std = (np.nanmean(U_array[1,errorFilter]), np.nanstd(U_array[1,errorFilter]))

        
        A_st_mean, A_st_std = (np.nanmean(A_st_array[errorFilter]), np.nanstd(A_st_array[errorFilter]))
        
        # Find the mean and std of the fitted parameters
        print('Organism size (Mean +- Std) {} +- {} mm'.format(np.nanmean(objDia_array), np.nanstd(objDia_array)))
        print('Translational velocity X (Mean +- Std) {} +- {} mm/s'.format(Ux_trans_mean, Ux_trans_std))
        print('Translational velocity Y (Mean +- Std) {} +- {} mm/s'.format(Uy_trans_mean, Uy_trans_std))

        print('Stokeslet strength (Mean +- Std) {} +- {} mm^2/s'.format(np.nanmean(A_st_array[errorFilter]), np.nanstd(A_st_array[errorFilter] )))
        print('Stresslet strength (Mean +- Std) {} +- {} mm^3/s'.format(np.nanmean(A_str_array[errorFilter]), np.nanstd(A_str_array[errorFilter] )))
        print('Source Dipole strength (Mean +- Std) {} +- {} mm^4/s'.format(np.nanmean(A_sd_array[errorFilter]), np.nanstd(A_sd_array[errorFilter] )))

        
        
        
        # Store the fitted parameters in an array for the dataset
        fileName = 'FittedParameters.pkl'
        fileName_mean_std = 'FittedParameters_Mean_Std.pkl'
        
        
        with open(os.path.join(rootFolder, dataFolder,fileName), 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump((x_cent_array, p_array, U_array, A_st_array, A_str_array, A_sd_array, relError_array, relError_mag_array) , f)
    #                

        with open(os.path.join(rootFolder, dataFolder,fileName_mean_std), 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump((objDia_mean, objDia_std, Ux_trans_mean, Ux_trans_std, Uy_trans_mean, Uy_trans_std, A_st_mean, A_st_std,errorBound) , f)
    #            
            
            
    #            
#        g = 9.81
#        mu = 1e-3
#        R = 
#        A_st_SI = A_st*1e-6 
#        deltaRho = 6*mu*A_st_SI/(g*(R**3))
#        
#        print('Density difference: {} kg/m^3'.format(deltaRho))
    #            
    #            #----------------------------------------------------------------------
    #            # Velocity in the lab reference frame
    #            #----------------------------------------------------------------------
    #            u_lab, v_lab = (u_fine + U_0*p_x, v_fine + U_0*p_y )
    #            U_lab = velMag(u_lab,v_lab)
    #            
    #  
    #            
    #            #----------------------------------------------------------------------
    #            # Velocity with translation and stokeslet component subtracted
    #            #----------------------------------------------------------------------
    #            
    #            
    #    #        u_fit, v_fit = computeFittedVelocity(x_real,y_real, unitvector([p_x,p_y]), [r_c_x, r_c_y], U_0, A_st, A_str, A_sd)
    #    #        
    #    #        
    #    #        #    
    #    #        u_fit[maskInside] = np.nan
    #    #        v_fit[maskInside] = np.nan
    #    #        
    #    #        U_fit = velMag(u_fit, v_fit)
    #    #            
    #    #        u_error, v_error = (u - u_fit, v - v_fit)
    #    #        u_error_flat, v_error_flat = (u_error.flatten(), v_error.flatten()) 
    #    #        u_flat, v_flat = (u.flatten(), v.flatten()) 
    #    #        
    #    #        U_error_flat = np.array([u_error_flat, v_error_flat])
    #    #        U_flat = np.array([u_flat, v_flat])
    #    #        U_error_flat = U_error_flat.flatten()
    #    #        U_flat = U_flat.flatten()
    #    #        
    #    #        
    #    #        relError_array[ii] = np.inner(U_error_flat,U_error_flat)**(1/2)/np.inner(U_flat,U_flat)**(1/2)
    #    #           
    #    #        print('Relative error: {}'.format(relError_array[ii]))
    #    #       
    #    #        U_error = velMag(u_error, v_error)
    #    #        relError = 100*U_error/U
    #            
    #            
    #            
    #            #    plotPIVdata(frame_color,x,y,u_fit ,v_fit,U_fit, orgContour)
    #            
    #            #--------------------------------------------------------------------------
    #            f, (axes1, axes2) = plt.subplots(1,2)
    #            
    #            axes1.imshow(frame_color)
    #            ax1 = axes1.contourf(x,y,np.flipud(U))
    #            axes1.quiver(x[::2],y[::2],np.flipud(u[::2]),np.flipud(v[::2]))
    #            
    #            cbar = plt.colorbar(ax1)
    #            
    #            cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
    #            axes1.set_title('Experimental velocity field')
    #            
    #               
    #            axes2.imshow(frame_color)
    #            ax2 = axes2.contourf(x,y,U_fit)
    #    #        ax2 = axes2.contourf(x,y,np.flipud(U_fit))
    #            axes2.scatter(pixelPermm(imW)*r_c_x,pixelPermm(imW)*r_c_y, color='b')
    #    #        axes2.quiver(x[::2],y[::2],np.flipud(u_fit[::2]),np.flipud(v_fit[::2]))
    #            axes2.quiver(x[::2],y[::2],u_fit[::2],v_fit[::2])
    #    
    #            axes2.arrow(pixelPermm(imW)*r_c_x,pixelPermm(imW)*r_c_y, 50*p_x, 50*p_y, head_width=5, head_length=5, fc='r', ec='r')    
    #            axes2.set_title('Fitted velocity field')
    #            
    #            cbar = plt.colorbar(ax2)
    #            cbar.ax.set_ylabel('Velocity magnitude (mm/s)')
    #            plt.pause(0.001)
    #            plt.show(block=False)
    #    #        --------------------------------------------------------------------------
    #            
    #            
    #            
    #    #            f = plt.subplots(figsize=(12,6))
    #    #            plt.subplot(121)
    #    #            plt.imshow(frame_color)
    #    #            ax1 = plt.contourf(x,y,(u-u_fit)/u)
    #    #            
    #    #            cbar = plt.colorbar(ax1)
    #    #            
    #    #         
    #    #            plt.title('Relative error in X velocity')
    #    #           
    #    #            
    #    #            plt.subplot(122)
    #    #            plt.imshow(frame_color)
    #    #            ax2 = plt.contourf(x,y,(v-v_fit)/u)
    #    #            plt.title('Relative error in Y velocity')
    #    #            
    #    #            cbar = plt.colorbar(ax2)
    #    #        
    #    #            plt.show()
    #            
    #            
    #    #        f = plt.figure(4)
    #    #        ax1 = plt.contourf(x,y,relError)
    #    #        cbar = plt.colorbar(ax1)
    #    #        cbar.ax.set_ylabel('Relative error (|u_fit - u|/|u|')
    #    #        plt.axis('image')
    #    #        plt.show()
    #            
    #            #    print('Mean relative error  in X velocity: {}'.format(100*np.inner(u-u_fit,u-u_fit)**(1/2)/np.inner(u,u)**(1/2)))
    #            #    print('Mean relative error  in Y velocity: {}'.format(100*np.inner(v-v_fit,v-v_fit)**(1/2)/np.inner(v,v)**(1/2)))
    #        
    #        
    #    # Plot the fitted parameters as a function of time
    #    
    #    # Relative error
    #        f = plt.figure()
    #        plt.plot(index_array, 100*relError_array)
    #        plt.xlabel('Index')
    #        plt.ylabel('Relative Error (%)')
    #        
    #        # Translational velocity
    #        f = plt.figure(figsize=(16,9))
    #        f1 = plt.subplot(131)
    #        plt.plot(index_array,U_array)
    #        plt.xlabel('Index')
    #        plt.ylabel('Fitted Translation Velocity (mm/s)')
    #        
    #        f2 = plt.subplot(132)
    #        plt.plot(index_array,A_st_array)
    #        plt.xlabel('Index')
    #        plt.ylabel('Fitted Stokeslet Strength (mm/s)')
    #        
    #        f3 = plt.subplot(133)
    #        plt.plot(index_array,A_str_array)
    #        plt.xlabel('Index')
    #        plt.ylabel('Fitted Stresslet Strength (mm/s)')
    #    
    
if __name__ == '__main__':
    main()