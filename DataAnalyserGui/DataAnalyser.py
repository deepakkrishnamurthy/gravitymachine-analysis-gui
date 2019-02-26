# -*- coding: utf-8 -*-


import sys
import os

import cv2
import numpy as np

from pyqtgraph.Qt import QtWidgets,QtCore, QtGui #possible to import form PyQt5 too ... what's the difference? speed? 


from CSV_Reader import CSV_Reader
from plot3D import plot3D
from VideoWindow import VideoWindow
from PlotWidget import PlotWidget
from VideoSaver import VideoSaver
from ImageSaver import ImageSaver

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
        
        self.video_saver=VideoSaver()
        self.image_saver=ImageSaver()
        self.isImageSaver=True #True: image_saver will be chose in place of video saver
        
        #widgets
        self.video_window=VideoWindow()
        self.fps=None #fps for saving
        self.xplot=PlotWidget('X displacement', label = 'X',color ='r')
        self.yplot=PlotWidget('Y displacement', label = 'Y',color ='g')
        self.zplot=PlotWidget('Z displacement', label = 'Z',color =(50, 100, 255))
        
        #Tool
        self.csv_reader=CSV_Reader()
        
        self.plot3D=plot3D()
        
        self.panVSlider = QtGui.QSlider(QtCore.Qt.Vertical)
        self.panVSlider.setRange(-400, 400)
        self.panVSlider.setValue(0)
        
        self.panHSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.panHSlider.setRange(-200, 200)
        self.panHSlider.setValue(0)
        
        self.home3Dbutton=QtGui.QPushButton()
        self.home3Dbutton.setFixedSize(20,20)
        self.home3Dbutton.setIcon(QtGui.QIcon('icon/home.png'))

        plot3D_layout=QtGui.QGridLayout()
        plot3D_layout.addWidget(self.plot3D,0,0,1,1)
        plot3D_layout.addWidget(self.panVSlider,0,1,1,1)
        plot3D_layout.addWidget(self.panHSlider,1,0,1,1)
        plot3D_layout.addWidget(self.home3Dbutton,1,1,1,1)

        # Create a vertical layout consisting of the video window and 3D plot
        v_layout = QtGui.QVBoxLayout()
        # v_layout = QtGui.QGridLayout()

        # v_layout.addWidget(self.video_window, 0,0,1,1)
        # v_layout.addLayout(self.zplot,0,1,1,1)

        v_layout.addWidget(self.video_window)
        v_layout.addWidget(self.zplot)


        # v_layout.addWidget(self.video_window)
        # v_layout.addLayout(plot3D_layout)

        # v_layout.setStretchFactor(plot3D_layout,0.5)
  

        
        # VERTICAL LAYOUT ON THE LEFT
        h_layout = QtGui.QHBoxLayout()
        
        # v_left_layout=QtGui.QVBoxLayout()
        # v_left_layout.addWidget(self.video_window)
        
        # # v_right_layout=QtGui.QVBoxLayout()
        # # v_right_layout.addWidget(self.xplot)
        # # v_right_layout.addWidget(self.yplot)
        # # v_right_layout.addWidget(self.zplot)
        
        # # v_right_layout.setStretchFactor(self.xplot,1)
        # # v_right_layout.setStretchFactor(self.yplot,1)
        # # v_right_layout.setStretchFactor(self.zplot,1)
        
        # h_layout.addLayout(v_left_layout)
        # h_layout.addLayout(v_right_layout)
        # h_layout.addLayout(plot3D_layout)

        h_layout.addLayout(v_layout)
        h_layout.addLayout(plot3D_layout)

        
        # h_layout.setStretchFactor(v_left_layout,1)
        # h_layout.setStretchFactor(v_right_layout,1)
        # h_layout.setStretchFactor(plot3D_layout,1)
        # Final action     
        # self.setLayout(v_layout)
        self.setLayout(h_layout)
        
    def reset_sliders(self,value):
        self.panHSlider.setValue(0)
        self.panVSlider.setValue(0)
        
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
        plot3d=self.plot3D.export_plot(self.quality)
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
        
        self.csv_reader.Xobjet_data.connect(self.xplot.update_plot)
        self.csv_reader.Yobjet_data.connect(self.yplot.update_plot)
        self.csv_reader.Zobjet_data.connect(self.zplot.update_plot)
        self.csv_reader.fps_data.connect(self.update_recording_fps)
        
        self.csv_reader.Time_data.connect(self.plot3D.update_Time)
        self.csv_reader.Xobjet_data.connect(self.plot3D.update_X)
        self.csv_reader.Yobjet_data.connect(self.plot3D.update_Y)
        self.csv_reader.Zobjet_data.connect(self.plot3D.update_Z)
        
        self.csv_reader.ImageTime_data.connect(self.video_window.initialize_image_time)
        self.csv_reader.ImageNames_data.connect(self.video_window.initialize_image_names)
        
        # Added Image Index as another connection
#        self.csv_reader.ImageIndex_data.connect(self.video_window.initialize_image_index)
        
        self.video_window.update_plot.connect(self.xplot.update_cursor)
        self.video_window.update_plot.connect(self.yplot.update_cursor)
        self.video_window.update_plot.connect(self.zplot.update_cursor)
        
        self.panHSlider.valueChanged.connect(self.plot3D.pan_X)
        self.panVSlider.valueChanged.connect(self.plot3D.pan_Z)
        self.home3Dbutton.clicked.connect(self.plot3D.reset_view)
        self.plot3D.reset_sliders.connect(self.reset_sliders)
        self.video_window.update_3Dplot.connect(self.plot3D.move_marker)
        
        self.video_window.record_signal.connect(self.record_change)
        self.video_window.image_to_record.connect(self.add_frame)
        self.video_window.imageName.connect(self.add_name)
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                   Modal window for 3D plot parameters
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class options3D_Dialog(QtGui.QDialog):
    traj_linewidth=QtCore.pyqtSignal(float)
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
        
class MainWindowMill(QtWidgets.QMainWindow):
    
   
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Data Analyser')
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
        optionTimeInterval.setShortcut('Ctrl+T')
        optionTimeInterval.setStatusTip('Time Interval')
        optionTimeInterval.triggered.connect(self.options_TimeInt)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(save3DplotAction)
        fileMenu.addAction(option3DplotAction)
        fileMenu.addAction(optionTimeInterval)
        
        self.central_widget.video_window.imageName.connect(self.update_statusBar)
        self.central_widget.csv_reader.Time_data.connect(self.initialize_image_time)
        
        
    def openFile(self):
        print('Opening dataset ...')

        self.directory = QtGui.QFileDialog.getExistingDirectory(self)
        
        self.trackFile, *rest = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.directory,"CSV fles (*.csv)")
        
        self.trakFile, *rest = os.path.split(self.trackFile)
        
        if os.path.exists(self.directory):

            # Walk through the folders and identify ones that contain images
            for dirs, subdirs, files in os.walk(self.directory, topdown=False):
               
                root, subFolderName = os.path.split(dirs)
                    
                print(subFolderName[0:6])
                if('images' in subFolderName):
                   
                   for fileNames in files:
                       key = fileNames
                       value = subFolderName
                       self.image_dict[key]=value

#                if(os.path.normpath(dirs) == os.path.normpath(self.directory)):
#                    for fileNames in files:
#                        if('.csv' in fileNames):
#                            trackFileNames.append(fileNames)

#            if(len(trackFileNames)==0):
#                raise FileNotFoundError('CSV track was not found!')      
#            elif(len(trackFileNames)>1):
#                print('More than one .csv file found!')
#                
#                for ii, filename in enumerate(trackFileNames):
##                    
#                      print('{}: {} \n'.format(ii+1, filename))
#                    
#                print('Choose the file to use:')
#                file_no = int(input())
#                    
#                self.trackFile = trackFileNames[file_no-1]
                print('Loaded {}'.format(self.trackFile))
                
#                for tracks in trackFileNames:
#                    if('division' in tracks):
#                        self.trackFile = tracks
#                        break
#                    elif('mod' in tracks):
#                        self.trackFile = tracks
#                        break
#                    else:
#                        self.trackFile = 'track.csv'
#                        break
#                    print('Loaded {}'.format(self.trackFile))
#
#
#            else:
#                self.trackFile = trackFileNames[0]
                

            # Passes the root directory to the Video Window
            # self.central_widget.video_window.initialize_directory(self.directory)
            # Proposed change: 
            # 1. Pass the root directory
            # 2. Pass a dictionary of the subfolders for each image
            # 3. Auto-detect which csv file


            self.central_widget.video_window.initialize_directory(self.directory, self.image_dict)

            



            self.central_widget.video_window.playButton.setEnabled(True)
            self.central_widget.video_window.recordButton.setEnabled(True)
            self.central_widget.plot3D.reinitialize_plot3D()

            # Open the CSV file before initializing parameters since otherwise it 
            # tries to open image before refreshing the image name list
            self.central_widget.csv_reader.open_newCSV(self.directory, self.trackFile)

            self.central_widget.video_window.initialize_parameters()


            # Need to connect the new Image Names

            # self.central_widget.csv_reader.ImageTime_data.connect(self.central_widget.video_window.initialize_image_time)
            # self.central_widget.csv_reader.ImageNames_data.connect(self.central_widget.video_window.initialize_image_names)

        
    def save_3Dplot(self):
        self.central_widget.plot3D.save_plot(quality = 10)
      
    def options_3Dplot(self):
        options_dialog = options3D_Dialog(self.central_widget.plot3D.opts['distance'])
        options_dialog.grid_linewidth.connect(self.central_widget.plot3D.update_grid_linewidth)
        options_dialog.traj_linewidth.connect(self.central_widget.plot3D.update_traj_linewidth)
        options_dialog.camera_distance.connect(self.central_widget.plot3D.update_camera_distance)
        options_dialog.background.connect(self.central_widget.plot3D.update_background)
        
        options_dialog.exec_()
        
    def options_TimeInt(self):
        print(self.image_time)
        options_dialog_time = options_TimeInt(self.image_time)
        options_dialog_time.index_data.connect(self.central_widget.csv_reader.update_index)
        options_dialog_time.exec_()
        
    def closeEvent(self, event):
        
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes | 
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
    win= MainWindowMill()
    qss = QSSHelper.open_qss(os.path.join('aqua', 'aqua.qss'))
    win.setStyleSheet(qss)
    win.central_widget.connect_all()

        
    win.show()
    splash.finish(win)
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
