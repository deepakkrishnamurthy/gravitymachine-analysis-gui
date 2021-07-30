# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:28:21 2018

@author: Francois, Deepak
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:28:21 2018

@author: Francois
"""
import csv as csv
import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import os
import pandas as pd
from _def import VARIABLE_HEADER_MAPPING

'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                             CSV reader
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CSV_Reader(QtCore.QObject):
    
    Time_data = QtCore.pyqtSignal(np.ndarray)
    fps_data = QtCore.pyqtSignal(float)
    Xobj_data = QtCore.pyqtSignal(np.ndarray)
    Yobj_data = QtCore.pyqtSignal(np.ndarray)
    Zobj_data = QtCore.pyqtSignal(np.ndarray)
    ObjLoc_data = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    ImageNames_data = QtCore.pyqtSignal(np.ndarray)
    ImageTime_data = QtCore.pyqtSignal(np.ndarray)
    LED_intensity_data = QtCore.pyqtSignal(np.ndarray)
    pixelpermm_data = QtCore.pyqtSignal(float)
    objective_data = QtCore.pyqtSignal(str)
#    ImageIndex_data = QtCore.pyqtSignal(np.ndarray)
    
    
    def __init__(self, parent=None, flip_z = False):
        super(CSV_Reader, self).__init__(parent)
        # File name for .csv file is now auto-detected
        self.file_name=''

        self.data = {key: np.array([]) for key in VARIABLE_HEADER_MAPPING}

        self.Time=np.array([])
        self.X_obj=np.array([])
        self.Y_obj=np.array([])
        self.Z_obj=np.array([])
        self.ImageNames=np.array([])
        self.index_min=0
        self.index_max=0
        self.df = None
        self.metadata = None
        self.flip_z = flip_z
    
    
    def computeSpeed(self,X,T):
        V=[]
        for i in range(1,len(T)-1):
            deltaT=T[i+1]-T[i-1]
            V.append((X[i+1]-X[i-1])/deltaT)
        
    
    def open_newCSV(self,directory, trackFile, Tmin = None, Tmax = None):

        Data=[]
        self.file_name = trackFile
        self.directory = directory
        
        trackPath = os.path.join(directory, self.file_name)
        
        # Read the data
        self.df = pd.read_csv(trackPath)
        
        try:
            self.metadata = pd.read_csv(os.path.join(directory, 'metadata.csv'))
        except:
            print("Metadata file not found")
        
        self.df[VARIABLE_HEADER_MAPPING['Time']] = self.df[VARIABLE_HEADER_MAPPING['Time']] - self.df[VARIABLE_HEADER_MAPPING['Time']][0]
        if(Tmax == 0 or Tmax is None):
            Tmax = np.max(self.df[VARIABLE_HEADER_MAPPING['Time']])
        
        if(Tmin is not None and Tmax is not None):
            # Crop the trajectory
            self.df = self.df.loc[(self.df[VARIABLE_HEADER_MAPPING['Time']]>=Tmin) & (self.df[VARIABLE_HEADER_MAPPING['Time']] <= Tmax)]
            self.df = self.df[1:]

        self.ColumnNames = list(self.df.columns.values)

        for key in VARIABLE_HEADER_MAPPING:
            if(VARIABLE_HEADER_MAPPING[key] in self.ColumnNames):
                self.data[key] = np.array(self.df[VARIABLE_HEADER_MAPPING[key]])
            else:
                print('Warning {} not found in input data'.format(key))
                self.data[key] = None

   
        self.index_min=0
        self.index_max=len(self.df)-1
        
        #send data on T, X,Y,Z to the plot, depending on the index range chosen        
        self.send_data()
        
        self.send_metadata()
        #Time and name of the image for the video reader
        self.send_image_time()
        

        
    def send_data(self):
    
        self.Time_data.emit(self.data['Time'][self.index_min:self.index_max+1])
        self.Xobj_data.emit(self.data['X_obj'][self.index_min:self.index_max+1])
        self.Yobj_data.emit(self.data['Y_obj'][self.index_min:self.index_max+1])
        self.Zobj_data.emit(self.data['Z_obj'][self.index_min:self.index_max+1])
        if(self.data['X_image'] is not None and self.data['Z_image'] is not None):
                self.ObjLoc_data.emit(self.data['X_image'][self.index_min:self.index_max+1], self.data['Z_image'][self.index_min:self.index_max+1])
        print('data sent')
        
    def send_metadata(self):
        if(self.metadata is not None):
            self.pixelpermm_data.emit(float(self.metadata['PixelPermm'][0]))
            self.objective_data.emit(str(self.metadata['Objective'][0]))
        else:
            pass
        
    def send_image_time(self):
        cropped_ImageNames = self.data['Image name'][self.index_min:self.index_max+1]
        cropped_Time=self.data['Time'][self.index_min:self.index_max+1]
        # cropped_LED_intensity = self.LED_intensity[self.index_min:self.index_max+1]
        
        ImageTime=[]
        new_ImageNames=[]
        ImageIndex = []
        # new_LED_intensity = []
        
        for i in range(len(cropped_ImageNames)):
            if cropped_ImageNames[i] is not np.nan:
                ImageIndex.append(i)
                new_ImageNames.append(cropped_ImageNames[i])
                ImageTime.append(round(cropped_Time[i],2))
                # new_LED_intensity.append(cropped_LED_intensity[i])
                
        # Checking to see if images are updated for a new dataset
        
        # print('New Starting Image: {}'.format(new_ImageNames[0]))

        self.ImageNames_data.emit(np.array(new_ImageNames))
        self.ImageTime_data.emit(np.array(ImageTime))
        # self.LED_intensity_data.emit(np.array(new_LED_intensity))
        
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