# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:28:21 2018

@author: Francois
"""
import csv as csv
import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import os

'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                             CSV reader
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CSV_Reader(QtCore.QObject):
    
    Time_data = QtCore.pyqtSignal(np.ndarray)
    fps_data = QtCore.pyqtSignal(float)
    Xobjet_data = QtCore.pyqtSignal(np.ndarray)
    Yobjet_data = QtCore.pyqtSignal(np.ndarray)
    Zobjet_data = QtCore.pyqtSignal(np.ndarray)
    ImageNames_data = QtCore.pyqtSignal(np.ndarray)
    ImageTime_data = QtCore.pyqtSignal(np.ndarray)
#    ImageIndex_data = QtCore.pyqtSignal(np.ndarray)
    
    
    def __init__(self, parent=None):
        super(CSV_Reader, self).__init__(parent)
        # File name for .csv file is now auto-detected
        self.file_name=''
        
        self.Time=np.array([])
        self.Xobjet=np.array([])
        self.Yobjet=np.array([])
        self.ZobjWheel=np.array([])
        self.ImageNames=np.array([])
        self.index_min=0
        self.index_max=0
    
    
    def computeSpeed(self,X,T):
        V=[]
        for i in range(1,len(T)-1):
            deltaT=T[i+1]-T[i-1]
            V.append((X[i+1]-X[i-1])/deltaT)
        
    
    def open_newCSV(self,directory, trackFile):

        Data=[]
        
        self.file_name = trackFile

        trackPath = os.path.join(directory, self.file_name)
        
        reader = csv.reader(open(trackPath,newline=''))
        
        for row in reader:
            Data.append(row)
        n=len(Data)
        
        self.Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])             # Time stored is in milliseconds
        self.Xobjet=np.array([float(Data[i][1]) for i in range(1,n)])             # Xpos in motor full-steps
        self.Yobjet=np.array([float(Data[i][2]) for i in range(1,n)])             # Ypos in motor full-steps
        Zobjet=np.array([float(Data[i][3]) for i in range(1,n)])             # Zpos is in encoder units
        ThetaWheel=np.array([float(Data[i][4])-float(Data[1][4]) for i in range(1,n)])
        self.ZobjWheel=np.array([float(Data[i][5])-float(Data[1][5]) for i in range(1,n)])
        ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])   # 0 for auto, 1 for manual
        self.ImageNames=np.array([Data[i][7] for i in range(1,n)])
        focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
        focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
        MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,n)])
        #colorR=np.array([int(Data[i][11]) for i in range(1,n)])
        #colorG=np.array([int(Data[i][12]) for i in range(1,n)])
        #colorB=np.array([int(Data[i][13]) for i in range(1,n)])
        
        
        # position for the plot
        
        xmin=self.Xobjet.min()
        xmax=self.Xobjet.max()
        
        ymin=self.Yobjet.min()
        ymax=self.Yobjet.max()

        #To recenter the data in the case of a bad calibration
        
        if xmax-xmin>15 and (xmin<-7.5 or xmax>7.5):
            delta_x=-np.mean(self.Xobjet)
            self.Xobjet=self.Xobjet+delta_x
            xmin+=delta_x
            xmax+=delta_x
        
        elif xmin<-7.5:
            delta_x=-7.5-xmin
            self.Xobjet=self.Xobjet+delta_x
            xmin+=delta_x
            xmax+=delta_x
            
        elif xmax>7.5:
            delta_x=7.5-xmax
            self.Xobjet=self.Xobjet+delta_x
            xmin+=delta_x
            xmax+=delta_x
        
        if ymax-ymin>3 and (ymin<0 or ymax>3):
            delta_y=-(np.mean(self.Yobjet)-1.5)
            self.Yobjet=self.Yobjet+delta_y
            ymin+=delta_y
            ymax+=delta_y
            
        elif ymin<0:
            delta_y=-ymin
            self.Yobjet=self.Yobjet+delta_y
            ymin+=delta_y
            ymax+=delta_y
            
        elif ymax>3:
            delta_y=3-ymax
            self.Yobjet=self.Yobjet+delta_y
            ymin+=delta_y
            ymax+=delta_y
            
        #Speed computation
        self.Vx=np.array([])
            
        self.index_min=0
        self.index_max=len(self.Time)-1
        
        #send data on T, X,Y,Z to the plot, depending on the index range chosen        
        self.send_data()
        
        #Time and name of the image for the video reader
        self.send_image_time()
        

        
    def send_data(self):
        self.Time_data.emit(self.Time[self.index_min:self.index_max+1])
        self.Xobjet_data.emit(self.Xobjet[self.index_min:self.index_max+1])
        self.Yobjet_data.emit(self.Yobjet[self.index_min:self.index_max+1])
        self.Zobjet_data.emit(self.ZobjWheel[self.index_min:self.index_max+1])
        print('data sent')
        
    def send_image_time(self):
        cropped_ImageNames=self.ImageNames[self.index_min:self.index_max+1]
        cropped_Time=self.Time[self.index_min:self.index_max+1]
        
        ImageTime=[]
        new_ImageNames=[]
        ImageIndex = []
        
        for i in range(len(cropped_ImageNames)):
            if len(cropped_ImageNames[i])>0:
                ImageIndex.append(i)
                new_ImageNames.append(cropped_ImageNames[i])
                ImageTime.append(round(cropped_Time[i],2))
                
        # Checking to see if images are updated for a new dataset
        
        # print('New Starting Image: {}'.format(new_ImageNames[0]))

        self.ImageNames_data.emit(np.array(new_ImageNames))
        self.ImageTime_data.emit(np.array(ImageTime))
#        self.ImageIndex_data.emit(np.array(ImageIndex))
        
        #fps calculation
        print('calculate fps')
        DeltaT=np.array(ImageTime[1:])-np.array(ImageTime[:-1])
        invDeltaT=np.array([1./dt for dt in DeltaT])
        fps=np.mean(invDeltaT)
        self.fps_data.emit(fps)
        print('fps sent')
        
    def update_index(self,index):
        self.index_min=index[0]
        self.index_max=index[1]
        self.send_data()
        self.send_image_time()
        print('index refreshed')