# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:36:28 2018

@author: Francois & Deepak
"""

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg
import cv2 as cv2
import time as time
import os


font = cv2.FONT_HERSHEY_SIMPLEX

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                         Image_Widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
''' 
   
class ImageWidget(pg.GraphicsLayoutWidget):
    
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view=self.addViewBox()
        
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img=pg.ImageItem(border='w')
        self.view.addItem(self.img)

        

        
#    def refresh_image(self, image_bgr): 
#
#        image_gray=cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
#
#        image_gray=cv2.rotate(image_gray,cv2.ROTATE_90_CLOCKWISE) #pgItem display the image with 90° anticlockwise rotation
#        
#        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(6,6))
#                
#        image_gray = clahe.apply(image_gray)
#        
#        self.img.setImage(image_gray)
        
    

#    def update_clahe(self):
#        # Update clahe parameters
#        self.clahe = cv2.createCLAHE(clipLimit = self.clahe_cliplimit, tileGridSize = (6,6))


        
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Video_widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''         

class VideoWindow(QtWidgets.QWidget):
    
    update_plot=QtCore.pyqtSignal(float)
    update_3Dplot=QtCore.pyqtSignal(float)
    imageName=QtCore.pyqtSignal(str)
    record_signal=QtCore.pyqtSignal(bool)
    image_to_record=QtCore.pyqtSignal(np.ndarray, str)
    
    def __init__(self, PixelPermm = 314, parent=None):
        super(VideoWindow, self).__init__(parent)

        #Video parameters
        self.image = None
        self.image_directory=''
        # Dictionary containing the subfolder address of all images
        self.image_dict = {}
        self.Time_Image=np.array([])
        self.Image_Names=[]
        self.Image_Time = []
        self.LED_intensity = []
        self.imW = 0
        self.imH = 0
        self.PixelPermm = PixelPermm
        
        self.Xobj_image = []
        self.Zobj_image = []
        
        self.grayscale = True
        # Image contrast settings
        # Contrast factor for image
        self.clahe_cliplimit = 8

        # Create a CLAHE object 
        self.clahe = cv2.createCLAHE(clipLimit = self.clahe_cliplimit, tileGridSize = (6,6))

        # Font and Font position parameters for annotating images
        # Settings for 720p images
        # self.scalebarSize = 20
        # self.baseFontScale = 0.01
        # self.timeStampPos_base = (20, 40)
        # self.scaleBar_textOffset_base = (180,25)

        self.scalebarSize = 250
        self.baseFontScale = 1
        self.timeStampPos_base = (20,50)
        self.scaleBar_textOffset_base = (220,25)

        self.newData = True

        
        self.timer=QtCore.QTimer()
        self.timer.setInterval(0) #in ms
        self.timer.timeout.connect(self.play_refresh)
        self.current_track_time=0
        self.current_computer_time=0
        
        self.current_track_index = 0        # Add image index
        self.prev_track_index = 0    
         
        self.isRecording=False
        
        # If true then plays the data in real-time
        self.real_time = True
        # No:of frames to advance for recording purposes
        self.frames = 3
        # This gives playback_speed x normal speed
        self.playback_speed = 1
        #Gui Component
        
        self.add_components()

    def add_components(self):

        # Widgets
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.view = self.graphics_widget.addViewBox()
        ## lock the aspect ratio so pixels are always square
        self.graphics_widget.view.setAspectLocked(True)
        ## Create image item
        self.graphics_widget.img=pg.ImageItem(border='w')
        self.graphics_widget.view.addItem(self.graphics_widget.img)
        
        self.playButton = QtGui.QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setCheckable(True)
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.recordButton = QtGui.QPushButton()
        self.recordButton.setEnabled(False)
        self.recordButton.setCheckable(True)
        self.recordButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton))
        self.recordButton.clicked.connect(self.record)

        self.positionSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setEnabled(False)
        self.positionSlider_prevValue=0
        
        self.positionSpinBox=QtGui.QDoubleSpinBox()
        self.positionSpinBox.setRange(0, 0)
        self.positionSpinBox.setSingleStep(0.01)
        self.positionSpinBox.setEnabled(False)
        self.positionSpinBox_prevValue=0
        
        # Connections
        self.positionSlider.valueChanged.connect(self.positionSpinBox_setValue)
        self.positionSpinBox.valueChanged.connect(self.positionSlider_setValue)

        # Create layouts to place inside widget
        controlLayout = QtGui.QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.positionSpinBox)
        controlLayout.addWidget(self.recordButton)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.graphics_widget)
        layout.addLayout(controlLayout)


        self.setLayout(layout)
        
    def refreshImage(self,image_name):
        # Changed so that it can handle images being split among multiple sub-directories.
        file_directory= os.path.join(self.image_directory, self.image_dict[image_name],image_name)

        # print(file_directory)
        self.image = cv2.imread(file_directory)
        if(self.imW==0 or self.imH ==0 or self.newData==True):
            self.imH, self.imW,*rest = np.shape(self.image)
            print(np.shape(self.image))
            print(self.imH, self.imW)
            self.newData = False
            
        self.apply_clahe()
        self.add_annotation()

        self.image = cv2.rotate(self.image,cv2.ROTATE_90_CLOCKWISE) #pgItem display the self.image with 90° anticlockwise rotation
        self.graphics_widget.img.setImage(self.image)

        self.imageName.emit(image_name)
        if self.isRecording:
            # print('Current Image : {}'.format(image_name))
            self.image_to_record.emit(self.image, image_name)

    def apply_clahe(self):
         # Apply contrast enhancement
        if(self.grayscale is True):
            image_gs = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.image = self.clahe.apply(image_gs)
            
        else:
            # Convert from BGR to LAB colorspace
            image_lab = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
            
            # Split the LAB self.image into individual channels
            L,A,B = cv2.split(image_lab)
            
            # Apply CLAHE contrast enhancement 
            CL = self.clahe.apply(L)
        
            image_lab = cv2.merge((CL,A,B))
        
            self.image = cv2.cvtColor(image_lab, cv2.COLOR_LAB2RGB)

    def add_annotation(self):

        if(len(self.Image_Time)!= 0):
            currTime = self.Image_Time[self.current_track_index]

            #            centroid = [int(self.imW/2) + self.Xobj_image[self.current_track_index], int(self.imH/2) - self.Zobj_image[self.current_track_index]]


            #            cv2.circle(self.image,(centroid[0],centroid[1]), 15, (255,255,255), 3)
            # print('Current self.image Time: {}'.format(currTime))
            cv2.putText(self.image, '{:.2f}'.format(np.round(currTime, decimals = 2))+'s', self.timeStampPosition(), font, self.fontScale(), (255, 255, 255), 2, cv2.LINE_AA)

            # if(LED_intensity>0):
            #     cv2.putText(self.image, 'Light ON', (580, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # else:
            #     cv2.putText(self.image, 'Light OFF', (580, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


            x_start = self.imW - int((self.scalebarSize/1000)*(self.PixelPermm))-self.scaleBar_offset()
            y_start = self.imH - self.scaleBar_offset()
            x_end = self.imW - self.scaleBar_offset()
            y_end = y_start

            scaleBar_text_offset = self.scaleBar_text_offset()

            cv2.putText(self.image, '{:d}'.format(self.scalebarSize)+'um', (int(x_end)-scaleBar_text_offset[0], y_start - scaleBar_text_offset[1]), font, self.fontScale(), (255, 255, 255), 2, cv2.LINE_AA)

            cv2.line(self.image, (x_start, y_start), (x_end, y_end), color =(255,255,255), thickness = int(self.imH*5/720),lineType = cv2.LINE_AA)
        
    def initialize_directory(self,directory, image_dict):
        # Making this more robust by passing the actual folder name containing images instead of assuming they are in /images/

        # This is the root directory containing the dataset
        self.image_directory=directory

        # This is the dictionary which contains the subdirectory address for all images.
        self.image_dict = image_dict

    def initialize_image_names(self,image_names):
        self.Image_Names=image_names
        
        if len(self.Image_Names)>0:
            self.refreshImage(self.Image_Names[0])
 
    def initialize_image_time(self,image_time):
        self.Image_Time=image_time
        self.positionSlider.setRange(0,len(self.Image_Time)-1)
        self.positionSlider.setEnabled(True)
        self.positionSpinBox.setRange(self.Image_Time[0],self.Image_Time[-1])
        self.positionSpinBox.setEnabled(True)
        
    def initialize_parameters(self):
        # Flag set to true when a new dataset is opened
        self.newData = True
        print('In initialize parameters')
        print(self.newData)
        if self.playButton.isChecked():
            self.playButton.setChecked(False)
            self.timer.stop()
            self.positionSlider.setEnabled(True)
            self.positionSpinBox.setEnabled(True)
            
        self.current_track_index = 0
        self.current_track_time=0
        self.current_computer_time=0
        self.positionSlider.setValue(0)
        self.positionSpinBox_prevValue=0
        self.positionSlider_prevValue=0

    def initialize_obj_centroids(self, Xobj_image, Zobj_image):
        self.Xobj_image = Xobj_image
        self.Zobj_image = Zobj_image
        
        print('Initialized object centroids')
        
    def positionSpinBox_setValue(self,value):
        newvalue=self.Image_Time[value]
        self.positionSpinBox.setValue(newvalue)
        self.positionSlider_prevValue=value
        
    def positionSlider_setValue(self,value):
        newvalue, hasToChange=self.find_slider_index(value)
       
        self.current_track_index = newvalue
        if hasToChange:
            self.positionSlider.setValue(newvalue)
            self.positionSpinBox.setValue(self.Image_Time[newvalue])
            self.positionSpinBox_prevValue=self.Image_Time[newvalue]
            
#            self.prev_track_index = newvalue
#            self.prev_track_index = self.Image_Index[newvalue]
            
            self.positionSlider_prevValue=newvalue
            self.refreshImage(self.Image_Names[newvalue])
            self.update_plot.emit(self.Image_Time[newvalue])
            self.update_3Dplot.emit(self.Image_Time[newvalue])
                
    def find_slider_index(self,value):
        #
        index=0
        found=False
        hasToChange=True
        
        if self.positionSpinBox_prevValue<value: 
            for i in range(0,len(self.Image_Time)):
                if self.Image_Time[i]-value>=0 and not(found):
                    index=i
                    found=True
            if not(found):
                index=len(self.Image_Time)-1
                
        elif self.positionSpinBox_prevValue>value:
            for i in range(len(self.Image_Time)-1,-1,-1):
                if self.Image_Time[i]-value<=0 and not(found):
                    index=i
                    found=True
            if not(found):
                index=0
        else:
            hasToChange=False
            
        return index,hasToChange
            
           
    def update_playback_speed(self, newvalue):
        self.playback_speed = newvalue

    def play(self):
        if self.playButton.isChecked():
            self.current_computer_time = time.time()
            self.current_track_time = self.positionSpinBox_prevValue
            # Set the prev index to the current index
            self.prev_track_index = self.current_track_index
            self.timer.start(0)
            self.positionSlider.setEnabled(False)
            self.positionSpinBox.setEnabled(False)
        else:
            self.timer.stop()
            self.positionSlider.setEnabled(True)
            self.positionSpinBox.setEnabled(True)
            
    def record(self):
        self.isRecording=self.recordButton.isChecked()
        self.record_signal.emit(self.isRecording)
        print('start-recording-signal')
    
    def play_refresh(self):
        
        if self.real_time:
            timediff = time.time()-self.current_computer_time

            timediff_scaled = self.playback_speed*timediff
            
            index = np.argmin(abs(self.Image_Time-(timediff_scaled+self.current_track_time)))

            if index>self.positionSlider_prevValue:
                self.current_computer_time += timediff
                self.current_track_time += timediff_scaled
                self.positionSlider.setValue(index)
                
        else:
            
            self.current_track_index = self.prev_track_index + self.frames
        
            self.positionSlider.setValue(self.current_track_index)
            
            self.prev_track_index = self.current_track_index

    def update_pixelsize(self, PixelPermm):
        self.PixelPermm = PixelPermm

    def scaleBar_offset(self):
        return int(20*self.imW/720)

    def fontScale(self):
        return max(int(0.75*self.baseFontScale*self.imW/720),1) 

    def timeStampPosition(self):
        return (int((self.imW/720)*self.timeStampPos_base[0]), int((self.imW/720)*self.timeStampPos_base[1]))

    def scaleBar_text_offset(self):
        return (int(max((self.imW/1920),0.5)*self.scaleBar_textOffset_base[0]), int((self.imW/1920)*self.scaleBar_textOffset_base[1]))