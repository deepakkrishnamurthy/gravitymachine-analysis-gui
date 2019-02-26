#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 18:53:22 2018
Code to compute the tracking error of a track.
@author: deepak
"""
import cv2
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
import rangeslider_functions
import sys
import time

plt.close("all")

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

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

def find_centroid_enhanced(image,last_centroid):
    #find contour takes image with 8 bit int and only one channel
    #find contour looks for white object on a black back ground
    contours = cv2.findContours(image, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    print('No:of contours: {}'.format(len(contours)))
    centroid=False
    isCentroidFound=False
    if len(contours)>0:
        all_centroid=[]
        dist=[]
        for cnt in contours:
            M = cv2.moments(cnt)
           
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centroid=np.array([cx,cy])
            isCentroidFound=True
            all_centroid.append(centroid)
#            print('curr centroid \n')
#            print(np.shape(centroid))
#            print('last centroid \n')
#            print(np.shape(last_centroid))
            dist.append([(np.sum((centroid - last_centroid)**2))**(1/2)])

    if isCentroidFound:
#        print(dist)
        ind = dist.index(min(dist))
        
#        print('Index that minimizes distance {}'.format(ind))
#        print('Minimum distance {}'.format(dist[ind]))
        
        orgCentroid = all_centroid[ind]
        orgContour = contours[ind]
#        print('Prevvious Centroid {}'.format(last_centroid))
#        print('Centroid that minimizes distance {}'.format(orgCentroid))
        

 

    
    # Approximate the contour to 1% of its arcLength
    epsilon = 0.01*cv2.arcLength(orgContour,True)
    approxContour = cv2.approxPolyDP(orgContour,epsilon,True)
            
    ((x, y), radius) = cv2.minEnclosingCircle(orgContour)
        
    cv2.circle(image,(orgCentroid[0],orgCentroid[1]),int(4*radius),color=255,thickness=-1)
    
    cnts_circle = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    circleContour = max(cnts_circle, key=cv2.contourArea)
    
    return isCentroidFound, orgCentroid, approxContour, circleContour 

def colorThreshold(image,thresh_low,thresh_high):
    #--------------------------------------------------------------------------
    # Function segments an image based on a given color threshold.
    #--------------------------------------------------------------------------
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
    #--------------------------------------------------------------------------
    # Final thresholded image
    #--------------------------------------------------------------------------
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel15)
    
    return im_th
    
    
    
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
def mmPerPixel(resolution_width):
    return 1./628/(resolution_width/1440)   #for a 1440x1080 image
def pixelPermm(resolution_width):
    return 628*resolution_width/1440

def main():
    #------------------------------------------------------------------------------
    # Dendraster
    #------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
    
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish7'
     #------------------------------------------------------------------------------
    # Acorn Worm
    #------------------------------------------------------------------------------
    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm3'
    
    #------------------------------------------------------------------------------
    # Brittle Star
    #------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar9_Long_Good_Ytracking'
    
    #------------------------------------------------------------------------------
    # Sea Urchin
    #------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/SeaUrchin/SeaUrchin7'
    #------------------------------------------------------------------------------
    # Snail
    #------------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail1'
    
    dataFolder, fileName = os.path.split(path)
    resultFolder = os.path.join(os.getcwd(),'TrackingErrorAnalysis_New')
    print(resultFolder)
    if(not os.path.exists(resultFolder)):
        os.makedirs(resultFolder)
        
    
        
    imageFolder = os.path.join(path,'images')
    # Choose the track to analyze
    TrackName = 'track.csv'
    
    recompute = 1
    
    if(os.path.exists(os.path.join(resultFolder,fileName+'_trackingError' + '.pkl')) and not recompute):
        with(open(os.path.join(resultFolder,fileName+'_trackingError' + '.pkl'),'rb')) as f:
            imageTimeStamp, trackingError = pickle.load(f)
    else:
            
        #--------------------------------------------------------------------------
        # Load data from the track into numpy arrays
        #--------------------------------------------------------------------------
        Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure = readCSV(os.path.join(path,TrackName))
        nData = len(Time)
        print("{:~^50} {}".format('No:of Data points:',nData))
        
        Tmin = 74
        Tmax = 310
#        Tmin_outlier = 450
#        Tmax_outlier = 454
#        Tmin_outlier_index = next((i for i,x in enumerate(Time) if x >= Tmin_outlier), None)
#        Tmax_outlier_index = next((i for i,x in enumerate(Time) if x >= Tmax_outlier), None)
        print(Tmin)
        print(Tmax)
        
        # First time index 
        Tmin_index = next((i for i,x in enumerate(Time) if x >= Tmin), None)
        Tmax_index = next((i for i,x in enumerate(Time) if x >= Tmax), None)
        
        
        
        indexArray = range(Tmin_index, Tmax_index)
    
        
        # Choose the color thresholds to make the image mask
        flag =1
        for dataIndex_a in indexArray:
            
            if(ImageName[dataIndex_a]):
                 image_a = ImageName[dataIndex_a]
                 frame_a_color = cv2.imread(os.path.join(imageFolder,image_a))
                 imH,imW, *rest = np.shape(frame_a_color)
                 if(flag is not 1):
                     v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(os.path.join(imageFolder,image_a))
                     thresh_low = (v1_min,v2_min,v3_min)
                     thresh_high = (v1_max,v2_max,v3_max)
                 else:
                     break
                 flag = 1
            else:
                 continue
        #--------------------------------------------------------------------------
        # Specify a color threshold manually
        #--------------------------------------------------------------------------
        # Dendraster
#        thresh_low = [0, 0, 107]
#        thresh_high = [255, 255, 255]
        # Starfish
#        thresh_low = [0, 0, 49]
#        thresh_high = [255, 255, 255]
        
#        # Seacucumber
#        thresh_low = [0, 0, 95]
#        thresh_high = [255, 255, 255]
        
         # Seacucumber
#        thresh_low = [0, 0, 84]
#        thresh_high = [255, 255, 255]
         
         # Acorn Worm
        thresh_low = [0, 0, 86]
        thresh_high = [255, 255, 255]
         
#             Brittle Star
#        thresh_low = [0, 0, 62]
#        thresh_high = [255, 255, 255]
         
#          Sea Urchin/Snail
#        thresh_low = [0, 0, 84]
#        thresh_high = [255, 255, 255]
        
        imCen = (imW/float(2), imH/float(2))
        
        trackingError = []
        imageTimeStamp = []
        
        
        
        prev_centroid = np.array([imW/float(2), imH/float(2)])
        
        imgNum = len(ImageName[Tmin_index:Tmax_index]) - np.count_nonzero(ImageName[Tmin_index:Tmax_index]=='')
        print('Total number of images:', imgNum)
        print(len(indexArray))
        
#        f1 = plt.figure()
        
        for ii,dataIndex_a in enumerate(indexArray):
            
            # Check to see if the current data point corresponds to an image
            if(ImageName[dataIndex_a]):
                update_progress(ii/float(len(indexArray)))
                image_a = ImageName[dataIndex_a]
                print(image_a,'\n')
                frame_a_color = cv2.imread(os.path.join(imageFolder,image_a))
                
                im_th = colorThreshold(frame_a_color,thresh_low,thresh_high)
                
                isCentroidFound, orgCentroid, orgContour, circleContour = find_centroid_enhanced(im_th,prev_centroid)

                prev_centroid = orgCentroid                
                # Tracking error in mm
                error = mmPerPixel(imW)*(orgCentroid - imCen)
                trackingError.append(error)
                imageTimeStamp.append(Time[dataIndex_a])
#                
#                cv2.drawContours(frame_a_color, [orgContour], 0, (0,255,0), 3)
#                
#                print('Organism centroid printed {}'.format(orgCentroid))
#                
#                plt.clf()
#                plt.imshow(frame_a_color)
#                plt.scatter(orgCentroid[0],orgCentroid[1],30,color='r')
#                plt.pause(0.001)
#                plt.show(block=False)
##                
                
                
                
            else:
                continue
        
        trackingError = np.array(trackingError)
       
        print(np.shape(trackingError))
        imageTimeStamp = np.array(imageTimeStamp)
        
        RMSerrorX = (np.mean(trackingError[:,0]**2))**(1/2)
        RMSerrorZ = (np.mean(trackingError[:,1]**2))**(1/2)
        
        
        print('RMS error in X : {} mm'.format(RMSerrorX))
        print('RMS error in Z : {} mm'.format(RMSerrorZ))
        
        file = os.path.join(resultFolder,fileName+'_trackingError' + '.pkl')
        print(file)
        with open(file, 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump((imageTimeStamp, trackingError), f)  
            
            
    
    trackingError_um = trackingError*1000
    
#     Plot the Tracking error
    plt.figure(figsize=(8,6),dpi=150)
    plt.plot(imageTimeStamp, trackingError[:,0]*1000,color = 'r',label='X tracking error')
    plt.plot(imageTimeStamp, trackingError[:,1]*1000,color = 'b',label='Z tracking error')
    plt.legend()
    plt.xlabel('Time (s)')
    plt.ylabel('Tracking error (um)')
    
    plt.show()
#    
#    # Plot histogram of tracking error
#    plt.figure(figsize=(12,6),dpi=150)
#    plt.subplot(121)
#    plt.hist((trackingError_um[:,0]**2)**(1/2),density=True, facecolor = 'r', edgecolor = 'k', alpha = 0.75)
#    plt.xlabel('Tracking error X (um)')
#    plt.ylabel('Cumulative probability')
#    
#    plt.subplot(122)
#    plt.hist((trackingError_um[:,1]**2)**(1/2),density=True, facecolor = 'b', edgecolor = 'k', alpha= 0.75)
#    plt.xlabel('Tracking error Z (um)')
#    plt.ylabel('Cumulative probability')
#    
#    plt.show()
    
    
    
if __name__ == '__main__':
    main()
cv2.destroyAllWindows()
    

