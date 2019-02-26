# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:33:58 2018
# Code to add time stamps to images for making Movies
@author: deepak90
"""

import numpy as np
import csv as csv
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cmocean
import os
import time
import scipy
from roipoly import roipoly
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import pickle
plt.close("all")
from PIL import Image
import imp
import Track
imp.reload(Track)


def main():
    font = cv2.FONT_HERSHEY_SIMPLEX
#    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
     #--------------------------------------------------------------------------
    # Acorn Worm
    #--------------------------------------------------------------------------
#    path="F:/GravityMachineBackup/HopkinsEmbryologyCourse/2018_06_12/Starfish/StarFish6highfreq"
    #--------------------------------------------------------------------------
    # Sea Cucumber
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1 2/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber9_Auto'
    
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_07/seacucmber4_auto_verylong_goodtrack'
    #--------------------------------------------------------------------------
    # Snail
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail2'
#    path = '/Volumes/GRAVMACH1 2/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail4'
    #--------------------------------------------------------------------------
    # Starfish
    #--------------------------------------------------------------------------
    
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Starfish/StarFish6'
    #--------------------------------------------------------------------------
#    Dendraster
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
    #--------------------------------------------------------------------------
    # Noctiluca
    #--------------------------------------------------------------------------
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_14/Noctiluca/Noctilica7'

    path = '/Volumes/DEEPAK-SSD/GravityMachine/PuertoRico_2018/GravityMachineData/2018_11_06/Tow_1/Centric_diatom_3_Good'
   

    #------------------------------------------------------------------------------
    # Folder in which images are stored
    #------------------------------------------------------------------------------
    # If analyzing original images
    #------------------------------------------------------------------------------
    imageFolder = '/Volumes/DEEPAK-SSD/GravityMachine/MovieRawFiles/Centric_Diatom_small_40_240/Images_GS'
#    imageFolder = os.path.join(path,'images')
#    imageFolder = '/Volumes/GRAVMACH1 2/GravityMachine/Results/PIV_Results/seacucmber9_Auto_IMG_33743_33971_Registered'
    #------------------------------------------------------------------------------
    # If analyzing preprocessed images then replace above folder with the folder containing those images
    #------------------------------------------------------------------------------
#    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Seacucumber4_T_744_Registered_GS'
#    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Starfish6_SideView_FlowTrace_FINAL'
#    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/Starfish6_FrontView_FlowTrace_FINAL'
    
    # Acorn worm
#    path ='/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm7'
#    imageFolder = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_06/AcornWorm_Experiment2_nolight/AcornWorm7/images'
    
    
    #Dendraster 
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_11/Dendraster_starved_11Days_nofood/Dendraster3'
    
    # Brittle Star
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/BrittleStar/BrittleStar9_Long_Good_Ytracking'
    
    # Snail
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Snail/snail1'
    
    # Polychaete 1
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_12/Polychaete_4D/Polychaete6'
    
    # Polychaete 2
#    path = '/Volumes/GRAVMACH1/HopkinsEmbroyologyCourse_GoodData/2018_06_13/Polychaete/Poly4'
#    
#    imageFolder = os.path.join(path,'images')
    
#    path = '/Volumes/GRAVMACH1/Hopkins_2018_08_31/MarSno2'
#    imageFolder = '/Volumes/GRAVMACH1/GravityMachine/Results/flowtrace_python/FinalVideos/MarineSnowFlowTrace'
    
    # Pyro Data
#    path = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/nnn1'
#    imageFolder = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/Pyro_Division_Processed_1'
    
#    imageFolder = '/Volumes/GRAVMACH1/PyroTracks_2018_12_21/Pyro_Ballooning_Cropped'
    dataFolder, fileName = os.path.split(path)

    
    
    
    imageType = 'Processed'
    
    
    rootImageFolder, folderName = os.path.split(imageFolder)
    # Choose the track to analyze
    TrackName = 'track.csv'
    
    
    

    savePath = os.path.join(rootImageFolder,folderName+'_TimeStamped')
    
    if(not os.path.exists(savePath)):
        os.makedirs(savePath)
    
    Tmin = 39
    Tmax = 250
    Track1 = Track.GravMachineTrack(path,TrackName,Tmin,Tmax)
    
    
    T_start = Track1.Time[0]
    
    if(imageType == 'Raw'):
        
        for ii in range(Track1.trackLen):
            
            if(Track1.ImageName[ii]):
                
             
                    
                Time = Track1.Time[ii] - T_start
                
                ImgName = Track1.ImageName[ii]
                
                print(ImgName)
                
                frame_color = cv2.imread(os.path.join(imageFolder,ImgName))
                
#                cv2.imshow('raw',frame_color)
                
                frame_gs = cv2.cvtColor(frame_color,cv2.COLOR_BGR2GRAY)
                
                clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(12,12))
                
                frame_clahe = clahe.apply(frame_gs)
            
                cv2.putText(frame_clahe, str(np.round(Time, decimals = 2)) + ' s', (30, 30), font, 5, (255, 255, 255), 3, cv2.LINE_AA)
                
        #        plt.clf()
#                cv2.imshow('frame',frame_clahe)
#                k = cv2.waitKey(1) & 0xff
#                if k == 27 : break
                
#                plt.show()
                
                cv2.imwrite(os.path.join(savePath, ImgName),frame_clahe)
                    
                
            
    
    elif(imageType=='Processed'):
        # List all images from the folder:
        FilesList = os.listdir(imageFolder)
        FilesList.sort()
        print(FilesList)
        
        print(Track1.Time[0])
        
#        imgName_start = FilesList[0][:-25] + '.tif'
#        imgName_end = FilesList[-1][:-25] + '.tif'
        imgName_start = FilesList[0] 
        imgName_end = FilesList[-1]
        
        
        print(imgName_start)
        print(imgName_end)
        
        startIndex,*rest = np.where(Track1.ImageName == imgName_start)
        stopIndex, *rest = np.where(Track1.ImageName == imgName_end)
        
        startIndex = int(startIndex)
        stopIndex = int(stopIndex)
        
        indexArray = []
        for ii in range(startIndex,stopIndex):
            if(Track1.ImageName[ii]):
                indexArray.append(ii)
                
    
        indexArray = np.array(indexArray)
        
        print(indexArray)
        
        
    
    
        
        
            
        imageCounter = 0
        trackCounter = 0
    
        while imageCounter < len(FilesList)-1:
            
            file = FilesList[imageCounter]
            currIndex = indexArray[trackCounter]
            
#            imgName = file[:-25] + '.tif'
            imgName = file

    
            if(Track1.ImageName[currIndex] == imgName):
                print('Correct Image found in Track')
                trackCounter += 1
                imageCounter += 1
            else:
                
                print('Missing image: {}'.format(Track1.ImageName[currIndex]))
                
                
                while(Track1.ImageName[currIndex] != imgName):
                    print('Searching for next available image...')
                    trackCounter += 1
                    currIndex = indexArray[trackCounter]
                    print(Track1.ImageName[currIndex])
    
                print('Next sequential image found!')
                        
                    
    
                
    #            
                
            
            Time = Track1.Time[currIndex] 
            
           
        
            
            frame_a_color = cv2.imread(os.path.join(imageFolder,file))
            frame_gs = cv2.cvtColor(frame_a_color, cv2.COLOR_BGR2GRAY)
        
        
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12,12))
            frame_clahe = clahe.apply(frame_gs)
    
    
            cv2.putText(img = frame_clahe, text = str(np.round(Time, decimals = 2)) + ' s', org = (30, 30), fontFace = font, fontScale=1, color = (255, 255, 255), thickness = 2,lineType = cv2.LINE_AA)
    
    #        plt.clf()
            cv2.imshow('frame',frame_clahe)
            k = cv2.waitKey(1) & 0xff
            if k == 27 : break
    #        ax = plt.gca()
            
    #        plt.show()
            
            cv2.imwrite(os.path.join(savePath, imgName),frame_clahe)
            
            
            

            
        
        
        
        
if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()

    
    
    

