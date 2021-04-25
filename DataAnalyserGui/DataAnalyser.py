# -*- coding: utf-8 -*-
import sys
import os

import cv2
import numpy as np
import pandas as pd

from pyqtgraph.Qt import QtWidgets,QtCore, QtGui #possible to import form PyQt5 too ... what's the difference? speed? 
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

from CSV_Reader import CSV_Reader
from plot3D import plot3D_widget
from VideoWindow import VideoWindow
from PlotWidget import PlotWidget
from VideoSaver import VideoSaver
from AnalysisWidget import AnalysisWidget
from _def import VARIABLE_HEADER_MAPPING

from aqua.qsshelper import QSSHelper

                   
# Testing to see branch changes
 
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Central Widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CentralWidget(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        # widgets
        self.video_window=VideoWindow(PixelPermm = 314)
        self.fps=None #fps for saving
        self.xplot = PlotWidget('X displacement', label = 'X',color ='r')
        self.yplot = PlotWidget('Y displacement', label = 'Y',color ='g')
        self.zplot = PlotWidget('Z displacement', label = 'Z',color =(50, 100, 255))

        self.plot3D_widget = plot3D_widget()

        self.AnalysisWidget = AnalysisWidget()
        # controller

        self.video_saver=VideoSaver()
        self.isImageSaver=False  #True: image_saver will be chose in place of video saver

        self.csv_reader=CSV_Reader(flip_z = False)
        #----------------------------------------------------------------------
        # Toggle Comment/Uncomment to turn Z-plot ON and OFF
        #----------------------------------------------------------------------
        # VERTICAL LAYOUT ON THE LEFT
        
        v_left_layout=QtGui.QVBoxLayout()
        v_left_layout.addWidget(self.video_window)
        
        v_right_layout = QtGui.QVBoxLayout()
        v_right_layout.addWidget(self.plot3D_widget)
        # Comment/Uncomment below to remove the image analysis widget
        v_right_layout.addWidget(self.AnalysisWidget)
        # v_right_layout=QtGui.QVBoxLayout()
        # v_right_layout.addWidget(self.xplot)
        # v_right_layout.addWidget(self.yplot)
        # v_right_layout.addWidget(self.zplot)

        # v_right_layout.setStretchFactor(self.xplot,1)
        # v_right_layout.setStretchFactor(self.yplot,1)
        # v_right_layout.setStretchFactor(self.zplot,1)
        h_layout = QtGui.QHBoxLayout()
        h_layout.addLayout(v_left_layout)
#        h_layout.addLayout(v_right_layout)
        h_layout.addLayout(v_right_layout)

#        h_layout.addLayout(v_layout)
#        h_layout.addLayout(plot3D_layout)
        
        h_layout.setStretchFactor(v_left_layout,1)
#        h_layout.setStretchFactor(v_right_layout,1)
        h_layout.setStretchFactor(v_right_layout,1)
        # Final action     
#        self.setLayout(v_layout)
        self.setLayout(h_layout)
        
    def update_recording_fps(self,fps):
        self.fps=np.round(fps,2)
        
    def record_change(self,isRecording):
        self.isRecording=isRecording
        if isRecording:
            options_recording = options_Recording()
            options_recording.recording_instructions.connect(self.create_video)
            options_recording.exec_()
        else:
            self.terminate_video()
            
    def create_video(self,recording_instructions):
        self.folder_path=recording_instructions.folder_path
        print(self.folder_path)
        self.quality=recording_instructions.quality
        print(self.quality)
        self.isImageSaver=recording_instructions.isImageSaver
        print(self.isImageSaver)
        
        if self.isImageSaver:
            self.image_saver.start(self.folder_path,self.fps)
        else:
            self.video_saver.start(self.folder_path,self.fps)
        
    def add_frame(self,img, image_name): #img is the trigger for adding a new image
        print('try add frame')
        plotx=self.xplot.export_plot(self.quality)
        ploty=self.yplot.export_plot(self.quality)
        plotz=self.zplot.export_plot(self.quality)
        print('try 2')
        plot3d=self.plot3D_widget.plot3D.export_plot(self.quality)
        print('koik')
        if self.isImageSaver:
            self.image_saver.register(image_name, img,plotx,ploty,plotz,plot3d)
        else:
            self.video_saver.register(img,plotx,ploty,plotz,plot3d)
        print('images added')
        
    def add_name(self,imgName):
        if self.isImageSaver:
            self.image_saver.register_name(imgName)
        
    def terminate_video(self):
        if self.isImageSaver:
            self.image_saver.wait() #all element in the queue should be processed
            self.image_saver.stop() #release the video
        else:
            self.image_saver.wait() #all element in the queue should be processed
            self.video_saver.stop() #release the video

    def connect_all(self):
        
        self.csv_reader.Time_data.connect(self.xplot.update_Time)
        self.csv_reader.Time_data.connect(self.yplot.update_Time)
        self.csv_reader.Time_data.connect(self.zplot.update_Time)
        
        self.csv_reader.Xobj_data.connect(self.xplot.update_plot)
        self.csv_reader.Yobj_data.connect(self.yplot.update_plot)
        self.csv_reader.Zobj_data.connect(self.zplot.update_plot)
        self.csv_reader.fps_data.connect(self.update_recording_fps)
        
        self.csv_reader.Time_data.connect(self.plot3D_widget.plot3D.update_Time)
        self.csv_reader.Xobj_data.connect(self.plot3D_widget.plot3D.update_X)
        self.csv_reader.Yobj_data.connect(self.plot3D_widget.plot3D.update_Y)
        self.csv_reader.Zobj_data.connect(self.plot3D_widget.plot3D.update_Z)
        
        self.csv_reader.ImageTime_data.connect(self.video_window.initialize_image_time)
        self.csv_reader.ObjLoc_data.connect(self.video_window.initialize_obj_centroids)
        self.csv_reader.ImageNames_data.connect(self.video_window.initialize_image_names)
        
        # Added Image Index as another connection
#        self.csv_reader.ImageIndex_data.connect(self.video_window.initialize_image_index)
        
        self.video_window.update_plot.connect(self.xplot.update_cursor)
        self.video_window.update_plot.connect(self.yplot.update_cursor)
        self.video_window.update_plot.connect(self.zplot.update_cursor)
        
       
        self.video_window.update_3Dplot.connect(self.plot3D_widget.plot3D.move_marker)
        
        self.video_window.record_signal.connect(self.record_change)
        self.video_window.image_to_record.connect(self.add_frame)
        self.video_window.imageName.connect(self.add_name)

        # Image analysis widget connections
        self.AnalysisWidget.show_roi.connect(self.video_window.toggle_ROI_show)

        self.video_window.roi_pos_signal.connect(self.AnalysisWidget.update_pos_display)
        self.video_window.roi_size_signal.connect(self.AnalysisWidget.update_size_display)

        # metadata
        self.csv_reader.pixelpermm_data.connect(self.video_window.update_pixelsize)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                   Window for Track parameters
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


class optionsTrack_Dialog(QtGui.QDialog):

    width = QtCore.pyqtSignal(float)
    length = QtCore.pyqtSignal(float)
    pixelpermm = QtCore.pyqtSignal(int)
    x_offset = QtCore.pyqtSignal(float)
    y_offset = QtCore.pyqtSignal(float)

    def __init__(self, width_value = 4, length_value = 30, x_offset_value = 0, y_offset_value = 0, PixelPermm_value=314, parent = None):
        super().__init__()
        self.setWindowTitle('Track Parameters')

        # Default options for the track parameters
        # Channel width
        self.width_value = width_value
        # Channel length
        self.length_value = length_value

        # Wall offsets (for tracks were homing may not have worked correctly)
        self.x_offset_value = x_offset_value
        self.y_offset_value = y_offset_value

        # Pixel size
        self.PixelPermm_value = PixelPermm_value    # Pixels per mm

        # Data entry tools (Spinboxes) for Pixel size, chamber extents etc.
        # Pixel size spinbox
        self.label_pixel = QtGui.QLabel('Pixel/mm')
        self.spinbox_pixelpermm=QtGui.QSpinBox()
        self.spinbox_pixelpermm.setRange(1,3000)
        self.spinbox_pixelpermm.setSingleStep(1)
        self.spinbox_pixelpermm.setValue(int(self.PixelPermm_value))
        self.spinbox_pixelpermm.valueChanged.connect(self.send_pixelsize)

        self.pixel_layout = QtGui.QHBoxLayout()
        self.pixel_layout.addWidget(self.label_pixel)
        self.pixel_layout.addWidget(self.spinbox_pixelpermm)

        self.pixel_group = QtGui.QWidget()
        self.pixel_group.setLayout(self.pixel_layout)

         # Chamber Width
        self.label_width = QtGui.QLabel('Chamber width (mm)')
        self.spinbox_width=QtGui.QDoubleSpinBox()
        self.spinbox_width.setRange(0,50)
        self.spinbox_width.setSingleStep(0.1)
        self.spinbox_width.setDecimals(1)
        self.spinbox_width.setValue(round(self.width_value,1))
        self.spinbox_width.valueChanged.connect(self.send_width)

        self.width_layout = QtGui.QHBoxLayout()
        self.width_layout.addWidget(self.label_width)
        self.width_layout.addWidget(self.spinbox_width)

        self.width_group = QtGui.QWidget()
        self.width_group.setLayout(self.width_layout)

         # Chamber Length
        self.label_length = QtGui.QLabel('Chamber length (mm)')
        self.spinbox_length = QtGui.QDoubleSpinBox()
        self.spinbox_length.setRange(0,50)
        self.spinbox_length.setSingleStep(0.1)
        self.spinbox_length.setDecimals(1)
        self.spinbox_length.setValue(round(self.length_value,1))
        self.spinbox_length.valueChanged.connect(self.send_length)


        self.length_layout = QtGui.QHBoxLayout()
        self.length_layout.addWidget(self.label_length)
        self.length_layout.addWidget(self.spinbox_length)

        self.length_group = QtGui.QWidget()
        self.length_group.setLayout(self.length_layout)


        # X - offset
        self.label_x_offset = QtGui.QLabel('X-offset (mm)')
        self.spinbox_x_offset = QtGui.QDoubleSpinBox()
        self.spinbox_x_offset.setRange(-50,50)
        self.spinbox_x_offset.setSingleStep(0.1)
        self.spinbox_x_offset.setDecimals(1)
        self.spinbox_x_offset.setValue(round(self.x_offset_value,1))
        self.spinbox_x_offset.valueChanged.connect(self.send_x_offset)


        self.x_offset_layout = QtGui.QHBoxLayout()
        self.x_offset_layout.addWidget(self.label_x_offset)
        self.x_offset_layout.addWidget(self.spinbox_x_offset)

        self.x_offset_group = QtGui.QWidget()
        self.x_offset_group.setLayout(self.x_offset_layout)


        # Y - offset
        self.label_y_offset = QtGui.QLabel('Y-offset (mm)')
        self.spinbox_y_offset = QtGui.QDoubleSpinBox()
        self.spinbox_y_offset.setRange(-50,50)
        self.spinbox_y_offset.setSingleStep(0.1)
        self.spinbox_y_offset.setDecimals(1)
        self.spinbox_y_offset.setValue(round(self.y_offset_value,1))
        self.spinbox_y_offset.valueChanged.connect(self.send_y_offset)


        self.y_offset_layout = QtGui.QHBoxLayout()
        self.y_offset_layout.addWidget(self.label_y_offset)
        self.y_offset_layout.addWidget(self.spinbox_y_offset)

        self.y_offset_group = QtGui.QWidget()
        self.y_offset_group.setLayout(self.y_offset_layout)


        h_layout_params = QtGui.QVBoxLayout()
        h_layout_params.addWidget(self.pixel_group)
        h_layout_params.addWidget(self.width_group)
        h_layout_params.addWidget(self.length_group)
        h_layout_params.addWidget(self.x_offset_group)
        h_layout_params.addWidget(self.y_offset_group)

        self.setLayout(h_layout_params)
        
        self.setStyleSheet(qss)

    def send_width(self):
        self.width_value = round(self.spinbox_width.value(),1)
        self.width.emit(self.width_value)

    def send_length(self):
        self.length_value = round(self.spinbox_length.value(),1)
        self.length.emit(self.length_value)
    
    def send_pixelsize(self):
        self.PixelPermm_value = int(self.spinbox_pixelpermm.value())
        self.pixelpermm.emit(self.PixelPermm_value)

    def set_pixelsize(self, pixelpermm):
        self.PixelPermm_value = pixelpermm
        self.spinbox_pixelpermm.setvalue(self.PixelPermm_value)


    def send_x_offset(self):
        self.x_offset_value = round(self.spinbox_x_offset.value(),1)
        self.x_offset.emit(self.x_offset_value)
    
    def send_y_offset(self):
        self.y_offset_value = round(self.spinbox_y_offset.value(),1)
        self.y_offset.emit(self.y_offset_value)

# class optionsImage_dialog(QtGui.QDialog):


class optionsVideo_dialog(QtGui.QDialog):

    playback_speed = QtCore.pyqtSignal(float)

    def __init__(self,playback_speed_value = 1,parent=None):

        super().__init__()
        
        self.playback_speed_value = playback_speed_value

        self.setWindowTitle('Playback Parameters')

        self.label_speed = QtGui.QLabel('Playback speed')
        self.hslider_speed = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_speed.setRange(0,200)
        self.spinbox_speed=QtGui.QDoubleSpinBox()
        self.spinbox_speed.setRange(0,20)
        self.spinbox_speed.setSingleStep(0.1)
        self.spinbox_speed.setValue(self.playback_speed_value)
        self.hslider_speed.valueChanged.connect(self.spinbox_speed_setValue)
        self.spinbox_speed.valueChanged.connect(self.hslider_speed_setValue)

        sliderSpeed_layout=QtGui.QHBoxLayout()
        sliderSpeed_layout.addWidget(self.label_speed)
        sliderSpeed_layout.addWidget(self.hslider_speed)
        sliderSpeed_layout.addWidget(self.spinbox_speed)


        self.setLayout(sliderSpeed_layout)
        
        self.setStyleSheet(qss)

    def spinbox_speed_setValue(self,value):
        newvalue=float(value)/10.
        self.spinbox_speed.setValue(newvalue)
        self.playback_speed.emit(newvalue)

    def hslider_speed_setValue(self,value):
        self.hslider_speed.setValue(int(value*10))

        



'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                   Modal window for 3D plot parameters
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class options3D_Dialog(QtGui.QDialog):
    traj_linewidth = QtCore.pyqtSignal(float)
    grid_linewidth=QtCore.pyqtSignal(float)
    camera_distance=QtCore.pyqtSignal(int)
    background=QtCore.pyqtSignal(str)
   
    def __init__(self,distance,parent=None):
        super().__init__()
        self.setWindowTitle('3D Plot Parameters')
        
        # Trajectory Linewidth
        self.label1 = QtGui.QLabel('Trajectory Linewidth')
        self.hslider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider1.setRange(0,500)
        self.hslider1.setValue(100)
        self.spinbox1=QtGui.QDoubleSpinBox()
        self.spinbox1.setSingleStep(0.01)
        self.spinbox1.setRange(0,5)
        self.spinbox1.setValue(1.0)
        self.hslider1.valueChanged.connect(self.spinBox1_setValue)
        self.spinbox1.valueChanged.connect(self.hslider1_setValue)
        slider1_layout=QtGui.QHBoxLayout()
        slider1_layout.addWidget(self.label1)
        slider1_layout.addWidget(self.hslider1)
        slider1_layout.addWidget(self.spinbox1)
        group_slider1=QtWidgets.QWidget()
        group_slider1.setLayout(slider1_layout)

        # Grid Linewidth
        self.label2 = QtGui.QLabel('Grid Linewidth')
        self.hslider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider2.setRange(0,50)
        self.hslider2.setValue(10)
        self.spinbox2=QtGui.QDoubleSpinBox()
        self.spinbox2.setSingleStep(0.1)
        self.spinbox2.setRange(0,5)
        self.spinbox2.setValue(1)
        self.hslider2.valueChanged.connect(self.spinBox2_setValue)
        self.spinbox2.valueChanged.connect(self.hslider2_setValue)
        slider2_layout=QtGui.QHBoxLayout()
        slider2_layout.addWidget(self.label2)
        slider2_layout.addWidget(self.hslider2)
        slider2_layout.addWidget(self.spinbox2)
        group_slider2=QtWidgets.QWidget()
        group_slider2.setLayout(slider2_layout)
        
        # distance between the camera and the center
        self.label3 = QtGui.QLabel('Camera distance')
        self.hslider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider3.setRange(0,500)
        self.hslider3.setValue(distance)
        self.spinbox3=QtGui.QSpinBox()
        self.spinbox3.setRange(0,500)
        self.spinbox3.setValue(distance)
        self.hslider3.valueChanged.connect(self.spinbox3.setValue)
        self.spinbox3.valueChanged.connect(self.hslider3.setValue)
        self.spinbox3.valueChanged.connect(self.send_newDist)
        slider3_layout=QtGui.QHBoxLayout()
        slider3_layout.addWidget(self.label3)
        slider3_layout.addWidget(self.hslider3)
        slider3_layout.addWidget(self.spinbox3)
        group_slider3=QtWidgets.QWidget()
        group_slider3.setLayout(slider3_layout)
        
        groupBox = QtWidgets.QGroupBox("Background color")
        layout = QtGui.QHBoxLayout()
        self.b1 = QtWidgets.QRadioButton("Black")
        self.b1.setChecked(True)
        self.b2 = QtWidgets.QRadioButton("White")
        layout.addWidget(self.b1)
        layout.addWidget(self.b2)
        groupBox.setLayout(layout)
        
        
        v_layout=QtGui.QVBoxLayout()
        v_layout.addWidget(group_slider1)
        v_layout.addWidget(group_slider2)
        v_layout.addWidget(group_slider3)
        v_layout.addWidget(groupBox)
        self.setLayout(v_layout)
        
        self.setStyleSheet(qss)
        
        self.b1.clicked.connect(self.change_background)
        self.b2.clicked.connect(self.change_background)
        
    def change_background(self):
        if self.b1.isChecked():
            self.background.emit('black')
        else:
            self.background.emit('white')
        
    def spinBox1_setValue(self,value):
        newvalue=float(value)/100.
        self.spinbox1.setValue(newvalue)
        self.traj_linewidth.emit(newvalue)
        print('traj emit')

    def hslider1_setValue(self,value):
        self.hslider1.setValue(int(value*100))
        
    def spinBox2_setValue(self,value):
        newvalue=float(value)/10.
        self.spinbox2.setValue(newvalue)
        self.grid_linewidth.emit(newvalue)

    def hslider2_setValue(self,value):
        self.hslider2.setValue(int(value*10))
    
    def send_newDist(self,value):
        self.camera_distance.emit(value)
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                   Modal window for time selection
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
       
class options_TimeInt(QtGui.QDialog):
    index_data=QtCore.pyqtSignal(np.ndarray)

    
    def __init__(self,Time,parent=None):
        super().__init__()
        self.setWindowTitle('Time Interval Selection')
        self.setMinimumWidth(800);
        self.Time=Time
        self.label_TimeInt=QtGui.QLabel('Time selection')
        self.range_slider1=rangeslider.QRangeSlider()
        self.range_slider1.setMax(int(Time.max()))
        self.range_slider1.setEnd(int(Time.max()))
        self.range_slider1.startValueChanged.connect(self.sliders_move)
        self.range_slider1.endValueChanged.connect(self.sliders_move)
        
        h_layout=QtGui.QHBoxLayout()
        h_layout.addWidget(self.label_TimeInt)
        h_layout.addWidget(self.range_slider1)
        
        self.setLayout(h_layout)
        self.setStyleSheet(qss)
        
    def sliders_move(self):        
        time_min,time_max=self.range_slider1.getRange()
        index_min=np.argmin(self.Time-time_min)
        index_max=np.argmin(self.Time-time_max)
        self.index_data.emit(np.array([index_min,index_max]))
        

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                   Modal window for recording a video
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class Recording_Instructions():
    def __init__(self,parent=None):
        self.quality=5
        self.folder_path='...'
        self.isImageSaver=True
        
       
class options_Recording(QtGui.QDialog):
    recording_instructions=QtCore.pyqtSignal(Recording_Instructions)

    
    def __init__(self,parent=None):
        super().__init__()
        
        #Choice of the directory

        self.instructions=Recording_Instructions()
        self.isFolderPath=False
        
        self.choose_directory=QtGui.QPushButton('Choose Directory')
        self.choose_directory.setIcon(QtGui.QIcon('icon/folder.png'))
        self.label_directory=QtGui.QLabel(self.instructions.folder_path)
        self.choose_directory.clicked.connect(self.pick_new_directory)
        
        self.button_video = QtGui.QPushButton(' Record a video')
        self.button_video.setIcon(QtGui.QIcon('icon/video.png'))
        self.button_video.setCheckable(True)
        self.button_video.setChecked(False)
        self.button_video.setEnabled(False)
        self.button_video.clicked.connect(self.start_recording)

        # video vs image
        groupbox_type_register = QtGui.QGroupBox('Type of registration')
        self.radiobutton_image = QtGui.QRadioButton('Stack of images (jpg)')
        self.radiobutton_video = QtGui.QRadioButton('Video (avi)')
        self.radiobutton_image.setChecked(self.instructions.isImageSaver)
        self.radiobutton_video.setChecked(not(self.instructions.isImageSaver))
        groupbox_layout_type_image = QtGui.QHBoxLayout()
        groupbox_layout_type_image.addWidget(self.radiobutton_video)
        groupbox_layout_type_image.addWidget(self.radiobutton_image)
        groupbox_type_register.setLayout(groupbox_layout_type_image)
        self.radiobutton_image.clicked.connect(self.radio_button_change)
        self.radiobutton_video.clicked.connect(self.radio_button_change)
        
        
        # Image quality
        self.labelQual = QtGui.QLabel('Quality')
        self.hsliderQual = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hsliderQual.setRange(0,10)
        self.hsliderQual.setValue(5)
        self.spinboxQual=QtGui.QSpinBox()
        self.spinboxQual.setRange(0,10)
        self.spinboxQual.setValue(self.instructions.quality)
        self.hsliderQual.valueChanged.connect(self.spinBoxQual_setValue)
        self.spinboxQual.valueChanged.connect(self.hsliderQual_setValue)
        sliderQual_layout=QtGui.QHBoxLayout()
        sliderQual_layout.addWidget(self.labelQual)
        sliderQual_layout.addWidget(self.hsliderQual)
        sliderQual_layout.addWidget(self.spinboxQual)
        group_sliderQual=QtWidgets.QWidget()
        group_sliderQual.setLayout(sliderQual_layout)
   
        h_layout=QtGui.QHBoxLayout()
        h_layout.addWidget(self.choose_directory)
        h_layout.addWidget(self.label_directory)
        
        v_layout=QtGui.QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(groupbox_type_register)
        v_layout.addWidget(group_sliderQual)
        v_layout.addWidget(self.button_video)
        
        self.setLayout(v_layout)
        self.setStyleSheet(qss)
        
    def spinBoxQual_setValue(self,value):
        self.spinboxQual.setValue(value)
        self.instructions.quality=value

    def hsliderQual_setValue(self,value):
        self.hsliderQual.setValue(value)
        
    def radio_button_change(self):
        self.instructions.isImageSaver=self.radiobutton_image.isChecked()
        
    def pick_new_directory(self):
        dialog = QtGui.QFileDialog()
        self.instructions.folder_path = dialog.getExistingDirectory(None, "Select Folder")
        if os.path.exists(self.instructions.folder_path):
            self.label_directory.setText(self.instructions.folder_path)
            self.button_video.setEnabled(True)
        else:
            self.button_video.setEnabled(False)
    
    def start_recording(self):
        self.recording_instructions.emit(self.instructions)
        self.close()
        
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Main Window
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
        
class MainWindow(QtWidgets.QMainWindow):
    
   
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Gravity Machine Data Analyser')
        self.setWindowIcon(QtGui.QIcon('icon/icon.png'))
        self.statusBar().showMessage('Ready')
        

        
        
        #WIDGETS
        self.central_widget=CentralWidget()  
        self.setCentralWidget(self.central_widget)
        
         
           
        #Data
        self.directory=''
        self.image_time=np.array([])
        self.image_dict = {}
        # Detect the CSV file name instead of assuming one.
        self.trackFile = []
        
        
        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        editmenu = menuBar.addMenu('&Edit')
        Videomenu = menuBar.addMenu('&Video')
        
        # Create new action
        openAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open File')
        openAction.triggered.connect(self.openFile)
        
        save3DplotAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Save 3D plot', self)        
        save3DplotAction.setShortcut('Ctrl+S')
        save3DplotAction.setStatusTip('Save 3D Plot')
        save3DplotAction.triggered.connect(self.save_3Dplot)
        
        option3DplotAction = QtGui.QAction(QtGui.QIcon('open.png'), '&3D-plot Parameters', self)        
        option3DplotAction.setShortcut('Ctrl+P')
        option3DplotAction.setStatusTip('3D Plot parameters')
        option3DplotAction.triggered.connect(self.options_3Dplot)
        
        optionTimeInterval = QtGui.QAction(QtGui.QIcon('open.png'), '&Select a Time Interval', self)        
        optionTimeInterval.setShortcut('Ctrl+I')
        optionTimeInterval.setStatusTip('Time Interval')
        optionTimeInterval.triggered.connect(self.options_TimeInt)

        optionTrack = QtGui.QAction(QtGui.QIcon('open.png'), '&Select Track Parameters', self)        
        optionTrack.setShortcut('Ctrl+T')
        optionTrack.setStatusTip('Track Parameters')
        optionTrack.triggered.connect(self.options_TrackParams)

        optionVideo = QtGui.QAction(QtGui.QIcon('open.png'), '&Video Parameters', self)        
        optionVideo.setShortcut('Ctrl+V')
        optionVideo.setStatusTip('Video Parameters')
        optionVideo.triggered.connect(self.options_VideoParams)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(save3DplotAction)
        # fileMenu.addAction(option3DplotAction)
        # fileMenu.addAction(optionTimeInterval)
        editmenu.addAction(optionTrack)
        editmenu.addAction(option3DplotAction)
        editmenu.addAction(optionTimeInterval)
        Videomenu.addAction(optionVideo)
        
        # Connections
        self.central_widget.video_window.imageName.connect(self.update_statusBar)
        self.central_widget.csv_reader.Time_data.connect(self.initialize_image_time)
        self.central_widget.AnalysisWidget.save_analysis_data.connect(self.save_analysis_data)
        
        
    def openFile(self):
        print('Opening dataset ...')

        self.directory = QtGui.QFileDialog.getExistingDirectory(self)
        
        self.trackFile, *rest = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.directory,"CSV files (*.csv)")
        
        # self.trackFile, *rest = os.path.split(self.trackFile)
        
        if os.path.exists(self.directory):

            # Walk through the folders and identify ones that contain images
            for dirs, subdirs, files in os.walk(self.directory, topdown=False):
               
                root, subFolderName = os.path.split(dirs)
                print('Dir: ',dirs)
                print('Subdir: ',subdirs)
                for file in files: 
                    # Find folders that contain the image stream we want to load. For backward compatibility this also checks all folders starting with 'images' 
                    if(file.lower().endswith('tif') and (((VARIABLE_HEADER_MAPPING['Image name'] in dirs) or ('images' in dirs)))):
                        key = file
                        value = dirs
                        self.image_dict[key]=value
                # print(subFolderName)
                # if('images' in subFolderName):
                   
                #    for fileNames in files:
                #        key = fileNames
                #        value = subFolderName
                #        self.image_dict[key]=value
                # elif(VARIABLE_HEADER_MAPPING['Image name'] in subFolderName):



                print('Loaded {}'.format(self.trackFile))

            self.central_widget.video_window.initialize_directory(self.directory, self.image_dict)

            self.central_widget.video_window.playButton.setEnabled(True)
            self.central_widget.video_window.recordButton.setEnabled(True)
            self.central_widget.plot3D_widget.plot3D.reinitialize_plot3D()

            # Open the CSV file before initializing parameters since otherwise it 
            # tries to open image before refreshing the image name list
            self.central_widget.csv_reader.open_newCSV(self.directory, self.trackFile, Tmin = 0 , Tmax = 3600)
            self.central_widget.video_window.initialize_parameters()

            # Need to connect the new Image Names

            self.central_widget.csv_reader.ImageTime_data.connect(self.central_widget.video_window.initialize_image_time)
            self.central_widget.csv_reader.ImageNames_data.connect(self.central_widget.video_window.initialize_image_names)

    def save_analysis_data(self, track_ID, track_condition, Tmin, Tmax, radius):
        
        print('Saving analysis file...')
        analysis_data = pd.DataFrame({'Organism':[], 'Condition':[], 'Diameter (px)':[],'Tmin':[], 'Tmax':[]})
        analysis_data = analysis_data.append(pd.DataFrame({'Organism':[track_ID], 'Condition':[track_condition], 'Diameter (px)':[radius], 'Tmin':[Tmin], 'Tmax':[Tmax]}))
        analysis_data.to_csv(os.path.join(self.directory, 'analysis_data.csv'))
        print('Saved analysis file')

    def save_3Dplot(self):
        self.central_widget.plot3D_widget.plot3D.save_plot(quality = 10)
      
    def options_3Dplot(self):
        options_dialog = options3D_Dialog(self.central_widget.plot3D_widget.plot3D.opts['distance'])
        options_dialog.grid_linewidth.connect(self.central_widget.plot3D_widget.plot3D.update_grid_linewidth)
        options_dialog.traj_linewidth.connect(self.central_widget.plot3D_widget.plot3D.update_traj_linewidth)
        options_dialog.camera_distance.connect(self.central_widget.plot3D_widget.plot3D.update_camera_distance)
        options_dialog.background.connect(self.central_widget.plot3D_widget.plot3D.update_background)
        
        options_dialog.exec_()

    def options_TrackParams(self):
        options_dialog_track = optionsTrack_Dialog(width_value = self.central_widget.plot3D_widget.plot3D.Width, length_value = self.central_widget.plot3D_widget.plot3D.Length, x_offset_value = self.central_widget.plot3D_widget.plot3D.x_offset, y_offset_value = self.central_widget.plot3D_widget.plot3D.y_offset, PixelPermm_value = self.central_widget.video_window.PixelPermm)
        options_dialog_track.pixelpermm.connect(self.central_widget.video_window.update_pixelsize)
        options_dialog_track.width.connect(self.central_widget.plot3D_widget.plot3D.update_width)
        options_dialog_track.length.connect(self.central_widget.plot3D_widget.plot3D.update_length)
        options_dialog_track.x_offset.connect(self.central_widget.plot3D_widget.plot3D.update_x_offset)
        options_dialog_track.y_offset.connect(self.central_widget.plot3D_widget.plot3D.update_y_offset)
        # Update the 2D plots with the offsets
        options_dialog_track.x_offset.connect(self.central_widget.xplot.update_offset)
        options_dialog_track.y_offset.connect(self.central_widget.yplot.update_offset)

        self.central_widget.csv_reader.pixelpermm_data.connect(options_dialog_track.set_pixelsize)
        
        
        options_dialog_track.exec_()

    def options_VideoParams(self):

        options_dialog_video = optionsVideo_dialog(playback_speed_value = self.central_widget.video_window.playback_speed)
        options_dialog_video.playback_speed.connect(self.central_widget.video_window.update_playback_speed)
        options_dialog_video.exec_()




        
    def options_TimeInt(self):
        print(self.image_time)
        options_dialog_time = options_TimeInt(self.image_time)
        options_dialog_time.index_data.connect(self.central_widget.csv_reader.update_index)
        options_dialog_time.exec_()
        
    def closeEvent(self, event):
        
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)

        if reply == QtWidgets.QMessageBox.Yes:

            cv2.destroyAllWindows()
            event.accept()
            sys.exit()
            
        else:
            event.ignore() 
            
    def update_statusBar(self,imageName):
        self.statusBar().showMessage(imageName)
        
    def initialize_image_time(self,time):
        self.image_time=time
    

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                             Main Function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

if __name__ == '__main__':

    #To prevent the error "Kernel died"
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    
    #Splash screen (image during the initialisation)
    splash_pix = QtGui.QPixmap('icon/icon.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    # splash.setMask(splash_pix.mask())
    splash.show()
    
    

    #Mainwindow creation
    win = MainWindow()
    qss = QSSHelper.open_qss(os.path.join('aqua', 'aqua.qss'))
    win.setStyleSheet(qss)
    win.central_widget.connect_all()

        
    win.show()
    splash.finish(win)
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
