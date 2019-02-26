# -*- coding: utf-8 -*-


import sys
import os

import cv2
import numpy as np

from pyqtgraph.Qt import QtWidgets,QtCore, QtGui #possible to import form PyQt5 too ... what's the difference? speed? 
import pyqtgraph as pg
import matplotlib.pyplot as plt
import matplotlib as mpl
import cmocean as cmocean

import pyqtgraph.opengl as gl
from utils import GridItem as Gd
from utils import rangeslider as rangeslider




import csv as csv

from aqua.qsshelper import QSSHelper
import time as time

			       

	
'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                             CSV reader
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CSV_Reader(QtCore.QObject):
    
    Time_data = QtCore.pyqtSignal(np.ndarray)
    Xobjet_data = QtCore.pyqtSignal(np.ndarray)
    Yobjet_data = QtCore.pyqtSignal(np.ndarray)
    Zobjet_data = QtCore.pyqtSignal(np.ndarray)
    ImageNames_data = QtCore.pyqtSignal(np.ndarray)
    ImageTime_data = QtCore.pyqtSignal(np.ndarray)
    
    
    def __init__(self, parent=None):
        super(CSV_Reader, self).__init__(parent)
        self.file_name="/track.csv"
        
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
        
    
    def open_newCSV(self,directory):

        Data=[]
        reader = csv.reader(open(directory+self.file_name,newline=''))
        
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
            
        self.index_min=0
        self.index_max=len(self.Time)-1
        
        self.Time_data.emit(self.Time)
        self.Xobjet_data.emit(self.Xobjet)
        self.Yobjet_data.emit(self.Yobjet)
        self.Zobjet_data.emit(self.ZobjWheel)
        
        #Speed computation
        
        self.Vx=np.array([])
        
        #Time and name of the image for the video reader
        self.send_image_time()
        
    def send_image_time(self):
        print('try send')
        cropped_ImageNames=self.ImageNames[self.index_min:self.index_max+1]
        cropped_Time=self.Time[self.index_min:self.index_max+1]
        
        ImageTime=[]
        new_ImageNames=[]
        
        for i in range(len(cropped_ImageNames)):
            if len(cropped_ImageNames[i])>0:
                new_ImageNames.append(cropped_ImageNames[i])
                ImageTime.append(round(cropped_Time[i],2))
        
        self.ImageNames_data.emit(np.array(new_ImageNames))
        self.ImageTime_data.emit(np.array(ImageTime))
        print('ok send')
        
    def update_index(self,index):
        self.index_min=index[0]
        self.index_max=index[1]
        self.Time_data.emit(self.Time[self.index_min:self.index_max+1])
        self.Xobjet_data.emit(self.Xobjet[self.index_min:self.index_max+1])
        self.Yobjet_data.emit(self.Yobjet[self.index_min:self.index_max+1])
        self.Zobjet_data.emit(self.ZobjWheel[self.index_min:self.index_max+1]) 
        self.send_image_time()
        print('index refreshed')
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            3D Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''        
class plot3D(gl.GLViewWidget):  
    
    reset_sliders=QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.size_traj=0.12
        self.size_grid=1.
        self.size_marker=0.4
        self.cmap=cmocean.cm.deep
        
        self.background='black'
        
        if self.background=='black':
            self.grid_color=(1.,1.,1.,0.5)
            self.setBackgroundColor((0.,0.,0.,1.))
        else:
            self.grid_color=(0.,0.,0.,0.5)
            self.setBackgroundColor('w')
                
        self.initial_center=[0,0,0]      #initial view center
        self.initial_position=[20,0,-100] #initial position f the camera relatively to the center
        
        #for manual pan with sider
        self.prev_pan_X=0
        self.prev_pan_Z=0
        
        self.initialize_plot()
    
    #------------------------------------------------------------
    #Cleaning when new data is import 
    #------------------------------------------------------------
    
    def clear_grid(self):
        self.removeItem(self.xygrid)
        self.removeItem(self.yzgrid)
        self.removeItem(self.xzgrid)
    
    def clear_plot(self):
        self.removeItem(self.marker)
        self.removeItem(self.scatter_plot)
        self.clear_grid()
    
    
    def reinitialize_plot3D(self):
        self.clear_plot()
        self.initialize_plot()
    
    #------------------------------------------------------------
    # Display the new data set
    #------------------------------------------------------------
    
    def update_Time(self,Timedata):
        self.Time=Timedata
        
    def update_X(self,Xdata):
        self.X=Xdata
    def update_Y(self,Ydata):
        self.Y=Ydata
    def update_Z(self,Zdata):
        self.Z=Zdata
        self.Zmax=self.Z.max()
        self.Zmin=self.Z.min()
        self.update_plot()
        
    def update_plot(self):
        n=len(self.X)
        self.pos=np.empty((n, 3))
        pg_cmap = self.generatePgColormap()
        self.color = pg_cmap.getLookupTable(start=0.0, stop=1.0, nPts=len(self.Time), alpha=True, mode='float')
        
        for i in range(n):
            self.pos[i]=(self.X[i],self.Y[i],self.Z[i])
         
        self.scatter_plot.setData(pos=self.pos, size=self.size_traj, color=self.color, pxMode=False)
        self.scatter_plot.setGLOptions('opaque')
    
        self.update_grid() #build a grid adapted to the size of the data
        self.set_initial_center() #set the point to which the camera is looking at
        self.reset_view()
        
    def update_grid(self):
        newZsize=np.ceil(self.Z.max()-self.Z.min())
        
        self.xygrid.translate(0, 0, self.Z.min())
        
        self.yzgrid.setSize(newZsize,3,0)
        self.yzgrid.translate(0, 0, 0.5*(newZsize-10)+self.Z.min())
        
        self.xzgrid.setSize(15,newZsize,0)
        self.xzgrid.translate(0, 0, 0.5*(newZsize-10)+self.Z.min())
        
    def generatePgColormap(self):
        colors=self.cmap(np.arange(256))
        colors=colors[100:]
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        return pgMap
    
    #------------------------------------------------------------
    # Action when the video is playing
    #------------------------------------------------------------
    
    def move_marker(self,time):
        index=np.argmin(abs(self.Time-time))
        pos = np.empty((1, 3))
        size = np.empty((1))
        color = np.empty((1, 4))
        pos[0]=(self.X[index],self.Y[index],self.Z[index]); size[0]=self.size_marker;color[0]=(1.0,1.0,1.0,1.0)

        self.marker.setData(pos=pos, size=size, color=color, pxMode=False)
        
        
    #------------------------------------------------------------
    # TODO when the program opens
    #------------------------------------------------------------

    def initialize_grid(self):
        self.xygrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.xygrid.setSize(15,3)
        self.xygrid.setSpacing(1,1,0)
        self.xygrid.translate(0, 1.5, 0)
        self.addItem(self.xygrid)
        
        self.yzgrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.yzgrid.setSize(10,3)
        self.yzgrid.setSpacing(1,1,0)
        self.yzgrid.rotate(90, 0, 1, 0)
        self.yzgrid.translate(7.5, 1.5, 5)
        self.addItem(self.yzgrid)
        
        self.xzgrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.xzgrid.setSize(15,10)
        self.xzgrid.setSpacing(1,1,0)
        self.xzgrid.rotate(90, 1, 0, 0)
        self.xzgrid.translate(0, 3, 5)
        self.addItem(self.xzgrid)
         
    def initialize_plot(self):
        self.Time=np.array([])
        self.X=np.array([])
        self.Y=np.array([])
        self.Z=np.array([])
        self.Zmax=10
        self.Zmin=0
        
        self.opts['distance'] = 20    
        self.show()

        self.axes=gl.GLAxisItem(size=None, antialias=True, glOptions='translucent')
        self.axes.translate(0,0,0)
        self.addItem(self.axes)
        
        self.initialize_grid()
        
        #Inital scatter plot
        pos = np.empty((1, 3))
        size = np.empty((1))
        color = np.empty((1, 4))
        pos[0] = (0,0,0); size[0] = 0.0;   color[0] = (1.0, 0.0, 0.0, 0.5)    
            
        self.scatter_plot = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        self.addItem(self.scatter_plot)
        
        #Initial marker
        pos2 = np.empty((1, 3))
        size2 = np.empty((1))
        color2 = np.empty((1, 4))
        pos2[0]=(0,0,0); size2[0]=self.size_marker;color2[0]=(1.0,1.0,1.0,1.0)
        
        self.marker=gl.GLScatterPlotItem(pos=pos2, size=size2, color=color2, pxMode=False)
        self.addItem(self.marker)
        
        self.reset_view()
        
    #------------------------------------------------------------
    #  View handling
    #------------------------------------------------------------
        
    def set_initial_center(self):
        self.initial_center=[0,0,(self.Z.max()+self.Z.min())/2]
        self.pan(dx=self.initial_center[0], dy=self.initial_center[1], dz=self.initial_center[2], relative=False)
        
    def reset_center(self):
        self.pan(dx=-self.initial_center[0], dy=-self.initial_center[1], dz=-self.initial_center[2], relative=False)
        self.initial_center=[0,0,0]
        
    def pan_X(self,value):
        self.pan(dx=value-self.prev_pan_X, dy=0, dz=0, relative=True)
        self.prev_pan_X=value
    
    def pan_Z(self,value):
        value=(self.Zmax-self.Zmin)/10*value
        self.pan(dx=0, dy=0, dz=value-self.prev_pan_Z, relative=True)
        self.prev_pan_Z=value
    
    def reset_view(self):
        self.reset_sliders.emit(0)
        self.setCameraPosition(distance=self.initial_position[0],elevation=self.initial_position[1],azimuth=self.initial_position[2])
    
    #------------------------------------------------------------
    #  3D Plot parameters
    #------------------------------------------------------------
    
    def update_grid_linewidth(self,value): 
        self.size_grid=value
        self.xygrid.setThickness(self.size_grid)
        self.yzgrid.setThickness(self.size_grid)
        self.xzgrid.setThickness(self.size_grid)
    
    def update_traj_linewidth(self,value):
        self.size_traj=value
        self.scatter_plot.setData(pos=self.pos, size=self.size_traj, color=self.color, pxMode=False)
    
    def update_camera_distance(self,value):
        self.setCameraPosition(distance=value)
        
    def update_background(self,value):
        print(value)
        self.background=value
        if value=='black':
            self.setBackgroundColor((0.,0.,0.,1.))
            self.grid_color=(1.,1.,1.,0.5)
            self.xygrid.setColor(self.grid_color)
            self.yzgrid.setColor(self.grid_color)
            self.xzgrid.setColor(self.grid_color)
        else:
            self.setBackgroundColor('w')
            self.grid_color=(0.,0.,0.,0.5)
            self.xygrid.setColor(self.grid_color)
            self.yzgrid.setColor(self.grid_color)
            self.xzgrid.setColor(self.grid_color)
            
    #------------------------------------------------------------
    #  Save plot and colorbar
    #------------------------------------------------------------
    
    def save_plot(self):
        directory,filetype = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", ".jpg")
        file_directory=directory+filetype
        if len(directory)>4:
            image1=self.grabFrameBuffer(False)
            width1=image1.width()
            height1=image1.height()
            width2=3000
            factor=width2/width1
            length2=int(factor*height1)
            self.xygrid.setThickness(self.size_grid*factor)
            self.yzgrid.setThickness(self.size_grid*factor)
            self.xzgrid.setThickness(self.size_grid*factor)
            self.scatter_plot.setData(pos=self.pos, size=1.2*factor*self.size_traj, color=self.color, pxMode=False)
            self.scatter_plot.setGLOptions('opaque')
            image=self.renderToArray((width2, length2))
            pg.makeQImage(image).save(file_directory)
            self.xygrid.setThickness(self.size_grid)
            self.yzgrid.setThickness(self.size_grid)
            self.xzgrid.setThickness(self.size_grid)
            self.scatter_plot.setData(pos=self.pos, size=self.size_traj, color=self.color, pxMode=False)
            self.scatter_plot.setGLOptions('opaque')
            
            self.save_colorbar(directory)

        
    def save_colorbar(self,directory):
        fig = plt.figure()
        ax1 = fig.add_axes([0.05, 0.05, 0.04, 0.8])
        # Set the colormap and norm to correspond to the data for which
        # the colorbar will be used.
        colors=self.cmap(np.arange(256))
        colors=colors[100:]
        cmap=mpl.colors.ListedColormap(colors)
        norm = mpl.colors.Normalize(vmin=0, vmax=self.Time[-1])
        
        # ColorbarBase derives from ScalarMappable and puts a colorbar
        # in a specified axes, so it has everything needed for a
        # standalone colorbar.  There are many more kwargs, but the
        # following gives a basic continuous colorbar with ticks
        # and labels.
        mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                        norm=norm,
                                        orientation='vertical')
        file_directory=directory+'colorbar.svg'
        plt.savefig(file_directory)
        
    
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''


class PlotWidget(pg.GraphicsLayoutWidget):
    
    def __init__(self,title, parent=None):
        super().__init__(parent)
        self.title=title
        #plot Zobjet

        
        self.Abs=np.array([])
        self.Ord=np.array([])
        self.plot1=self.addPlot(title=title)
        self.curve=self.plot1.plot(self.Abs,self.Ord)
        self.plot1.enableAutoRange('xy', True)
        self.plot1.showGrid(x=True, y=True)
        
        self.point=QtCore.QPointF(0,0)
        self.vLine = pg.InfiniteLine(pos=self.point,angle=90, movable=False)
        self.plot1.addItem(self.vLine, ignoreBounds=True)
        #self.plot1.addItem(self.point)
        
    def update_Time(self,Time_data):
        self.Abs=Time_data
        
    def update_plot(self,Ord_data):
        self.Ord=Ord_data
        self.curve.setData(self.Abs,self.Ord)

    def initialize_plot(self): #unused
        self.Abs=[]
        self.Ord=[]
        self.curve.setData(self.Abs,self.Ord)
        
    def update_cursor(self,time):
        self.point=QtCore.QPointF(time,0)
        self.vLine.setPos(self.point)

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
        
        #Gui Component
        
        self.image_widget=ImageWidget()
        
        self.playButton = QtGui.QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setCheckable(True)
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

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

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.image_widget)
        layout.addLayout(controlLayout)


        self.setLayout(layout)
        
    def refreshImage(self,image_name):
        file_directory= self.image_directory+image_name
        image=cv2.imread(file_directory)
        self.image_widget.refresh_image(image)
        self.imageName.emit(image_name)
        
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
    

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Central Widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CentralWidget(QtWidgets.QWidget):
    
   
    def __init__(self):
        super().__init__()
        
        #widgets
        self.video_window=VideoWindow()
        self.xplot=PlotWidget('X function of Time')
        self.yplot=PlotWidget('Y function of Time')
        self.zplot=PlotWidget('Z function of Time')
        
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
        
        # VERTICAL LAYOUT ON THE LEFT
        h_layout = QtGui.QHBoxLayout()
        
        v_left_layout=QtGui.QVBoxLayout()
        v_left_layout.addWidget(self.video_window)
        
        v_right_layout=QtGui.QVBoxLayout()
        v_right_layout.addWidget(self.xplot)
        v_right_layout.addWidget(self.yplot)
        v_right_layout.addWidget(self.zplot)
        
        v_right_layout.setStretchFactor(self.xplot,1)
        v_right_layout.setStretchFactor(self.yplot,1)
        v_right_layout.setStretchFactor(self.zplot,1)
        
        h_layout.addLayout(v_left_layout)
        h_layout.addLayout(v_right_layout)
        h_layout.addLayout(plot3D_layout)
        
        h_layout.setStretchFactor(v_left_layout,1)
        h_layout.setStretchFactor(v_right_layout,1)
        h_layout.setStretchFactor(plot3D_layout,1)
        # Final action     
        self.setLayout(h_layout)
        
    def reset_sliders(self,value):
        self.panHSlider.setValue(0)
        self.panVSlider.setValue(0)
        
    def connect_all(self):
        
        self.csv_reader.Time_data.connect(self.xplot.update_Time)
        self.csv_reader.Time_data.connect(self.yplot.update_Time)
        self.csv_reader.Time_data.connect(self.zplot.update_Time)
        
        self.csv_reader.Xobjet_data.connect(self.xplot.update_plot)
        self.csv_reader.Yobjet_data.connect(self.yplot.update_plot)
        self.csv_reader.Zobjet_data.connect(self.zplot.update_plot)
        
        self.csv_reader.Time_data.connect(self.plot3D.update_Time)
        self.csv_reader.Xobjet_data.connect(self.plot3D.update_X)
        self.csv_reader.Yobjet_data.connect(self.plot3D.update_Y)
        self.csv_reader.Zobjet_data.connect(self.plot3D.update_Z)
        
        self.csv_reader.ImageNames_data.connect(self.video_window.initialize_image_names)
        self.csv_reader.ImageTime_data.connect(self.video_window.initialize_image_time)
        
        self.video_window.update_plot.connect(self.xplot.update_cursor)
        self.video_window.update_plot.connect(self.yplot.update_cursor)
        self.video_window.update_plot.connect(self.zplot.update_cursor)
        
        self.panHSlider.valueChanged.connect(self.plot3D.pan_X)
        self.panVSlider.valueChanged.connect(self.plot3D.pan_Z)
        self.home3Dbutton.clicked.connect(self.plot3D.reset_view)
        self.plot3D.reset_sliders.connect(self.reset_sliders)
        self.video_window.update_3Dplot.connect(self.plot3D.move_marker)
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
        self.hslider1.setRange(0,50)
        self.hslider1.setValue(12)
        self.spinbox1=QtGui.QDoubleSpinBox()
        self.spinbox1.setSingleStep(0.01)
        self.spinbox1.setRange(0,0.5)
        self.spinbox1.setValue(0.12)
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
        self.hslider3.setRange(0,50)
        self.hslider3.setValue(distance)
        self.spinbox3=QtGui.QSpinBox()
        self.spinbox3.setRange(0,50)
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
#                   Modal window for 3D plot parameters
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
        print('try open')
        self.directory = QtGui.QFileDialog.getExistingDirectory(self)
        if os.path.exists(self.directory):
            self.central_widget.video_window.initialize_directory(self.directory)
            self.central_widget.video_window.playButton.setEnabled(True)
            self.central_widget.plot3D.reinitialize_plot3D()
            self.central_widget.video_window.initialize_parameters()
            self.central_widget.csv_reader.open_newCSV(self.directory)
        
    def save_3Dplot(self):
        self.central_widget.plot3D.save_plot()
      
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
    splash.setMask(splash_pix.mask())
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
