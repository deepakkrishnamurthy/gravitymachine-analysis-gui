# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 20:23:25 2018

@author: Francois
"""

# -*- coding: utf-8 -*-


import sys
import os

import cv2
import numpy as np

from pyqtgraph.Qt import QtWidgets,QtCore, QtGui #possible to import form PyQt5 too ... what's the difference? speed? 
import pyqtgraph as pg
import matplotlib.pyplot as plt
#from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

import pyqtgraph.opengl as gl
from collections import deque

#from utils import rangeslider as rangeslider


import csv as csv

from aqua.qsshelper import QSSHelper
import time as time


'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Physical parameters
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

mu=1000
g=np.array([0,0,9.81])
eta=10**(-5)

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Point and Stick
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class Referential():
    def __init__(self,pos=np.array([0,0,0]),speed=np.array([0,0,0]),acc=np.array([0,0,0])):
        self.pos=pos
        self.speed=speed
        self.acc=acc
        
class Point(): 
    
    def __init__(self,pos=np.array([0,0,0]),rot_speed=np.array([0,0,0]),rot_acc=np.array([0,0,0])):
        self.pos=pos
        self.rot_speed=rot_speed
        self.rot_acc=rot_acc
        
class Stick():
    def __init__(self,point1,point2,radius,rho):
        self.point1=point1
        self.point2=point2
        self.center_mass=0.5*(point1+point2)
        self.radius=radius
        self.rho
        self.res=50
        self.stick=self.get_stick()
        
    def get_stick(self):
        stick=[]
        alpha=np.linspace(0,1,self.res)
        for a in alpha:
            pos=(1-a)*self.point1.pos+a*self.point2.pos
            speed=(1-a)*self.point1.speed+a*self.point2.speed
            acc=(1-a)*self.point1.acc+a*self.point2.acc
            stick.append(Point(pos,speed,acc))
        
    def lambda_parr(self):
        a=self.point2.pos-self.point1.pos
        l2=np.vdot(a,a)
        return 8*np.pi*mu/np.log(l2/self.radius**2)
    
    def lambda_ortho(self):
        return 2*self.lambda_parr()
        
    def v_parr(self,ref_speed,dl):
        return np.vdot(speed,dl)*dl/np.linalg.norm(dl)
    
    def v_ortho(self,speed,dl):
        return speed-self.v_parr(speed,dl)
    
    #elementary forces
    def visquous_df(self,pointA,pointB):
        speed=(pointA.speed+pointB.speed)/2
        dl=pointB.pos-pointA.pos
        return self.lambda_parr()*self.v_parr(speed,dl)+self.lambda_ortho()*self.v_ortho(speed,dl)
           
    def pes_df(self,pointA,pointB):
        dl=np.linalg.norm(np.pointB.pos-pointA.pos)
        return self.rho*dl*g
    
    #elementary moment
    def visquous_dm(self,pointA,pointB,point0):
        lever_arm=((pointB.pos+pointA.pos)*0.5-point0.pos)
        return np.cross(lever_arm,self.visquous_df(pointA,pointB))
    
    def pes_dm(self,pointA,pointB,point0):
        lever_arm=((pointB.pos+pointA.pos)*0.5-point0.pos)
        return np.cross(lever_arm,self.pes_df(pointA,pointB))
    
    #forces
    def visquous_f(self):
        f=np.array([0,0,0])
        for i in range(len(self.stick)-1):
            f=f+self.visquous_df(self.stick[i],self.stick[i+1])
        return f 
    
    def pes_f(self):
        f=np.array([0,0,0])
        for i in range(len(self.stick)-1):
            f=f+self.pes_df(self.stick[i],self.stick[i+1])
        return f
    
    #moment
    def visquous_m(self,point0):
        m=np.array([0,0,0])
        for i in range(len(self.stick)-1):
            m=m+self.visquous_dm(self.stick[i],self.stick[i+1],point0)
        return m 
    
    def pes_m(self,point0):
        m=np.array([0,0,0])
        for i in range(len(self.stick)-1):
            m=m+self.pes_dm(self.stick[i],self.stick[i+1],point0)
        return m
        
class BrittleStar():
    def __init__(self,point0,point1,point2,rho,radius):
        self.stick1=Stick(point0,point1,rho,radius)
        self.stick2=Stick(point0,point2,rho,radius)
        
    
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Computation
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class Computation(): 
    
    def __init__(self):
        self.A=0
        
        
    def helix(self,t): 
        R=1
        omega=np.pi/2
        Vz=1
        return np.array([R*np.cos(omega*t),R*np.sin(omega*t),(Vz*t)%10]),np.array([R,omega*t*180/np.pi,(Vz*t)%10])
    

    
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Brittle Star
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class BrittleStar(gl.GLGraphicsItem.GLGraphicsItem): 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        body_mesh = gl.MeshData.sphere(rows=20, cols=20,radius=0.2)
        self.body = gl.GLMeshItem(meshdata=body_mesh, smooth=True, color=(1, 1, 1, 1), shader='balloon', glOptions='additive')
        
        arm1_mesh=gl.MeshData.cylinder(rows=20, cols=20, radius=[0.1, 0.1], length=1, offset=False)
        self.arm1 = gl.GLMeshItem(meshdata=arm1_mesh, smooth=True, color=(0, 0, 1, 1), shader='balloon', glOptions='additive')
        self.arm1.translate(0,0,0.1)
        self.arm1.rotate(-50,0,1,0)
        
        arm2_mesh=gl.MeshData.cylinder(rows=10, cols=10, radius=[0.1, 0.1], length=1, offset=False)
        self.arm2 = gl.GLMeshItem(meshdata=arm2_mesh, smooth=True, color=(1, 0, 0, 1), shader='balloon', glOptions='additive')
        self.arm2.translate(0,0,0.1)
        self.arm2.rotate(50,0,1,0)
        
        self.arm1.setParentItem(self)
        self.arm2.setParentItem(self)
        self.body.setParentItem(self)
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            BrittleStar Tail
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class BrittleStar_Tail(gl.GLScatterPlotItem): 
    
    def __init__(self, parent=None):
        
        super().__init__()
        
        self.length=30
        self.tail_pos=np.empty((self.length, 3))
        self.size = np.empty((self.length))
        for i in range(self.length):
            self.tail_pos[i]=(0,0,0)
            self.size[i]=0.1
        color_map = self.generatePgColormap('viridis',self.length)
        self.color = color_map.getLookupTable(start=0.0, stop=1.0, nPts=self.length, alpha=True, mode='float') 
        self.setData(pos=self.tail_pos, size=self.size, color=self.color, pxMode=False)
        
    def generatePgColormap(self,cm_name,n):
        pltMap = plt.get_cmap(cm_name)
        colors = pltMap.colors
        colors = [c + [1.0] for c in colors]
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        return pgMap
    
    def set_tail_initial_pos(self,pos):
        for i in range(len(self.tail_pos)):
            self.tail_pos[i]=(pos[0],pos[1],pos[2])
        self.setData(pos=self.tail_pos, size=self.size, color=self.color, pxMode=False)
    
    def update_tail(self,pos):
        for i in range(len(self.tail_pos)-1):
            self.tail_pos[i]=self.tail_pos[i+1]
        self.tail_pos[-1]=(pos[0],pos[1],pos[2])
        self.setData(pos=self.tail_pos, size=self.size, color=self.color, pxMode=False)
    
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Animation3D
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class Animation3D(gl.GLViewWidget):  
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.computation=Computation()
        
        self.axes=gl.GLAxisItem(size=None, antialias=True, glOptions='translucent')
        self.addItem(self.axes)
        
        self.BrittleStar=BrittleStar()
        self.brittlestar_tail=BrittleStar_Tail()
        
        self.addItem(self.BrittleStar)
        self.addItem(self.brittlestar_tail)
        
        self.xygrid = gl.GLGridItem()
        self.xygrid.setSize(5,5,0)
        self.xygrid.setSpacing(1,1,0)
        self.xygrid.translate(0, 0, 0)
        self.addItem(self.xygrid)
        
        self.timer=QtCore.QTimer()
        self.timer.setInterval(100) #in ms
        self.timer.timeout.connect(self.refresh_anim)
        
        self.initial_pos=np.array([0,0,0])
        self.prev_pos=self.initial_pos
        self.initial_angle=np.array([0,0,0])
        self.prev_angle=self.initial_angle
        
    
        
    def translate_object(self,pos):
        dx=pos[0]-self.prev_pos[0]
        dy=pos[1]-self.prev_pos[1]
        dz=pos[2]-self.prev_pos[2]
        self.BrittleStar.translate(dx,dy,dz)
        self.prev_pos=pos
        
    def rotate_object(self,angle):
        dalphax=angle[0]-self.prev_angle[0]
        dalphay=angle[1]-self.prev_angle[1]
        dalphaz=angle[2]-self.prev_angle[2]
        self.BrittleStar.rotate(dalphax,1,0,0,local=True)
        self.BrittleStar.rotate(dalphay,0,1,0,local=True)
        self.BrittleStar.rotate(dalphaz,0,0,1,local=True)
        self.prev_angle=angle
        
    
        
    def set_initial_pos(self):
        self.initial_pos=np.array([1,0,0])
        self.translate_object(self.initial_pos)
        self.brittlestar_tail.set_tail_initial_pos(self.initial_pos)
        
    def set_initial_angle(self):
        self.rotate_object(np.array([0,0,90]))
        self.prev_angle=np.array([0,0,0])
        
        
    def refresh_anim(self):
        current_time=time.time()-self.start_time
        pos_cart,pos_cyl=self.computation.helix(current_time)
        self.translate_object(pos_cart)
        self.rotate_object([0,0,pos_cyl[1]])
        #imposer ces translations aux points initiaux
        self.brittlestar_tail.update_tail(pos_cart)

    
    def start_anim(self):
        self.set_initial_pos()
        self.set_initial_angle()
        self.timer.start()
        self.start_time=time.time()
        
    def stop_anim(self):
        self.timer.stop()
        
    
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Central Widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CentralWidget(QtWidgets.QWidget):
    
   
    def __init__(self):
        super().__init__()
        self.animation3D=Animation3D()
        
        # checkable video pushbutton
        self.button_start = QtGui.QPushButton('Start Animation')
        self.button_start.setIcon(QtGui.QIcon('icon/video.png'))
        self.button_start.setCheckable(True)
        self.button_start.setChecked(False)
        
        
        v_layout=QtGui.QVBoxLayout()
        v_layout.addWidget(self.animation3D)
        v_layout.addWidget(self.button_start)
        self.setLayout(v_layout)
        
    def start_button(self):
        if self.button_start.isChecked():
            self.animation3D.start_anim()
            self.button_start.setText("Stop Animation")
        else:
            self.animation3D.stop_anim()
            self.button_start.setText("Stop Animation")
        
    def connect_all(self):
        self.button_start.clicked.connect(self.start_button)

        


'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Main Window
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
        
class MainWindowMill(QtWidgets.QMainWindow):
    
   
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('BrittleStar Animation')
        self.setWindowIcon(QtGui.QIcon('icon/icon.png'))
        self.statusBar().showMessage('Ready')
        
        
        #WIDGETS
        self.central_widget=CentralWidget()  
        self.setCentralWidget(self.central_widget)
           
        #Data
        self.directory=''
        
        
        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        
        
        save3DplotAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Save 3D plot', self)        
        save3DplotAction.setShortcut('Ctrl+S')
        save3DplotAction.setStatusTip('Save 3D Plot')
        save3DplotAction.triggered.connect(self.save_3Dplot)
        
        fileMenu.addAction(save3DplotAction)
        
        
        
    def save_3Dplot(self):
        self.central_widget.plot3D_1.save_plot()
      
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