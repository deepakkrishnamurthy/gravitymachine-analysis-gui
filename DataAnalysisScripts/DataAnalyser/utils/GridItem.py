# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 09:13:35 2018

@author: Francois
"""

import numpy as np

from OpenGL.GL import *
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

__all__ = ['GLGridItem']

class GLGridItem(GLGraphicsItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    
    Displays a wire-grame grid. 
    """
    
    def __init__(self, size=None, color=(1,1,1,0.3),thickness=1.0, antialias=True, glOptions='translucent'):
        GLGraphicsItem.__init__(self)
        self.setGLOptions(glOptions)
        self.antialias = antialias
        if size is None:
            size = QtGui.QVector3D(20,20,1)
        self.setSize(size=size)
        self.setSpacing(1, 1, 1)
        
        self.color=color
        self.thickness=thickness

    
    def setSize(self, x=None, y=None, z=None, size=None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z or size=QVector3D().
        """
        if size is not None:
            x = size.x()
            y = size.y()
            z = size.z()
        self.__size = [x,y,z]
        self.update()

        
    def size(self):
        return self.__size[:]
    
    def setColor(self,color):
        self.color=color
        self.update()
        
    def setThickness(self,thickness):
        self.thickness=thickness
        self.update()

    def setSpacing(self, x=None, y=None, z=None, spacing=None):
        """
        Set the spacing between grid lines.
        Arguments can be x,y,z or spacing=QVector3D().
        """
        if spacing is not None:
            x = spacing.x()
            y = spacing.y()
            z = spacing.z()
        self.__spacing = [x,y,z]
        self.update() 

        
    def spacing(self):
        return self.__spacing[:]
        
    def paint(self):
        self.setupGLState()
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            
        glLineWidth(self.thickness)
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        xs,ys,zs = self.spacing()
        xvals = np.arange(-x/2., x/2. + xs*0.001, xs) 
        yvals = np.arange(-y/2., y/2. + ys*0.001, ys) 
        glColor4f(self.color[0],self.color[1],self.color[2],self.color[3])
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x,  yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        
        glEnd()