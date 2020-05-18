# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 20:33:52 2018

@author: Francois
"""

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters
import cv2 as cv2
from PQG_ImageExporter import PQG_ImageExporter

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
pg.setConfigOption('foreground', 'w')
pg.setConfigOptions(antialias=True)
fontTicks = QtGui.QFont()
fontTicks.setPixelSize(18)


class PlotWidget(pg.GraphicsLayoutWidget):

    def __init__(self, title, label=None, color='w', offset = 0, parent=None):
        super().__init__(parent)
        self.title = title
        
        self.offset = offset

        self.Abs = np.array([])
        self.Ord = np.array([])
        self.ax_y = pg.AxisItem('left', pen=pg.mkPen('w', width=2))
        self.ax_x = pg.AxisItem('bottom', pen=pg.mkPen('w', width=2))

        self.ax_x.tickFont = fontTicks
        self.ax_y.tickFont = fontTicks

        # self.ax_x.tickTextOffset = 32
        # self.ax_y.tickTextOffset = 32
        # self.ax_x.tickTextHeight = 32
        # self.ax_y.tickTextheight = 32

        labelStyle = {'color': '#FFF', 'font-size': '12pt'}

        self.ax_x.setLabel('Time (s)', **labelStyle)
        self.ax_y.setLabel(label + '(mm)', **labelStyle)

        self.ax_x.showLabel(True)
        self.ax_y.showLabel(True)

        self.plot1 = self.addPlot(
            title=title, pen=pg.mkPen(color, width=2),
            axisItems={'left': self.ax_y, 'bottom': self.ax_x}
        )

        self.curve = self.plot1.plot(
            self.Abs, self.Ord, pen=pg.mkPen(color, width=3)
        )
        self.curve.setClipToView(True)

        self.plot1.enableAutoRange('xy', True)
        self.plot1.showGrid(x=True, y=True)

        self.point = QtCore.QPointF(0, 0)
        self.vLine = pg.InfiniteLine(
            pos=self.point, angle=90, movable=False, pen=pg.mkPen('r', width=3)
        )

        self.plot1.addItem(self.vLine, ignoreBounds=True)
        # self.plot1.addItem(self.point)

    def update_Time(self, Time_data):
        self.Abs = Time_data

    def update_plot(self, Ord_data):
        self.Ord = Ord_data
        self.curve.setData(self.Abs, self.Ord - self.offset)
        self.curve.setDownsampling(auto=True)

    def update_cursor(self, time):
        self.point = QtCore.QPointF(time, 0)
        self.vLine.setPos(self.point)
        
    def update_offset(self, offset):
        self.offset = offset
        self.update_plot(self.Ord)
        

    def qimage_to_numpy(self, image):
        # Convert a QImage to a numpy array
        width = image.width()
        height = image.height()
        ptr = image.constBits()
        img = np.frombuffer(
            ptr.asstring(image.byteCount()), dtype=np.uint8
        ).reshape(height, width, 4)
        return img

    def export_plot(self, quality, background_color='black'):
        exporter = PQG_ImageExporter(self.plot1.scene(), background_color)
        exporter.parameters()['width'] = 200*quality   # (also affects height)
        img = exporter.export(fileName=None, toBytes=True, copy=False)
        img2 = self.qimage_to_numpy(img)
        img2 = cv2.cvtColor(img2, cv2.COLOR_RGBA2RGB)
        return img2
