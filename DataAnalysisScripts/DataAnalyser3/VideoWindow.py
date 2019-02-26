# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:36:28 2018

@author: Francois
"""

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg
import cv2 as cv2
import time as time

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
        
    def refresh_image(self, image_bgr):      
        image_rgb=cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_rgb=cv2.rotate(image_rgb,cv2.ROTATE_90_CLOCKWISE) #pgItem display the image with 90° anticlockwise rotation
        self.img.setImage(image_rgb)
        
        
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
    
    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)

        #Video parameters
        self.image_directory=''
        self.Time_Image=np.array([])
        self.Image_Names=[]
        
        self.timer=QtCore.QTimer()
        self.timer.setInterval(100) #in ms
        self.timer.timeout.connect(self.play_refresh)
        self.current_track_time=0
        self.current_computer_time=0
        self.isRecording=False
        
        #Gui Component
        
        self.image_widget=ImageWidget()
        
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
        layout.addWidget(self.image_widget)
        layout.addLayout(controlLayout)


        self.setLayout(layout)
        
    def refreshImage(self,image_name):
        file_directory= self.image_directory+image_name
        image=cv2.imread(file_directory)
        self.image_widget.refresh_image(image)
        self.imageName.emit(image_name)
        print('Image sent from VideoWindow: {}'.format(image_name))
        if self.isRecording:
            # Also send the image name of the image being emmited
           
            self.image_to_record.emit(image, image_name)
        
    def initialize_directory(self,directory):
        self.image_directory=directory+'/images/'
        
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
        if self.playButton.isChecked():
            self.playButton.setChecked(False)
            self.timer.stop()
            self.positionSlider.setEnabled(True)
            self.positionSpinBox.setEnabled(True)
            
        self.current_track_time=0
        self.current_computer_time=0
        self.positionSlider.setValue(0)
        self.positionSpinBox_prevValue=0
        self.positionSlider_prevValue=0
        
    def positionSpinBox_setValue(self,value):
        newvalue=self.Image_Time[value]
        self.positionSpinBox.setValue(newvalue)
        self.positionSlider_prevValue=value
        
    def positionSlider_setValue(self,value):
        newvalue,hasToChange=self.find_slider_index(value)
        if hasToChange:
            self.positionSlider.setValue(newvalue)
            self.positionSpinBox.setValue(self.Image_Time[newvalue])
            self.positionSpinBox_prevValue=self.Image_Time[newvalue]
            self.positionSlider_prevValue=newvalue
            self.refreshImage(self.Image_Names[newvalue])
            self.update_plot.emit(self.Image_Time[newvalue])
            self.update_3Dplot.emit(self.Image_Time[newvalue])
            
    def find_slider_index(self,value):
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
                

            
    def play(self):
        if self.playButton.isChecked():
            self.current_computer_time=time.time()
            self.current_track_time=self.positionSpinBox_prevValue
            self.timer.start(0)
            self.positionSlider.setEnabled(False)
            self.positionSpinBox.setEnabled(False)
        else:
            self.timer.stop()
            self.positionSlider.setEnabled(True)
            self.positionSpinBox.setEnabled(True)
            
    
    def play_refresh(self):
        timediff=time.time()-self.current_computer_time
        
        index=np.argmin(abs(self.Image_Time-(timediff+self.current_track_time)))
        if index>self.positionSlider_prevValue:
            self.current_computer_time+=timediff
            self.current_track_time+=timediff
            self.positionSlider.setValue(index)
            
            
            
    def record(self):
        self.isRecording=self.recordButton.isChecked()
        self.record_signal.emit(self.isRecording)
        print('start-recording-signal')
            
