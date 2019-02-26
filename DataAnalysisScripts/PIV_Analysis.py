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
def plotPIVdata(image,x,y,u,v, orgContour,figname=1,saveFileName='PIVdata.tif'):
    # Plots the PIV vector field overlaid on the raw image
    maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
    u[maskInside] = np.nan
    v[maskInside] = np.nan
    U = velMag(u,v)
       
#    U_min = 0
#    U_max = 1.2
    
    u,v, U = (np.flipud(u), np.flipud(v), np.flipud(U))
    
    fig = plt.figure(figname)
#    plt.ioff()
    plt.clf()
     
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0)
    ax2 = plt.contourf(x, y, U, cmap = cmocean.cm.amp, alpha=1.0,linewidth=0,linestyle=None)
    
    #ax2 = plt.pcolor(x,y,U,cmap = cmocean.cm.amp)
    #ax1 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.solar)
    #ax3 = plt.streamplot(x,y,u,v)
    
#    ax3 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.amp)
#    ax4 = plt.streamplot(x,y,u,-v,color='blue',linewidth = 1, density = 1.5, arrowsize=0.1)

    ax3 = plt.quiver(x[::2],y[::2],u[::2],v[::2],color='k')
    cbar = plt.colorbar(ax2)
    cbar.ax.set_ylabel('Flow velocity magnitude (mm/s)')


    plt.xlabel('X')
    plt.ylabel('Z')
    #    cbar.set_label('Speed')
    plt.axis('image')
#    plt.pause(0.001)
#    
    plt.savefig(saveFileName,dpi=300)
#    plt.show(block=False)
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
   
#    plt.matshow (cimg , cmap=cm.Greys_r )
#    plt.show()
        
    # Extract the contour of the shape to use as a mask
    
#    # Copy the thresholded image.
#    im_floodfill = im_th.copy()
#     
#    # Mask used to flood filling.
#    # Notice the size needs to be 2 pixels than the image.
#    h, w = im_th.shape[:2]
#    mask = np.zeros((h+2, w+2), np.uint8)
#     
#    # Floodfill from point (0, 0)
#    cv2.floodFill(im_floodfill, mask, (0,0), 255);
#     
#    # Invert floodfilled image
#    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
#     
#    # Combine the two images to get the foreground.
#    im_out = im_th | im_floodfill_inv
#     
#    # Display images.
#    cv2.imshow("Thresholded Image", im_th)
#    cv2.imshow("Floodfilled Image", im_floodfill)
#    cv2.imshow("Inverted Floodfilled Image", im_floodfill_inv)
#    cv2.imshow("Foreground", im_out)
#    cv2.waitKey(0)
    
    


    
#==============================================================================
# PIV Analysis
#==============================================================================
def doPIV(frame_a_color,frame_b_color, dT = 1.0, sign2noise_min=1.5, pixel2mm = 1.0, smoothing_param = 2.0):
       
    frame_a = cv2.cvtColor(frame_a_color , cv2.COLOR_BGR2GRAY)
    frame_b = cv2.cvtColor(frame_b_color , cv2.COLOR_BGR2GRAY)
    
   
    
    imW, imH = np.shape(frame_a)
 
    
    u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a.astype(np.int32), frame_b.astype(np.int32), window_size = 48, overlap = 24, dt = dT, search_area_size = 48, sig2noise_method='peak2peak' )
    
    x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size = 48, overlap = 24 )

    u,v = pivPostProcess(u,v,sig2noise,sig2noise_min = 1.5 ,smoothing_param = 2.0)
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
def main():
    #--------------------------------------------------------------------------
    # Some preliminaries
    #--------------------------------------------------------------------------
    refFrame = {0:'OrganismReferenceFrame',1:'DisturbanceVelField'} 
    imgFormat = '.png'
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
     #rootFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto/'
    #rootFolder = '/Volumes/GravMachine/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_07/Sea_Cucumber/seacucmber9_Auto/'
    #rootFolder='/Volumes/GravMachine/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_06/Dendraster/Dendraster_3_nolight/'
    #rootFolder = '/Volumes/GravMachine/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_14/Noctilica/Noctilica7/'
    #--------------------------------------------------------------------------
    # Sea Cucumber
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'
    #--------------------------------------------------------------------------
    # Snail
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail2'

    #--------------------------------------------------------------------------
    # Starfish
    #--------------------------------------------------------------------------
    
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6highfreq'
    
    dataFolder, fileName = os.path.split(path)
    
    
    resultRootFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/PIV_Results'
   

    #------------------------------------------------------------------------------
    # Folder in which images are stored
    #------------------------------------------------------------------------------
    # If analyzing original images
    #------------------------------------------------------------------------------
#    imageFolder = os.path.join(path,'images')
    #------------------------------------------------------------------------------
    # If analyzing preprocessed images then replace above folder with the folder containing those images
    #------------------------------------------------------------------------------
    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Seacucumber4_T_744_Registered_GS'
    # Choose the track to analyze
    TrackName = 'track.csv'
    
    
    #--------------------------------------------------------------------------
    # Load data from the track into numpy arrays
    #--------------------------------------------------------------------------
    Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName,focusMeasure, focusPhase, MaxfocusMeasure = readCSV(os.path.join(path,TrackName))
    nData = len(Time)
    print("{:~^50} {}".format('No:of Data points:',nData))
    
    #--------------------------------------------------------------------------
    # Specify the time interval OR the starting image of the track on which do PIV
    #--------------------------------------------------------------------------    
    time_based = 0
    
    startIndex = 18718
    nImages = 100
    stopIndex = startIndex + nImages
    
    Tmin = 108
    Tmax = 110
    
    Tmin_index = next((i for i,x in enumerate(Time) if x > Tmin), None)
    Tmax_index = next((i for i,x in enumerate(Time) if x > Tmax), None)
    
    indexArray = range(Tmin_index, Tmax_index)
    
    FocusMeasureArray = np.zeros_like(indexArray)
     #--------------------------------------------------------------------------
    #   Find the first data index corresponding to the Image Name (If Image Name is specified)
    #--------------------------------------------------------------------------
    if(time_based==0):
        indexFound = 0
        while (not indexFound):
            found_a = 0
            dataIndex_a = 0
            while(not found_a and dataIndex_a < nData):
               
                if(ImageName[dataIndex_a]=='IMG_'+str(startIndex)+'.tif'):
                    found_a = 1
                else:
                    dataIndex_a+=1
                    continue
                
            if(dataIndex_a==nData and found_a == 0):
                print('Image index not within bounds. Please enter a new start index')
                startIndex = int(input('Enter new start index'))
            elif(found_a==1):
                indexFound=1
                print('-'*50)
                print('Start Image {} found!'.format(ImageName[dataIndex_a]))
                print('-'*50)
            
        image_b = ImageName[dataIndex_a]
        
    #--------------------------------------------------------------------------
    # Create a Folder in which to store the PIV frames and other data
    #--------------------------------------------------------------------------
    if(time_based == 1):
        resultFolder_objFrame = os.path.join(resultRootFolder,fileName+'_{}_{}'.format(Tmin,Tmax),'objFrame')
        resultFolder_labFrame = os.path.join(resultRootFolder,fileName+'_{}_{}'.format(Tmin,Tmax),'labFrame')
        dataFolder = os.path.join(resultRootFolder,fileName+'_{}_{}'.format(Tmin,Tmax),'PIVdata')
    else:
        resultFolder_objFrame = os.path.join(resultRootFolder,'Registered_'+fileName+'_IMG_{}_{}'.format(startIndex,stopIndex),'objFrame')
        resultFolder_labFrame = os.path.join(resultRootFolder,'Registered_'+fileName+'_IMG_{}_{}'.format(startIndex,stopIndex),'labFrame')
        dataFolder = os.path.join(resultRootFolder,'Registered_'+fileName+'_IMG_{}_{}'.format(startIndex,stopIndex),'PIVdata')
        
    
    
    if(not os.path.exists(resultFolder_objFrame)):
        os.makedirs(resultFolder_objFrame)
    if(not os.path.exists(resultFolder_labFrame)):
        os.makedirs(resultFolder_labFrame)
    if(not os.path.exists(dataFolder)):
        os.makedirs(dataFolder)
    
     #--------------------------------------------------------------------------
    # Choose the color thresholds to make the image mask
    #--------------------------------------------------------------------------
    flag = 0 # Set Flag=0 for choosing the threshold using sliders
    if(time_based==1):
        for dataIndex_a in indexArray:
            if flag == 1:
                break
            if(ImageName[dataIndex_a]):
                 image_a = ImageName[dataIndex_a]
                 v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(os.path.join(imageFolder,image_a))
                 thresh_low = (v1_min,v2_min,v3_min)
                 thresh_high = (v1_max,v2_max,v3_max)
                 flag = 1
            else:
                 continue
    else:
         if(flag is not 1):
             image_a = ImageName[dataIndex_a]
             v1_min,v2_min,v3_min,v1_max,v2_max,v3_max = getColorThreshold(os.path.join(imageFolder,image_a))
             thresh_low = (v1_min,v2_min,v3_min)
             thresh_high = (v1_max,v2_max,v3_max)
             flag = 1
         else:
             pass
         
    
    # Snail
#    thresh_low = [0, 0, 70]
#    thresh_high = [255, 255, 255]
    #--------------------------------------------------------------------------
    # Seacucumber
    #--------------------------------------------------------------------------
#    thresh_low = [0, 0, 115]
#    thresh_high = [255, 255, 255]
    
    U_max_global = 0
    U_min_global = 100

   
    if(time_based==1):
   
        for dataIndex_a in indexArray:
            
            # Check to see if the current data point corresponds to an image
            if(ImageName[dataIndex_a]):
                image_a = ImageName[dataIndex_a]
                counter = 1
                # Iterate till you find the subsequent image
                while(not ImageName[dataIndex_a+counter]):
                    counter+=1
                dataIndex_b = dataIndex_a + counter
                image_b = ImageName[dataIndex_b]
                
                
                print('-'*50)
                print('Analyzing Frame pairs: {} and {} \n at Time points {} and {}'.format(image_a,image_b, Time[dataIndex_a],Time[dataIndex_b]))
                print('-'*50)
    
                #--------------------------------------------------------------------------
                # Store the time difference between the frames from the CSV file
                #--------------------------------------------------------------------------
                deltaT = Time[dataIndex_b] - Time[dataIndex_a]
                deltaX = Xobj[dataIndex_b] - Xobj[dataIndex_a]
                deltaZimg = Zobj[dataIndex_b] - Zobj[dataIndex_a]
                deltaZ_wheel = ZobjWheel[dataIndex_b] - ZobjWheel[dataIndex_a]
                deltaZ = deltaZ_wheel - deltaZimg # Displacement of wheel only
                # Velocity component due to the stage movement
                u_stage = deltaX/float(deltaT)      # Stage velocity in mm/s
                v_stage = deltaZ/float(deltaT)
                
                #--------------------------------------------------------------------------
                # Load the frame-pair into memory
                #--------------------------------------------------------------------------
                frame_a_color = cv2.imread(os.path.join(imageFolder,image_a))
                frame_b_color = cv2.imread(os.path.join(imageFolder,image_b))
                
                print(np.shape(frame_a_color))
                
                imH,imW, *rest = np.shape(frame_a_color)
                frame_a_gs = cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2GRAY)
                frame_b_gs= cv2.cvtColor(frame_a_color,cv2.COLOR_BGR2GRAY)
                
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
                x,y,u,v = doPIV(frame_a_color,frame_b_color, dT = deltaT)
                
                print(np.shape(x)[0])
                print(np.shape(y)[1])
                print(x.min())
                print(y.max())
                #--------------------------------------------------------------------------
                # Interpolate the data onto a finer grid for display only
                #--------------------------------------------------------------------------
                x_fine, y_fine, u_fine, v_fine = interpolateToGrid(x,y,u,v,scaleFactor=2)
                
                #--------------------------------------------------------------------------
                # Convert the data into real units
                #--------------------------------------------------------------------------
                #x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = mmPerPixel(imW)/float(deltaT) )
                u,v = (data2RealUnits(u,mmPerPixel(imW)), data2RealUnits(v,mmPerPixel(imW)))
                u_fine,v_fine = (data2RealUnits(u_fine,mmPerPixel(imW)), data2RealUnits(v_fine,mmPerPixel(imW)))
                #--------------------------------------------------------------------------
                # Correct for stage motion
                #--------------------------------------------------------------------------
                #u,v = (u - u_stage,v - v_stage)
                #--------------------------------------------------------------------------
                # Extract a mask for the organism and for the region of fluid far from the organism
                # Set the velocity within this masked region to NaN
                #--------------------------------------------------------------------------
                print('Threshold Lower: {}'.format(thresh_low))
                print('Threshold Higher: {}'.format(thresh_high))
                orgMask, orgContour, circleContour, orgCentroid = colorThreshold(frame_a_color,thresh_low,thresh_high)
                # Note that to find the mask we need to consider the Up-down flipped matrix of the positions to follow the image convention
                maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
                maskInside_fine = pointInContour(np.flipud(x_fine),np.flipud(y_fine),orgContour)
                maskInsideCircle = pointInContour(x,y,circleContour)
                
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
                plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine,v_fine,orgContour,figname=1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))
    #            plotPIVdata(frame_a_gs,x,y,u,v,U,orgContour,figname=1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))
    
               #--------------------------------------------------------------------------
                # Pickle the raw Data
                #--------------------------------------------------------------------------
                with open(os.path.join(dataFolder,'PIV_' + image_a[0:-4]+'.pkl'), 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump((x, y , u, v, orgContour, circleContour), f)
                
            else:
                continue

#==============================================================================
# PIV analysis based on Image names and no:of images
#==============================================================================

    
    else:
    
        # Iterate till we reach the end Image
        while(image_b!='IMG_'+str(stopIndex)+'.tif'):
    #        
            if(ImageName[dataIndex_a]):
                image_a = ImageName[dataIndex_a]
                counter = 1
                while(not ImageName[dataIndex_a+counter]):
                    counter+=1
                dataIndex_b = dataIndex_a + counter
                image_b = ImageName[dataIndex_b]
                
                print('-'*50)
                print('Analyzing Frame pairs: {} and {} \n at Time points {} and {}'.format(image_a,image_b, Time[dataIndex_a],Time[dataIndex_b]))
                print('-'*50)
                
                #--------------------------------------------------------------------------
                # Store the time difference between the frames from the CSV file
                #--------------------------------------------------------------------------
                deltaT = Time[dataIndex_b] - Time[dataIndex_a]
                deltaX = Xobj[dataIndex_b] - Xobj[dataIndex_a]
                deltaZimg = Zobj[dataIndex_b] - Zobj[dataIndex_a]
                deltaZ_wheel = ZobjWheel[dataIndex_b] - ZobjWheel[dataIndex_a]
                deltaZ = deltaZ_wheel - deltaZimg # Displacement of wheel only
                # Velocity component due to the stage movement
                u_stage = deltaX/float(deltaT)      # Stage velocity in mm/s
                v_stage = deltaZ/float(deltaT)
                
                #--------------------------------------------------------------------------
                # Load the frame-pair into memory
                #--------------------------------------------------------------------------
                frame_a_color = cv2.imread(os.path.join(imageFolder,image_a))
                frame_b_color = cv2.imread(os.path.join(imageFolder,image_b))
                
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
                x,y,u,v = doPIV(frame_a_color,frame_b_color, dT = deltaT)
             
                #--------------------------------------------------------------------------
                # Interpolate the data onto a finer grid for display only
                #--------------------------------------------------------------------------
                x_fine, y_fine, u_fine, v_fine = interpolateToGrid(x,y,u,v,scaleFactor=2)
                
                #--------------------------------------------------------------------------
                # Convert the data into real units
                #--------------------------------------------------------------------------
                #x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = mmPerPixel(imW)/float(deltaT) )
                u,v = (data2RealUnits(u,mmPerPixel(imW)), data2RealUnits(v,mmPerPixel(imW)))
                u_fine,v_fine = (data2RealUnits(u_fine,mmPerPixel(imW)), data2RealUnits(v_fine,mmPerPixel(imW)))
                #--------------------------------------------------------------------------
                # Correct for stage motion
                #--------------------------------------------------------------------------
                #u,v = (u - u_stage,v - v_stage)
                #--------------------------------------------------------------------------
                # Extract a mask for the organism and for the region of fluid far from the organism
                # Set the velocity within this masked region to NaN
                #--------------------------------------------------------------------------
             
                orgMask, orgContour, circleContour, orgCentroid = colorThreshold(frame_a_color,thresh_low,thresh_high)
                # Note that to find the mask we need to consider the Up-down flipped matrix of the positions to follow the image convention
                maskInside = pointInContour(np.flipud(x),np.flipud(y),orgContour)
                maskInside_fine = pointInContour(np.flipud(x_fine),np.flipud(y_fine),orgContour)
                maskInsideCircle = pointInContour(x,y,circleContour)
                maskInsideCircle_fine = pointInContour(x_fine,y_fine,circleContour)
                
                u_avg = np.nanmean(u[~maskInsideCircle])
                u_avg_fine = np.nanmean(u_fine[~maskInsideCircle_fine])
                
                print(u_avg)
                print(u_avg_fine)
                
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
                plotPIVdata(frame_a_gs,x_fine,y_fine,u_fine,v_fine,orgContour,figname=1,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))
#                plotPIVdata(frame_a_gs,x,y,u,v,U,orgContour,saveFileName=os.path.join(resultFolder_objFrame,image_a[0:-4]+'_'+refFrame[0]+imgFormat))
    
               #--------------------------------------------------------------------------
                # Pickle the raw Data
                #--------------------------------------------------------------------------
                with open(os.path.join(dataFolder,'PIV_' + image_a[0:-4]+'.pkl'), 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump((x, y , u, v, orgContour, circleContour), f)
                    
                dataIndex_a = dataIndex_b
                    
            else:
                dataIndex_a += 1
        
        
            
    print('Max speed: {}'.format(U_max_global))
    print('Min speed: {}'.format(U_min_global))

        
    
    

            
        
    
    
    
    

        
        
if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()