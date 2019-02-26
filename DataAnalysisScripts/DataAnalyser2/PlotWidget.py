# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:33:52 2018

@author: Francois
"""

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters
import cv2 as cv2
from PQG_ImageExporter import PQG_ImageExporter
    
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
        
    def export_plot(self,folder_path):
#        print('try export')
#        pixMap = QtGui.QPixmap.grabWidget(self.plot1)
#        pixMap.save(folder_path+'/temp.png',width=100,height=50)
        
        print('ok1')
        exporter = PQG_ImageExporter(self.plot1.scene(),'black') #'white' for a white back ground
        exporter.parameters()['width'] = 1440   # (note this also affects height parameter)
        print('ok2')
        exporter.export(folder_path+'/temp.png')
        print('ok3')
        return cv2.imread(folder_path+'/temp.png')
