#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 14:51:24 2018

@author: deepak
"""

import cv2
import sys
import pims
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import imp
import PIV_Functions
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
 
major_ver, minor_ver, subminor_ver = cv2.__version__.split('.')
 
def main():
 
    # Set up tracker.
    # Instead of MIL, you can also use
 
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    tracker_type = tracker_types[7]
    print('Using tracker: {}'.format(tracker_type))
 
    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
 
    input_dict = {0:'video',1:'images'}

    input_type = 'images'

    # We provide a either a video or sequence of frames

#    VideoFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/InfiniteBeadDance.MOV'
    
#    VideoFolder = '/Volumes/GRAVMACH1/GravityMachine/SedimentingGlassBeads_2017/StableParticlePairsMVI_1902.MOV'
#    VideoFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/SedimentingBeads/StablePair_Trimmed.MOV'
#    ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/SedimentingBeads/StablePair_Trimmed.MOV'

    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments/ProcessedImages'

    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Starfish10_failure'
    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/AcornWorm3_failure'

    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Polychaete1_failure'

    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Poly1_failure'
#    ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Poly2_failure/*.tif'
    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Starfish6_feeding'
    # ImagesFolder = '/Volumes/DEEPAK-SSD/GravityMachine/TrackingFailureData/Starfish6_wall_failure'

#    ImagesFolder = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/Pyro_Ballooning_GS'
#    ImagesFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6/images'
    
    ImagesFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3/images/'        
    rootPath, *rest = os.path.split(ImagesFolder)
    savePath = os.path.join(rootPath, 'ParticleTracks2.csv')
    
    overwrite = True
    
    if(input_type == 'video'):
    
        # Read video
        video = cv2.VideoCapture(VideoFolder)
    #        nFrames    = video.get(CV_CAP_PROP_FRAME_COUNT)
        FPS = 30
        deltaT = 1/FPS
        
        print('Video FPS : {}'.format(FPS))
    
        # Exit if video not opened.
        if not video.isOpened():
            print("Could not open video")
            sys.exit()
     
        # Read first frame.
        ok, frame = video.read()
        if not ok:
            print('Cannot read video file')
            sys.exit()
    
    elif(input_type == 'images'):

        frames = pims.ImageSequence(ImagesFolder)

        nFrames = len(frames)

        frame = frames[0]
        
        frame_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        
        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
        thresh_low = (0,0,95)
        thresh_high = (255,255,255)
        Contour = PIV_Functions.findContours(frame_hsv,thresh_low, thresh_high,'largest')
        
        cv2.drawContours(frame_gray, [Contour], 0,(255,255,255),3)
        
        cv2.imshow('frame',frame_gray)
        
        cv2.imwrite('Dendraster_segmented.png',frame_gray)
        key = cv2.waitKey(0) & 0xFF
                # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            pass
        
        
    
    if(not os.path.exists(savePath) or overwrite==True ):


       
       
        
        

    
         
        # Define an initial bounding box
    #    bbox = (287, 23, 86, 320)
     
        # Uncomment the line below to select a different bounding box
        bbox = cv2.selectROI(frame, False)
     
        # Initialize tracker with first frame and bounding box
        ok = tracker.init(frame, bbox)
        
        nFrames = 50
        
        Centroids = np.zeros(( nFrames, 2))
        Time = np.zeros((nFrames,1))
        counter = 0
        while True and counter < nFrames:
            # Read a new frame
            if(input_type == 'video'):
                ok, frame = video.read()
                
                if not ok:
                    break
            elif(input_type == 'images'):
    
                frame = frames[counter]
             
            # Start timer
            timer = cv2.getTickCount()
     
            # Update tracker
            ok, bbox = tracker.update(frame)
            
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            # Calculate the center of the bounding box and store it
            
            x_pos = bbox[0] + bbox[2]/2
            y_pos = bbox[1] + bbox[3]/2
            
#            if(counter>0):
#                Time[counter,:] = Time[counter-1,:] + deltaT
            Centroids[counter,:] = [x_pos, y_pos]
            # Calculate Frames per second (FPS)
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
     
            # Draw bounding box
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2)
     
            # Display tracker type on frame
#            cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,50),2);
         
            # Display FPS on frame
#            cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,50), 2);
     
            # Display result
            cv2.imshow("Tracking", frame)
#            cv2.imwrite(str(counter)+'.png',frame)
            # Exit if ESC pressed
            k = cv2.waitKey(1) & 0xff
            if k == 27 : break
        
            print(counter)
            counter += 1
            
        # Save data
#        Velocity = np.diff(Centroids,axis=0)/np.tile(np.diff(Time,axis=0),(1,2))
    
#        Velocity = np.insert(Velocity, 0 ,[np.nan, np.nan], axis = 0)
    
#        df = pd.DataFrame({'X':np.squeeze(Centroids[:,0]),'Z':np.squeeze(Centroids[:,1])})
        
#        df.to_csv(savePath, encoding='utf-8', index=False)

            
    else:
        
        df = pd.read_csv(savePath)
    
    
    
    

    # Analysis on the data
    
#    print(df)
#    
#    PixelPermm = 74
#    FPS = 30
#    
#    ParticleSpeed = (df['V_x']**2 + df['V_z']**2)**(1/2)*(1/PixelPermm)
#    
#    plt.figure()
#    
#    plt.scatter(df['Z'],df['X'], s= 20, c = df['Time'])
#    
#    plt.axes().set_aspect('equal', 'datalim')
#    
#    plt.show()
#    
#    plt.figure()
#    plt.plot(df['Time'], ParticleSpeed,'k-')
#    plt.fill_between(df['Time'],ParticleSpeed,0, alpha=0.3, color = 'k')
#    plt.ylim(0, np.max(ParticleSpeed)+1)
#    plt.xlim(0, np.max(df['Time']))
#    plt.show()
    
#    DestinationFolder = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/Pyro_Ballooning_Cropped'
#    
#    if(not os.path.exists(DestinationFolder)):
#        os.makedirs(DestinationFolder)
#    
#    # Read the tracks and draw the image from the centroid reference
#    counter = 0
#    imSize = 200
#    nFrames = 450
#    imgIndex = 49300
#    while True and counter < nFrames:
#        frame = frames[counter]
#        X_pos, Y_pos = (int(df['X'][counter]), int(df['Z'][counter]))
#        
#        currFrame_cropped = frame[Y_pos-int(imSize/2):Y_pos+int(imSize/2), X_pos-int(imSize/2):X_pos+int(imSize/2)]
#        
#        
#        cv2.imshow('Cropped frame',currFrame_cropped)
#        k = cv2.waitKey(1) & 0xff
#        if k == 27 : break
#    
#        cv2.imwrite(os.path.join(DestinationFolder,'IMG_'+'{:07d}'.format(imgIndex)+'.tif'), currFrame_cropped)
#
#        
#        
#        counter+=1
#        imgIndex += 1
    
    
    
        
if __name__ == '__main__':
    main()