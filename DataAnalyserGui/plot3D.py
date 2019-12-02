# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:30:49 2018

@author: Francois
"""
import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg
import cmocean as cmocean
import pyqtgraph.opengl as gl
from utils import GridItem as Gd
import cv2 as cv2

import matplotlib.pyplot as plt
import matplotlib as mpl

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            3D Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''        
pg.setConfigOptions(antialias=True)
class plot3D(gl.GLViewWidget):  
    
    reset_sliders=QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None, Width=4, Length = 30):
        super().__init__(parent)
        
        self.Width = Width
        self.prevWidth = self.Width
        self.Length = Length
        self.prevLength = self.Length
        self.x_offset = 0
        self.x_offset_prev = self.x_offset
        self.y_offset = 0
        self.y_offset_prev = self.y_offset

        self.size_traj=0.12
        self.size_grid = 1
        self.size_marker = 1
        self.cmap=cmocean.cm.deep
        self.Z_curr = 0
        self.Z_prev = 0
        
        self.background='black'
        
        if self.background=='black':
            self.grid_color=(1.,1.,1.,0.5)
            self.setBackgroundColor((0.,0.,0.,1.))
        else:
            self.grid_color=(0.,0.,0.,0.5)
            self.setBackgroundColor('w')
                
        self.initial_center=[0,0,0]      #initial view center
        self.initial_position=[20,0,-100] #initial position of the camera relatively to the center
        
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

    def update_extent_values(self):
        self.prevLength = self.Length
        self.x_offset_prev = self.x_offset
        self.y_offset_prev = self.y_offset
        self.prevWidth = self.Width


    def update_width(self, Width):

        self.update_extent_values()
        self.Width = Width
        self.update_grid_extents()

    def update_length(self, Length):

        self.update_extent_values()
        self.Length = Length
        self.update_grid_extents()

    def update_x_offset(self, x_offset):

        self.update_extent_values()
        self.x_offset = x_offset
        self.update_grid_extents()

    def update_y_offset(self, y_offset):
        self.update_extent_values()
        self.y_offset = y_offset
        self.update_grid_extents()
        
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

    def update_grid_extents(self):
        newZsize=np.ceil(self.Z.max()-self.Z.min())

        self.xygrid.setSize(self.Length,self.Width)
        self.xygrid.translate((self.x_offset - self.x_offset_prev) , 0.5*(self.Width - self.prevWidth) + (self.y_offset - self.y_offset_prev), 0)

        self.yzgrid.setSize(newZsize,self.Width,0)
        self.yzgrid.translate(0.5*(self.Length - self.prevLength) + (self.x_offset - self.x_offset_prev), 0.5*(self.Width - self.prevWidth) + (self.y_offset - self.y_offset_prev), 0)

        self.xzgrid.setSize(self.Length,newZsize,0)
        self.xzgrid.translate((self.x_offset - self.x_offset_prev), (self.Width - self.prevWidth) + (self.y_offset - self.y_offset_prev), 0)

        
    def update_grid(self):
        newZsize=np.ceil(self.Z.max()-self.Z.min())
        
        self.xygrid.translate(0, 0, self.Z.min())

        
        self.yzgrid.setSize(newZsize,self.Width,0)
        self.yzgrid.translate(0, 0, 0.5*(newZsize-10)+self.Z.min())
        
        self.xzgrid.setSize(self.Length,newZsize,0)
        self.xzgrid.translate(0, 0, 0.5*(newZsize-10)+self.Z.min())
        
    def generatePgColormap(self):
        colors=self.cmap(np.arange(256))
        self.colors=colors[50:]
        positions = np.linspace(0, 1, len(self.colors))
        pgMap = pg.ColorMap(positions, self.colors)
        self.color_map=mpl.colors.ListedColormap(self.colors)
        return pgMap
    
    #------------------------------------------------------------
    # Action when the video is playing
    #------------------------------------------------------------
    
    def move_marker(self,time):
        index=np.argmin(abs(self.Time-time))
        pos = np.empty((1, 3))
        size = np.empty((1))
        color = np.empty((1, 4))
        pos[0]=(self.X[index],self.Y[index],self.Z[index]); size[0]=self.size_marker;color[0]=(255,0,0,1.0)

        self.marker.setData(pos=pos, size=size, color=color, pxMode=False)
        
        self.Z_curr = self.Z[index]
        dZ = self.Z_curr - self.Z_prev
        
        self.Z_prev = self.Z_curr
        
        self.move_camera(dZ, time)
        # We also should move the camera along with the object and also orbit the camera
        
#    def zoom_camera(self):
        
        
        
    def move_camera(self, Z, time):
        self.initial_center=[0,0,Z]
        self.pan(dx=self.initial_center[0], dy=self.initial_center[1], dz=self.initial_center[2], relative=False)
        
#        self.setCameraPosition(distance)
        # center, dist, elevation, azimuth = self.cameraPosition()
        
        
        
        # Functionality to orbit the camera
        # self.orbit(azim = 1, elev = 0)

    #------------------------------------------------------------
    # TODO when the program opens
    #------------------------------------------------------------

    def initialize_grid(self):

        self.xygrid_pos = self.Width/2

        self.xygrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.xygrid.setSize(self.Length,self.Width)
        self.xygrid.setSpacing(1,1,0)
        self.xygrid.translate(0, self.Width/2, 0)
        self.addItem(self.xygrid)
        
        self.yzgrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.yzgrid.setSize(10,3)
        self.yzgrid.setSpacing(1,1,0)
        self.yzgrid.rotate(90, 0, 1, 0)
        self.yzgrid.translate(self.Length/2, self.Width/2, 5)
        self.addItem(self.yzgrid)
        
        self.xzgrid = Gd.GLGridItem(color=self.grid_color,thickness=self.size_grid)
        self.xzgrid.setSize(self.Length,10)
        self.xzgrid.setSpacing(1,1,0)
        self.xzgrid.rotate(90, 1, 0, 0)
        self.xzgrid.translate(0, self.Width, 5)
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
    
    def get_image_to_save(self,quality):
        image1=self.grabFrameBuffer(False)
        width1=image1.width()
        height1=image1.height()
        width2=200*quality
        factor=width2/width1
        length2=int(factor*height1)
        self.xygrid.setThickness(self.size_grid*factor)
        self.yzgrid.setThickness(self.size_grid*factor)
        self.xzgrid.setThickness(self.size_grid*factor)
        self.scatter_plot.setData(pos=self.pos, size=1.2*factor*self.size_traj, color=self.color, pxMode=False)
        self.scatter_plot.setGLOptions('opaque')
        image=pg.makeQImage(self.renderToArray((width2, length2)))
        self.xygrid.setThickness(self.size_grid)
        self.yzgrid.setThickness(self.size_grid)
        self.xzgrid.setThickness(self.size_grid)
        self.scatter_plot.setData(pos=self.pos, size=self.size_traj, color=self.color, pxMode=False)
        self.scatter_plot.setGLOptions('opaque')
        return image
    
    def save_plot(self,quality=5):
        directory,filetype = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", ".jpg")
        file_directory=directory+filetype
        if len(directory)>4:
            image=self.get_image_to_save(quality)
            image.save(file_directory)
            self.save_colorbar(directory)
            
    def qimage_to_numpy(self,image):
        # Convert a QImage to a numpy array
        #image = image.convertToFormat(QtGui.QImage.Format_ARGB32)
        width = image.width()
        height = image.height()
        ptr = image.constBits()
        img=np.frombuffer(ptr.asstring(image.byteCount()), dtype=np.uint8).reshape(height, width, 4) 
        return img
            
    def export_plot(self,quality):
        image=self.get_image_to_save(quality)
        imagenumpy=self.qimage_to_numpy(image)
        imagenumpy=cv2.cvtColor(imagenumpy,cv2.COLOR_RGBA2RGB)
        return imagenumpy

        
    def save_colorbar(self,directory):
        fig = plt.figure()
        ax1 = fig.add_axes([0.05, 0.05, 0.04, 0.8])
        # Set the colormap and norm to correspond to the data for which
        # the colorbar will be used.
#        colors=self.cmap(np.arange(256))
#        colors=colors[0:-50]
#        cmap=mpl.colors.ListedColormap(self.colors)
        norm = mpl.colors.Normalize(vmin=0, vmax=self.Time[-1])
        
        # ColorbarBase derives from ScalarMappable and puts a colorbar
        # in a specified axes, so it has everything needed for a
        # standalone colorbar.  There are many more kwargs, but the
        # following gives a basic continuous colorbar with ticks
        # and labels.
        mpl.colorbar.ColorbarBase(ax1, cmap=self.color_map,
                                        norm=norm,
                                        orientation='vertical')
        file_directory=directory+'colorbar.svg'
        plt.savefig(file_directory)
        