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
#                            Video_widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''         

class VideoWindow(QtWidgets.QWidget):
    
    update_plot=QtCore.pyqtSignal(float)
    update_3Dplot=QtCore.pyqtSignal(float)
    imageName=QtCore.pyqtSignal(str)
    record_signal=QtCore.pyqtSignal(bool)
    image_to_record=QtCore.pyqtSignal(np.ndarray, str)

    roi_circle_pos_signal = QtCore.pyqtSignal(int, int)
    roi_circle_size_signal = QtCore.pyqtSignal(int)
    
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
        
        self.n_features = 3    # No:of features we want to track at the same time
        self.track_ids = [ii for ii in range(self.n_features)]
        self.tracker_type_feature = "CSRT"
        
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
        self.frames_stride = 10
        # This gives playback_speed x normal speed
        self.playback_speed = 1
        
        # Tracking related
        self.tracking_flag = False
        self.tacking_init_flag = False
        self.tracking_data_available = False
        self.tracking_data = None
        
        self.add_components()

    def add_components(self):

        # Widgets
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.view = self.graphics_widget.addViewBox()
        ## lock the aspect ratio so pixels are always square
        self.graphics_widget.view.setAspectLocked(True)
        ## Create image item
        self.graphics_widget.img = pg.ImageItem(border='w', axisOrder = 'row-major')
        self.graphics_widget.view.addItem(self.graphics_widget.img)
        self.graphics_widget.view.invertY()

        
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

        
        # ROIs
        self.add_circular_roi()
        self.add_rectangular_rois()

        # Tracking
        self.initialize_track_variables()
        
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
        self.image_raw = np.copy(self.image)    # Store a copy of the raw image

        # Run the tracking if run_tracking_flag is true\
        if(self.tracking_flag == True):
            self.track()
        else:
            pass

        self.add_annotation()

        # self.image = cv2.rotate(self.image,cv2.ROTATE_90_CLOCKWISE) #pgItem display the self.image with 90° anticlockwise rotation
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
            self.current_track_index = self.prev_track_index + self.frames_stride
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
    # -----------------------------------------------------------------------------------------------------------------------------------
    # ROI related functions
    # -----------------------------------------------------------------------------------------------------------------------------------
    def add_circular_roi(self):
        # Add circular ROI for finding the approximate centroid of the object
        self.roi_circle_pos = (self.imW/2, self.imH/2)
        self.roi_circle_size = (300, 300)

        self.ROI_circle = pg.CircleROI(self.roi_circle_pos, self.roi_circle_size, scaleSnap = True, translateSnap = True, pen = 'y')
        # self.ROI_circle.addScalehandle((0,0),(1,1))
        self.graphics_widget.view.addItem(self.ROI_circle)
        self.ROI_circle.hide()
        self.ROI_circle.sigRegionChanged.connect(self.update_ROI_circle)
        self.roi_circle_pos = self.ROI_circle.pos()
        self.roi_circle_size = self.ROI_circle.size()

    def add_rectangular_rois(self):
        # Add rectangular ROIs for choosing the features
        self.ROI = {}
        self.roi_size = (50,50)

        self.roi_pos = [((1 + ii)/self.n_features*self.imW/2 , (1+ii)/self.n_features*self.imH/2) for ii in range(self.n_features)] 
        for index in range(self.n_features):
        
            self.ROI[index] = pg.ROI(self.roi_pos[index], self.roi_size, scaleSnap=True, translateSnap=True, pen = 'r')
            self.ROI[index].setZValue(10)
            self.ROI[index].addScaleHandle((0,0), (1,1))
            self.ROI[index].addScaleHandle((1,1), (0,0))
            self.graphics_widget.view.addItem(self.ROI[index])
            self.ROI[index].hide()
            self.ROI[index].sigRegionChanged.connect(self.update_ROI)
            # self.roi_pos = self.ROI.pos()
            # self.roi_size = self.ROI.size()

        self.roi_size = (300,300)
        # Add a separate ROI to handle tracking of the whole object
        self.ROI['object'] = pg.ROI((self.imW/2, self.imH/2), self.roi_size, scaleSnap=True, translateSnap=True, pen = 'g')
        self.ROI['object'].setZValue(10)
        self.ROI['object'].addScaleHandle((0,0), (1,1))
        self.ROI['object'].addScaleHandle((1,1), (0,0))
        self.graphics_widget.view.addItem(self.ROI['object'])
        self.ROI['object'].hide()
        self.ROI['object'].sigRegionChanged.connect(self.update_ROI)

    def update_ROI(self):
        
        # Update the initial bounding boxes based on user's selected bbox.
        for ii in self.track_ids:

            roi_pos = self.ROI[ii].pos()
            roi_size = self.ROI[ii].size()

            self.bbox_init[ii] = (roi_pos[0], roi_pos[1], roi_size[0], roi_size[1])
            print('Updated bbox feature {} to: {}'.format(ii, self.bbox_init[ii]))

        roi_pos = self.ROI['object'].pos()
        roi_size = self.ROI['object'].size()

        self.bbox_object_init = (roi_pos[0], roi_pos[1], roi_size[0], roi_size[1])
        print('Updated bbox object to: {}'.format(self.bbox_object_init))

    def update_ROI_circle(self):
        self.roi_circle_pos = self.ROI_circle.pos()
        self.roi_circle_size = self.ROI_circle.size()

        self.send_roi_circle_data()

    def toggle_ROI_circle(self, flag):

        if(flag == True):
            self.ROI_circle.show()
        else:
            self.ROI_circle.hide()

    def toggle_ROI(self, flag):
        if(flag == True):
            for ii in self.track_ids:
                self.ROI[ii].show()
        else:
            for ii in self.track_ids:
                self.ROI[ii].hide()

    def toggle_ROI_object(self, flag):
        if(flag == True):
            self.ROI['object'].show()
        else:
            self.ROI['object'].hide()

    def send_roi_circle_data(self):

        roi_width = self.roi_circle_size[0]
        roi_height = self.roi_circle_size[1]

        roi_radius = (roi_width + roi_height)/2.0

        roi_center_x = int(self.roi_circle_pos[0] + roi_width/2.0)
        roi_center_y = int(self.roi_circle_pos[1] + roi_height/2.0)

        self.true_centroid_object_X, self.true_centroid_object_Z = roi_center_x, roi_center_y

        self.roi_circle_pos_signal.emit(roi_center_x, roi_center_y)
        self.roi_circle_size_signal.emit(int(roi_radius))
    #------------------------------------------------------------------------------------------------------------------------------------
    # Tracking related functions
    #------------------------------------------------------------------------------------------------------------------------------------
    def initialize_track_variables(self):
        self.Timestamp_array = []
        self.track_id_array = []
        self.bbox = {}
        self.bbox_init = {}
        self.tracker_instance = {}
        self.tracker_flag = {}
        self.centroids = {}
        self.centroids_x_array = {}
        self.centroids_y_array = {}
        self.image_names = []
        self.true_centroid_object_X = None
        self.true_centroid_object_Z = None
        self.true_centroid_object_X_array = []
        self.true_centroid_object_Z_array = []
        self.bbox_object = None
        self.bbox_object_init = None
        self.centroids_object_curr = None
        self.centroids_object_prev = None


        self.add_object_tracker()
        for ii in self.track_ids:    # Allocate dicts to store the tracks
            self.add_new_dict_entry(ii)

    def toggle_tracking(self, flag):

        if(flag == True):
            # Start tracking
            self.tracking_data_available = False
            self.tracking_data = None
            self.initialize_object_tracker()
            self.initialize_feature_tracker()
            self.tracking_flag = True
            self.real_time = False  # Disable real-time playing since we may want to skip frames for tracking 
            # Start the timer
            self.playButton.setChecked(True)
            self.play()
        else:
            self.real_time = True
            self.tracking_flag = False
            self.playButton.setChecked(False)
            self.play()
            # Tracking data available flag
            if(self.tracking_data is not None):
                self.tracking_data_available = True

    def add_new_dict_entry(self, track_id):
    
        self.bbox[track_id] = []
        
        if self.tracker_type_feature == 'BOOSTING':
            self.tracker_instance[track_id] = cv2.TrackerBoosting_create()
        if self.tracker_type_feature == 'MIL':
            self.tracker_instance[track_id] = cv2.TrackerMIL_create()
        if self.tracker_type_feature == 'KCF':
            self.tracker_instance[track_id] = cv2.TrackerKCF_create()
        if self.tracker_type_feature == 'TLD':
            self.tracker_instance[track_id] = cv2.TrackerTLD_create()
        if self.tracker_type_feature == 'MEDIANFLOW':
            self.tracker_instance[track_id] = cv2.TrackerMedianFlow_create()
        if self.tracker_type_feature == 'GOTURN':
            self.tracker_instance[track_id] = cv2.TrackerGOTURN_create()
        if self.tracker_type_feature == 'MOSSE':
            self.tracker_instance[track_id] = cv2.TrackerMOSSE_create()
        if self.tracker_type_feature == "CSRT":
            self.tracker_instance[track_id] = cv2.TrackerCSRT_create()
            
        self.tracker_flag[track_id] = 0
        self.centroids [track_id] = []
        self.centroids_x_array[track_id] = []
        self.centroids_y_array[track_id] = []

    def add_object_tracker(self):
        # Create a separate tracker for detecting the centroid of the sphere
        self.tracker_object = cv2.TrackerKCF_create()
        self.tracker_object_flag = None
        # self.bbox_object = None
        # self.bbox_object_init = None

    def initialize_object_tracker(self):
        
        self.tracker_object_flag = self.tracker_object.init(self.image_raw, self.bbox_object_init)
        x_pos_object = self.bbox_object_init[0] + self.bbox_object_init[2]/2
        y_pos_object = self.bbox_object_init[1] + self.bbox_object_init[3]/2
        self.centroid_object_curr = np.array([x_pos_object, y_pos_object])

    def initialize_feature_tracker(self):
        # Choose the initial bounding boxes to start the tracking
        for ii in range(self.n_features):

            print('bbox {} chosen as {}'.format(ii, self.bbox_init[ii]))
            
             # Initialize tracker with first frame and bounding box
            self.tracker_flag[ii] = self.tracker_instance[ii].init(self.image_raw, self.bbox_init[ii])

    def track(self):

        self.curr_time = self.Image_Time[self.current_track_index]

        self.Timestamp_array.append(self.curr_time)

        # Update the tracker for the whole sphere
        self.tracker_object_flag, self.bbox_object = self.tracker_object.update(self.image_raw)
    
        # Update tracker
        for ii in self.track_ids:
            self.tracker_flag[ii], self.bbox[ii] = self.tracker_instance[ii].update(self.image_raw)

        if(self.tracker_object_flag):
        # Sphere center successfully tracked
        
            self.centroid_object_prev =  self.centroid_object_curr
            x_pos_sphere = self.bbox_object[0] + self.bbox_object[2]/2
            y_pos_sphere = self.bbox_object[1] + self.bbox_object[3]/2
            self.centroid_object_curr = np.array([x_pos_sphere, y_pos_sphere])
            
            print('Detected object centroid: {}'.format(self.centroid_object_curr))

            centroid_object_disp = self.centroid_object_curr - self.centroid_object_prev
            
            print('Object disp vector: {}'.format(centroid_object_disp))
            
            self.true_centroid_object_X += centroid_object_disp[0]
            self.true_centroid_object_Z += centroid_object_disp[1]
            
            self.true_centroid_object_X_array.append(self.true_centroid_object_X)
            self.true_centroid_object_Z_array.append(self.true_centroid_object_Z)
            
            p1 = (int(self.bbox_object[0]), int(self.bbox_object[1]))
            p2 = (int(self.bbox_object[0] + self.bbox_object[2]), int(self.bbox_object[1] + self.bbox_object[3]))
            cv2.rectangle(self.image, p1, p2, (255,255,255), 3, 2)
            print(p1, p2)
            print('Tracking whole sphere succesfully')
        else:
            print('Warning: Failure detected in tracking of whole sphere...')

        for jj, ii in enumerate(self.track_ids):
        # Draw bounding box
            if self.tracker_flag[ii]:
                # Tracking success
                  # Calculate the center of the bounding box and store it
            
                x_pos = self.bbox[ii][0] + self.bbox[ii][2]/2
                y_pos = self.bbox[ii][1] + self.bbox[ii][3]/2
                self.centroids[ii] = (x_pos, y_pos)
                self.centroids_x_array[ii].append(x_pos)
                self.centroids_y_array[ii].append(y_pos)
                
                p1 = (int(self.bbox[ii][0]), int(self.bbox[ii][1]))
                p2 = (int(self.bbox[ii][0] + self.bbox[ii][2]), int(self.bbox[ii][1] + self.bbox[ii][3]))

                # print('Tracked bbox for feature {}: {}'.format(ii, self.bbox[ii]))

                cv2.rectangle(self.image, p1, p2, (255,255,255), 2, 1)
                print('Tracking # {} succesfully'.format(ii))
            else :
                # Tracking failure
                print('Tracking failure for feature: {}'.format(ii))
                pass
                # cv2.putText(image, "Tracking failure detected for {}".format(ii), (100+20*jj,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2)
                
                # # Show the last detected bbox on the image
                # p1 = (int(bbox[ii][0]), int(bbox[ii][1]))
                # p2 = (int(bbox[ii][0] + bbox[ii][2]), int(bbox[ii][1] + bbox[ii][3]))
                # cv2.rectangle(image_raw, p1, p2, (255,0,0), 2, 1)
                
                # # Choose a new point to track
                # new_id = max(track_ids)+1
                # track_ids.append(new_id)
                # add_new_dict_entry(new_id)
                
                # bbox[new_id] = cv2.selectROI("Choose bbox for new track {}".format(new_id), image_raw, False)
                # key = cv2.waitKey(0)

        
    # def save_tracking_data(self, track_id):
    #     self.tracking_data = pd.DataFrame({'track ID':[], 'feature ID':[], 'Time':[], 'feature centroid X':[], 'feature centroid Z':[], 'sphere centroid X':[], 'sphere centroid Z':[]})
    #     for ii in range(self.n_features):
    #         self.tracking_data = data.append(pd.DataFrame({'track ID':np.repeat(track_id, len(self.centroids_x_array[ii]), axis = 0), 'feature ID':np.repeat(ii, len(self.centroids_x_array[ii]), axis = 0), 'Time': self.Timestamp_array, 'feature centroid X': self.centroids_x_array[ii], 'feature centroid Z': self.centroids_y_array[ii], 'sphere centroid X': self.true_centroid_sphere_X_array, 'sphere centroid Z': self.true_centroid_sphere_Z_array }))
    #     self.tracking_data.to_csv(os.path.join(track_id +'_' + self.Timestamp_array.min() + '_' + self.Timestamp_array.max()+'.csv'))

