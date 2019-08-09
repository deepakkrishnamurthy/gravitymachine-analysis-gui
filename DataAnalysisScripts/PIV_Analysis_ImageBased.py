#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 12:38:47 2018
PIV analysis of Gravity Machine Data
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

def getColorThreshold(imageName, filterName = 'HSV'):
   
    
    range_filter = filterName.upper()

   
    image = cv2.imread(imageName)

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
#==============================================================================
def velMag(u,v):
    return np.sqrt((u**2+v**2))
#==============================================================================
def plotPIVdata(image,x,y,u,v, orgContour,figname=1,show = 0,saveFileName='PIVdata.tif'):
    # Plots the PIV vector field overlaid on the raw image
    imH, imW, *rest = np.shape(image)
    
    if(orgContour is not None):
        maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
        x, y = (x*mmPerPixel(imW), y*mmPerPixel(imW))
        u[maskInside] = np.nan
        v[maskInside] = np.nan
    U = velMag(u,v)
       
    U_min = 0
    U_max = 100
    levels = np.linspace(U_min, U_max, 9)
    
#    u,v, U = (np.flipud(u), np.flipud(v), np.flipud(U))
    y = np.flipud(y)
    
    fig = plt.figure(figname,figsize=(12,8))
#    plt.ioff()
    plt.clf()
    ax =plt.gca()
#    cv2.drawContours(image, [orgContour], -1,(0,255,0), 3)
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0, extent = [0,mmPerPixel(imW)*imW,mmPerPixel(imW)*imH, 0])
#    ax2 = plt.contourf(x, y, 1000*U, cmap = cmocean.cm.amp, levels=levels, alpha=1.0,linewidth=0,linestyle=None, vmin=U_min, vmax=U_max)
    
    #ax2 = plt.pcolor(x,y,U,cmap = cmocean.cm.amp)
    #ax1 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.solar)
    #ax3 = plt.streamplot(x,y,u,v)
    
#    ax3 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.amp)
#    ax4 = plt.streamplot(x,y,u,-v,color=[1,1,1,0.75],linewidth = 1.2, density = 1.5, arrowsize=0.001)

    ax3 = plt.quiver(x[::2],y[::2],u[::2],v[::2],1000*U[::2], scale = 1, cmap = cmocean.cm.amp)

#      ax3 = plt.quiver(x[::2],y[::2],u[::2],v[::2],C = 1000*U color=[0,0,0,0.8], scale = 1)


    cbar = plt.colorbar(ax3)
#    plt.clim(U_min,U_max)
    
    

    cbar.set_label('Flow velocity magnitude (um/s)')
    plt.axis('image')
    
#    
    plt.savefig(saveFileName,dpi=300)
#    if(show==1):
    plt.show(block=False)
    plt.pause(0.001)
#    plt.show()
    
    
    

#==============================================================================
# Extract the image region corresponding to the organism.
#==============================================================================  
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

    
#    plt.matshow(im_th , cmap=cm.Greys_r )
#    plt.title('Thresholded Image')
#    plt.show()
    
    # Select the largest contour as the final mask
    cnts = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    print('No:of contours:{}'.format(len(cnts)))
    
   
    largestContour = max(cnts, key=cv2.contourArea)
    
    M = cv2.moments(largestContour)
    
    # Approximate the contour to 1% of its arcLength
    epsilon = 0.001*cv2.arcLength(largestContour,True)
    approxContour = cv2.approxPolyDP(largestContour,epsilon,True)
    
    # Find the center and radius of largest enclosing circle        
    ((x, y), radius) = cv2.minEnclosingCircle(largestContour)
    
    orgCentroid = np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
    
    cv2.circle(im_th,(orgCentroid[0],orgCentroid[1]),int(5*radius),color=255,thickness=-1)
    
    cnts_circle = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]

    print('No:of contours in circle masked image:{}'.format(len(cnts_circle)))
    
    circleContour = max(cnts_circle, key=cv2.contourArea)
    
    
    
    return im_th, approxContour, circleContour, orgCentroid 
   

    
#==============================================================================
# PIV Analysis
#==============================================================================
def doPIV(frame_a_color,frame_b_color, dT = 1.0, sign2noise_min=1.5, pixel2mm = 1.0, smoothing_param = 2.0):
       
    frame_a = cv2.cvtColor(frame_a_color , cv2.COLOR_BGR2GRAY)
    frame_b = cv2.cvtColor(frame_b_color , cv2.COLOR_BGR2GRAY)
    
   
    
 
    win_size = 64
    overlap = 32
    searchArea = 64
    u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a.astype(np.int32), frame_b.astype(np.int32), window_size = win_size, overlap = overlap, dt = dT, search_area_size = searchArea, sig2noise_method='peak2peak' )
    
    x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size = win_size, overlap = overlap )

    u,v = pivPostProcess(u,v,sig2noise,sig2noise_min = 1.5 ,smoothing_param = 2.0)
    #x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 100 )
    
   # openpiv.tools.save(x, y, u, v, mask, 'exp1_001.txt' )
   
    #openpiv.tools.display_vector_field('exp1_001.txt', scale=0.01, width=0.0025)
    return x,y,u,v

def pivPostProcess(u,v,sig2noise,sig2noise_min=1.5,smoothing_param=2.0):
    
    u, v, mask = openpiv.validation.sig2noise_val(u, v, sig2noise, threshold = sig2noise_min )

    print('-'*50)
    print('Percentage of bad vectors: {} %'.format(100*np.count_nonzero(np.isnan(u))/np.prod(u.shape)))
    print('-'*50)    
    u, v = openpiv.filters.replace_outliers( u, v, method='localmean', max_iter=10, kernel_size=2)
    
#    (u,v) =(np.flipud(u), np.flipud(v))
    
    (u,v)=(smoothData(u,sigma_smooth=1.5), smoothData(v,sigma_smooth=1.5))
    
    return u,v

def data2RealUnits(data,scale=1.0):
    return data*scale

def smoothData(data,sigma_smooth=1.0,order_=0):
     return ndimage.gaussian_filter(data, sigma= sigma_smooth, order= order_)
 
def savePIVdata(imageName,x,y,u,v,orgContour):
    pass
#==============================================================================
# Find subset of points that lie inside a contour
#==============================================================================
def pointInContour(x,y,contour):
    
    H = np.shape(x)[0]
    W = np.shape(x)[1]
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
def readCSV(fileName):
    Data=[]
    reader = csv.reader(open(fileName,newline=''))
    for row in reader:
        Data.append(row)
    n=len(Data) 
    
    #Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
    Time=np.array([float(Data[i][0]) - float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
    Xobj=np.array([float(Data[i][1]) for i in range(1,n)])                    # Xpos in motor full-steps
    Yobj=np.array([float(Data[i][2]) for i in range(1,n)])                    # Ypos in motor full-steps
    Zobj=np.array([float(Data[i][3]) for i in range(1,n)])                    # Zpos is in encoder units
    ThetaWheel=np.array([float(Data[i][4]) for i in range(1,n)])
    ZobjWheel=np.array([float(Data[i][5]) for i in range(1,n)])
    ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])              # 0 for auto, 1 for manual
    ImageName=np.array([Data[i][7] for i in range(1,n)])
    focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
    focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
    MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,n)])
    
    return Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName, focusMeasure, focusPhase, MaxfocusMeasure    
#==============================================================================
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx] 
#============================================================================== 
def mmPerPixel(resolution_width):
    return 1./628/(resolution_width/1440)   #for a 1440x1080 image
def pixelPermm(resolution_width):
    return 628*resolution_width/1440
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

def readPIVdata(filename):
    
    with(open(filename,'rb')) as f:
        x, y , u, v, orgContour, circleContour =  pickle.load(f)
    
    return x,y,u,v,orgContour, circleContour

#--------------------------------------------------------------------------
# Some preliminaries
#--------------------------------------------------------------------------
refFrame = {0:'OrgRefFrame',1:'LabRefFrame'} 
imgFormat = ['.png','.svg']
#--------------------------------------------------------------------------
# SeaCucumber
#--------------------------------------------------------------------------
#    thresh_low = [0,47,92]
#    thresh_high = [255,255,255]
#    
#    thresh_low = [0,77,50]
#    thresh_high = [255,255,255]
#--------------------------------------------------------------------------
# Dendraster
#--------------------------------------------------------------------------
#    thresh_low = [0,47,54]
#    thresh_high = [255,255,255]
#--------------------------------------------------------------------------
# Noctiluca
#--------------------------------------------------------------------------
#    thresh_low = [0,0,98]
#    thresh_high = [255,255,255]

#--------------------------------------------------------------------------
# Acorn Worm
#--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm4'
#--------------------------------------------------------------------------
# Sea Cucumber
#--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/SeaCucumber/seacucmber9_Auto'

#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'
#--------------------------------------------------------------------------
# Snail
#--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail2'
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail4'
#--------------------------------------------------------------------------
# Starfish
#--------------------------------------------------------------------------

#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'

  
#--------------------------------------------------------------------------
#    Dendraster
#--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
#--------------------------------------------------------------------------
# Noctiluca
#--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca/Noctilica7'

#Marine Snow
#    path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2'
#--------------------------------------------------------------------------
# Star Diatom
#--------------------------------------------------------------------------
#    path = '/Volumes/DEEPAK-SSD/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_07/diatom_star'

#--------------------------------------------------------------------------
# Centric diatom
#--------------------------------------------------------------------------

#    path = '/Volumes/DEEPAK-SSD/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_06/Tow_1/Centric_diatom_3_Good'

#path = '/Users/deepak/Dropbox/GravityMachine/BackgroundFlowMeaurement/BeforeEquilibration'

path = '/Users/deepak/Dropbox/GravityMachine/BackgroundFlowMeaurement/AfterMixing_Equlibration'
dataFolder, fileName = os.path.split(path)


wdir = path
   

#------------------------------------------------------------------------------
# Folder in which images are stored
#------------------------------------------------------------------------------
# If analyzing original images
#------------------------------------------------------------------------------
imageFolder = os.path.join(path,'images00000')
#    imageFolder ='/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/MarineSnow_segment_32200_Registered_GS'
#    imageFolder = '/Volumes/GRAVMACH1 2/GravityMachine/Results/PIV_Results/seacucmber9_Auto_IMG_33743_33971_Registered'
#------------------------------------------------------------------------------
# If analyzing preprocessed images then replace above folder with the folder containing those images
#------------------------------------------------------------------------------
#    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Seacucumber4_T_744_Registered_GS'



# Choose the track to analyze
TrackName = 'track000.csv'

#--------------------------------------------------------------------------
# Load data from the track into numpy arrays
#--------------------------------------------------------------------------
#    Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure = readCSV(os.path.join(path,TrackName))

Tmin = 0
Tmax = 0
Track1 = Track.GravMachineTrack(path,TrackName,Tmin,Tmax)

Track_full = Track.GravMachineTrack(path,TrackName)

nData = Track1.trackLen
#    print("{:~^50} {}".format('No:of Data points:',nData))

#--------------------------------------------------------------------------
# Specify the time interval OR the starting image of the track on which do PIV
#--------------------------------------------------------------------------    
AnalysisDict = {0:'ImageBasedSeq',1:'ImageBasedNonSeq',2:'TimeBased'}
AnalysisType = 0
#--------------------------------------------------------------------------
# Global index of the dataset
#--------------------------------------------------------------------------
indexArray = np.array(range(0,Track1.trackLen))
imageIndexMask = np.zeros_like(indexArray,dtype='bool')

for ii in indexArray:
    if(Track1.ImageName[ii]):
        imageIndexMask[ii] = 1
        
   
#--------------------------------------------------------------------------
# Index of images      
#--------------------------------------------------------------------------
imageIndex = indexArray[imageIndexMask]
print(imageIndex)

if(AnalysisDict[AnalysisType] is 'ImageBasedSeq'):
    
    startImage = 0
    startImage_str = 'IMG_'+'{:07d}'.format(startImage)+'.tif'
    nImages = 200
    stopImage = startImage + nImages
    stopImage_str = 'IMG_'+'{:07d}'.format(stopImage)+'.tif'
    
    

    
    
#        print(Track1.ImageName[imageIndex] == startImage_str)
    
    startImageIndex = np.int(np.array(np.nonzero(Track1.ImageName[imageIndex] == startImage_str)))
    stopImageIndex = np.int(np.array(np.nonzero(Track1.ImageName[imageIndex] == stopImage_str)))
    
 
#        print(startImageIndex)
#        print(stopImageIndex)
#        
#        print(Track1.ImageName[imageIndex[startImageIndex]])
#        print(Track1.ImageName[imageIndex[stopImageIndex]])
    
    
    
    # Find the global index corresponding to the image indices
    
    # Contains the global indices in the data corresponding to the images
    ImageIndexArray = imageIndex[startImageIndex:stopImageIndex]
    
    print(ImageIndexArray)
    ImagePairs = [[ImageIndexArray[ii], ImageIndexArray[ii+1]] for ii in range(0,len(ImageIndexArray)-1)]
    ImagePairs = np.array(ImagePairs)
    
#        print(ImagePairs)
    
#        for ii in range(len(ImagePairs)):
#            print('ImagePairs: {}, {}'.format(Track1.ImageName[ImagePairs[ii][0]], Track1.ImageName[ImagePairs[ii][1]]))
    
elif(AnalysisDict[AnalysisType] is 'ImageBasedNonSeq'):
    
    # Specify subset of images on which to do PIV using a Filter
    
    # FocusMeasure based Filter
    
    
    focusMeasureMean = np.nanmean(Track_full.focusMeasure)
    focusMeasureStd = np.nanstd(Track_full.focusMeasure)
    
    focusMeasureMask = Track1.focusMeasure > focusMeasureMean + 0.5*focusMeasureStd
#        focusMeasureMask = Track1.focusMeasure > 0.95*focusMeasureMean 

    # Mask of index containing images and satisfying the focus measure threshold
    bestImageMask = np.array(focusMeasureMask & imageIndexMask,dtype='bool')
    
    # Indices of images satisfying the Focus measure condition
    BestImageIndex = indexArray[bestImageMask]
    
    
    ImagePairs = []
    
    for ii in range(0,len(imageIndex)-1):
#            print(bestImageMask[imageIndex[ii]], bestImageMask[imageIndex[ii+1]],'\n')
        if(bestImageMask[imageIndex[ii]]==1 and bestImageMask[imageIndex[ii+1]]==1):
            ImagePairs.append([imageIndex[ii],imageIndex[ii+1]])
    
    ImagePairs = np.array(ImagePairs)
    print('No:of data points: {}'.format(len(ImagePairs)))

    
    startImage = int(Track1.ImageName[ImagePairs[0][0]][4:-4])
    
    stopImage = int(Track1.ImageName[ImagePairs[len(ImagePairs)-1][0]][4:-4])
    
    print(startImage)
    print(stopImage)

    
    
    time.sleep(1.0)
#        print(ImagePairs)
    # Store the 
#        ImageIndexArray = bestImagePairs
#  
#        print(Track1.ImageName[ImageIndexArray[201]])
#        print(Track1.ImageName[ImageIndexArray[202]])
#        
#        # Plot the focus measure and the filtered data points
#        plt.figure()
#        plt.plot(Track1.Time, Track1.focusMeasure)
#        plt.scatter(Track1.Time[imageIndexMask], Track1.focusMeasure[imageIndexMask],50, color = 'r')
#        #    plt.scatter(OrgTrack1.Time[imageIndexMask], OrgTrack1.focusMeasure[imageIndexMask],10, color = 'k')
#        
#        plt.scatter(Track1.Time[bestImageMask], Track1.focusMeasure[bestImageMask],30, color = 'k', alpha = 0.8)
#        plt.scatter(Track1.Time[bestImagePairs], Track1.focusMeasure[bestImagePairs],10, color = 'y', alpha = 0.7)
#        
#        plt.xlabel('Time')
#        plt.ylabel('Focus measure')
#        
#        print('No:of data points: {}'.format(len(bestImagePairs)))
        
    
elif(AnalysisDict[AnalysisType] is 'TimeBased'):
    
    # To be completed
    
    Tmin = 108
    Tmax = 110
    
    Tmin_index = next((i for i,x in enumerate(Track1.Time) if x >= Tmin), None)
    Tmax_index = next((i for i,x in enumerate(Track1.Time) if x >= Tmax), None)
    
    indexArray = range(Tmin_index, Tmax_index)
    
    
#  
#        
#--------------------------------------------------------------------------
# Create a Folder in which to store the PIV frames and other data
#--------------------------------------------------------------------------
#    resultRootFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/PIV_Results/Noctilica7_IMG_10783_11267'
#    resultRootFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/PIV_Results/Dendraster3_IMG_4329_4377'
resultRootFolder = os.path.join(wdir,fileName+'_IMG_{}_{}'.format(startImage, stopImage))
resultFolder_objFrame = os.path.join(resultRootFolder,'objFrame')
resultFolder_labFrame = os.path.join(resultRootFolder,'labFrame')
PIVdataFolder = os.path.join(resultRootFolder,'PIVdata_64px')
    
   


if(not os.path.exists(resultFolder_objFrame)):
    os.makedirs(resultFolder_objFrame)
    
if(not os.path.exists(resultFolder_labFrame)):
    os.makedirs(resultFolder_labFrame)
if(not os.path.exists(PIVdataFolder)):
    os.makedirs(PIVdataFolder)

 #--------------------------------------------------------------------------
# Choose the color thresholds to make the image mask
#--------------------------------------------------------------------------
flag = 1 # Set Flag=0 for choosing the threshold using sliders
  
if(flag is not 1):
    image_a = Track1.ImageName[ImagePairs[0][0]]
    v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(os.path.join(imageFolder,image_a))
    thresh_low = (v1_min,v2_min,v3_min)
    thresh_high = (v1_max,v2_max,v3_max)
    flag = 1
else:
    pass
     
# Marine snow
   
#    thresh_low = [0, 0, 54]
#    thresh_high = [255, 255, 255]
# Snail
#    thresh_low = [0, 0, 70]
#    thresh_high = [255, 255, 255]
#--------------------------------------------------------------------------
# Seacucumber
#--------------------------------------------------------------------------
#    thresh_low = [0, 0, 125]
#    thresh_high = [255, 255, 255]
#--------------------------------------------------------------------------
# Starfish
#--------------------------------------------------------------------------
#    thresh_low = [0, 0, 47]
#    thresh_high = [255, 255, 255]
#--------------------------------------------------------------------------
# Deandraster
#--------------------------------------------------------------------------
#    thresh_low = [0, 0, 95]
#    thresh_high = [255, 255, 255]

#--------------------------------------------------------------------------
# Noctiluca
#--------------------------------------------------------------------------
#    thresh_low = [0,0,95]
#    thresh_high = [255, 255, 255]
#--------------------------------------------------------------------------
# Star diatom
#--------------------------------------------------------------------------

#    thresh_low = [0,0,65]
#    thresh_high = [255, 255, 255]
#    

thresh_low = [255,255,255]
thresh_high = [255, 255, 255]

U_max_global = 0
U_min_global = 100

print(ImagePairs)
overwrite = True
#==============================================================================
# PIV analysis based on Image names and no:of images
#==============================================================================

#     The image pairs to be analyzed are stored in the array ImagePairs

for ii in range(len(ImagePairs)):
    
    dataIndex_a, dataIndex_b = (ImagePairs[ii][0], ImagePairs[ii][1])
    image_a, image_b = (Track1.ImageName[dataIndex_a], Track1.ImageName[dataIndex_b])
  
   
        
    
    #--------------------------------------------------------------------------
    # Load the frame-pair into memory
    #--------------------------------------------------------------------------
    frame_a_color = cv2.imread(os.path.join(imageFolder,image_a))
    frame_b_color = cv2.imread(os.path.join(imageFolder,image_b))
        
    #--------------------------------------------------------------------------
    # Store the time difference between the frames from the CSV file
    #--------------------------------------------------------------------------
    deltaT = Track1.Time[dataIndex_b] - Track1.Time[dataIndex_a]
    print(deltaT)
    print(1/float(deltaT))
    deltaX = Track1.Xobj[dataIndex_b] - Track1.Xobj[dataIndex_a]
    deltaZimg = Track1.Zobj[dataIndex_b] - Track1.Zobj[dataIndex_a]
    deltaZ_wheel = Track1.ZobjWheel[dataIndex_b] - Track1.ZobjWheel[dataIndex_a]
    deltaZ = deltaZ_wheel - deltaZimg # Displacement of wheel only
    # Velocity component due to the stage movement
    u_stage = deltaX/float(deltaT)      # Stage velocity in mm/s
    v_stage = deltaZ/float(deltaT)
    
   
        
    print(np.shape(frame_a_color))
        
#                plt.figure()
#                plt.ion()
#                plt.imshow(frame_a_color)
#                plt.show()
        
    imH,imW, *rest = np.shape(frame_a_color)
    frame_a_gs = cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2GRAY)
        
#                plt.figure()
#                plt.ion()
#                plt.imshow(frame_a_gs,cmap=plt.cm.gray)
#                plt.show()
#            frame_a, frame_b = (cv2.equalizeHist(frame_a_gs), cv2.equalizeHist(frame_b_gs))
#            
#            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#            
#            frame_a_clahe = clahe.apply(frame_a_gs)
#            
#            plt.figure()
#            plt.subplot(131)
#            plt.imshow(frame_a_gs, cmap = plt.cm.gray)
#            plt.title('Original Image')
#            plt.subplot(132)
#            plt.imshow(frame_a,cmap = plt.cm.gray)
#            plt.title('Histogram equalized')
#            plt.subplot(133)
#            plt.imshow(frame_a_clahe,cmap = plt.cm.gray)
#            plt.title('CLAHE')
#            plt.show()
        
    #--------------------------------------------------------------------------
    # Perform the PIV computation
    #--------------------------------------------------------------------------
    if(not os.path.exists(os.path.join(PIVdataFolder,'PIV_' + image_a[0:-4]+'.pkl')) or overwrite):
        print('-'*50)
        print('Analyzing Frame pairs: {} and {} \n at Time points {} and {}'.format(image_a,image_b, Track1.Time[dataIndex_a], Track1.Time[dataIndex_b]))
        print('-'*50)
        x,y,u,v = doPIV(frame_a_color,frame_b_color, dT = deltaT)
        print(imW)
        print(mmPerPixel(imW))
        u,v = (data2RealUnits(u,scale = mmPerPixel(imW)), data2RealUnits(v,scale = mmPerPixel(imW)))
    else:
#            #--------------------------------------------------------------------------
#            # Read the PIV data 
#            #--------------------------------------------------------------------------
        print('-'*50)
        print('Loading: {} and {} \n at Time points {} and {}'.format(image_a,image_b, Track1.Time[dataIndex_a], Track1.Time[dataIndex_b]))
        print('-'*50)
        pklFile = os.path.join(os.path.join(PIVdataFolder,'PIV_' + image_a[0:-4]+'.pkl'))
        x,y,u,v,orgContour, circleContour = readPIVdata(pklFile)
 
    #--------------------------------------------------------------------------
    # Interpolate the data onto a finer grid for display only
    #--------------------------------------------------------------------------
    x_fine, y_fine, u_fine, v_fine = interpolateToGrid(x,y,u,v,scaleFactor=2)
    
    #--------------------------------------------------------------------------
    # Convert the data into real units
    #--------------------------------------------------------------------------
    #x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = mmPerPixel(imW)/float(deltaT) )
   
    #--------------------------------------------------------------------------
    # Correct for stage motion
    #--------------------------------------------------------------------------
    #u,v = (u - u_stage,v - v_stage)
    #--------------------------------------------------------------------------
    # Extract a mask for the organism and for the region of fluid far from the organism
    # Set the velocity within this masked region to NaN
    #--------------------------------------------------------------------------
    
    orgContour = None
    circleContour = None
#    orgMask, orgContour, circleContour, orgCentroid = colorThreshold(frame_a_color,thresh_low,thresh_high)
#    # Note that to find the mask we need to consider the Up-down flipped matrix of the positions to follow the image convention
#    maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
#    maskInside_fine = pointInContour(np.flipud(x_fine),np.flipud(y_fine),orgContour)
#    maskInsideCircle = pointInContour(x,y,circleContour)
#    maskInsideCircle_fine = pointInContour(x_fine,y_fine,circleContour)
#    
#    u_avg, v_avg = (np.nanmean(u[~maskInsideCircle]), np.nanmean(v[~maskInsideCircle]))
#    u_avg_fine, v_avg_fine = (np.nanmean(u_fine[~maskInsideCircle_fine]), np.nanmean(v_fine[~maskInsideCircle_fine]))
    
#        print(u_avg)
#        print(u_avg_fine)
        
#                u = u - u_avg
#                u_fine = u_fine - u_avg_fine 
        
        
#            plt.figure(2)
#            plt.scatter(x,y,color='b')
#            plt.scatter(x[maskInsideCircle],y[maskInsideCircle],color='r')
#            plt.show()
        
#            u[maskInside] = np.nan
#            v[maskInside] = np.nan
#            
#            u_fine[maskInside_fine] = np.nan
#            v_fine[maskInside_fine] = np.nan
        
    U = velMag(u,v)
    
    U_max = np.nanmax(U)
    U_min = np.nanmin(U)
    #--------------------------------------------------------------------------
    # Extract global maxima and minima for the speed
    #--------------------------------------------------------------------------
    if(U_max > U_max_global):
        U_max_global = U_max
        
    if(U_min < U_min_global):
        U_min_global = U_min
    
        
    #--------------------------------------------------------------------------
    # Display image and the PIV field overlaid
    #--------------------------------------------------------------------------
    # Display the velocity field in the reference frame of the organism
    #--------------------------------------------------------------------------
    plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine ,v_fine ,orgContour,figname=1,show = 1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat[0]))
    plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine ,v_fine ,orgContour,figname=1,show = 1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat[1]))
   
    
#    plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine - u_avg_fine  ,v_fine - v_avg_fine ,orgContour,figname=1,show = 1,saveFileName=os.path.join(resultFolder_labFrame,image_a[0:-4]+'_'+refFrame[1]+imgFormat[0]))
#    plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine - u_avg_fine , v_fine - v_avg_fine ,orgContour,figname=1,show = 1,saveFileName=os.path.join(resultFolder_labFrame,image_a[0:-4]+'_'+refFrame[1]+imgFormat[1]))
#plotPIVdata(frame_a_gs,x,y,u,v,orgContour,figname=1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))

#                plotPIVdata(frame_a_gs,x,y,u,v,U,orgContour,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))



    # Display the Raw Image and Processed Images
#        frame_a_color = cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2RGB)
    
#        plt.figure()
#        plt.imshow(frame_a_color)
#        plt.title('Raw Image')
#        plt.show()
#        
#        cv2.drawContours(frame_a_color, [orgContour], -1,(0,255,0), 3)
#        plt.figure()
#        plt.imshow(frame_a_color)
#        plt.scatter(orgCentroid[0], orgCentroid[1],20,color = 'r')
#        
#        plt.title('Segmented Image')
#        plt.show()
    
    
    #--------------------------------------------------------------------------
    # Pickle the raw Data
    #--------------------------------------------------------------------------
    if(not os.path.exists(os.path.join(PIVdataFolder,'PIV_' + image_a[0:-4]+'.pkl'))):
        with open(os.path.join(PIVdataFolder,'PIV_' + image_a[0:-4]+'.pkl'), 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump((x, y , u, v, orgContour, circleContour), f)
        
    
            
   
    
    
        
print('Max speed: {}'.format(U_max_global))
print('Min speed: {}'.format(U_min_global))

    



cv2.destroyAllWindows()     
    





    
    
