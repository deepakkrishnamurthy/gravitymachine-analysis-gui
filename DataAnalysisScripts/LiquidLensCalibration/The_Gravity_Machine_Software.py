# -*- coding: utf-8 -*-


import sys
import os

import cv2
import numpy as np

from pyqtgraph.Qt import QtWidgets,QtCore, QtGui #possible to import form PyQt5 too ... what's the difference? speed? 
import pyqtgraph as pg
#import pyqtgraph.ptime as ptime We use the package time in place
import pyqtgraph.dockarea as dock #used for the drag and dropp plots
from pyqtgraph.dockarea.Dock import DockLabel


from slickpicker.slickpicker import QColorEdit #Color picker package
from utils import rangeslider as rangeslider

import utils.image_enhancement as image_enhancement
import utils.image_processing as image_processing
import utils.units_converter as units_converter
import utils.PID as PID
import utils.YTracking as YTracking


import CSV_Tool
import Arduino_Tool

from aqua.qsshelper import QSSHelper
import utils.dockareaStyle as dstyle

from collections import deque
from queue import Queue
			       

from camera.VideoStream import VideoStream as VideoStream
from camera.ImageSaver import ImageSaver as ImageSaver

import time
import imutils


	
'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                          Object Tracking
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class Object_Tracking(QtCore.QObject):
    
    centroid_glob = QtCore.pyqtSignal(np.ndarray)
    Rect_pt1_pt2 = QtCore.pyqtSignal(np.ndarray)
    plot_data=QtCore.pyqtSignal(np.ndarray)

    def __init__(self,parent=None):
        super().__init__(parent)
        

        #CSV register
        self.csv_register=CSV_Tool.CSV_Register()
        
        #Arduino controller for the wheel
        self.isWheelConnected=True
        if self.isWheelConnected:        
            self.arduino_wheel=Arduino_Tool.Arduino_Wheel()
        else:
            self.arduino_wheel=None
            
        #Arduino Controller for the LED Panel  
        self.isLEDPanelConnected=False
        if self.isLEDPanelConnected:
            self.arduino_led_panel=Arduino_Tool.Arduino_LED_Panel()
        else:
            self.arduino_led_panel=True
            
        #counter and flag
        self.start_saving=False
        self.start_tracking=False      #tracking activation / computer side
        self.start_Y_tracking=False

        self.current_image_name=''     #name of the current image being processing when start_saving=True
        self.manualMode=1              #tracking activation / Arduino side:  manualMode=0 ifthe computer control the wheel
        self.distractionFreeMode = 1   #distractionFreeMode=1 if a crop image is use to track the particule when she has already been flagged
        self.globCounter=0             #number of frame a particule is tracked for a track period
        self.trackGapCounter = 0;      #Keeps track of nb of consecutive frames when object is not tracked
        self.flag=0                    #flag=1 if a centroid is detected on the current frame
        self.SpeedBasedfactor=1        #0<SpeedBasedfactor<1: 1:pure position tracking, 0: pure speed tracking
		
        #image geometrical data (depending on the resolution)
        self.cropRatio=10.
        self.image_width=480           #width of the thresh image received
        self.image_center=False        #np.array size 2
        self.cropSize=48
        
        #data to keep
        self.dequeLen = 20
        
        #Time
        self.begining_Time=0           #Time begin the first time we click on the start_tracking button
        self.Time=deque(maxlen=self.dequeLen)
        self.averageDt=0
        
        #Total angle traveled by the wheel (unit=rad)
        self.ThetaWheel=deque(maxlen=self.dequeLen) #trigonometric sens
        
        #Location of the left corner of the cropped image in the Image referenciel (unit=px)
        self.origLoc=np.array((0,0))   
        
        #Object position in Image referenciel (unit=px)
        self.centroids = deque(maxlen=self.dequeLen) # Create a buffer to store the tracked object centroids
        
        #Image center position in the centerline referentiel (unit=mm)
        self.Ximage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Yimage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Zimage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        
        
        #Object position in the centerline referentiel (unit=mm)
        self.Xobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Yobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Zobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
       
        self.ZobjWheel=deque(maxlen=self.dequeLen)         #Zobjet in the wheel's referentiel
        self.VobjWheel=0                                   #object's speed in the wheel referential
        

        #Y-Tracking parameters and data
        self.ytracker=YTracking.YTracker()       #We use a class in a separate folder to handle all the YTracking
        self.Yerror=0                            #distance in mm to the optimal position

        self.liquid_lens_freq=2
        self.liquid_lens_ampl=0.075
        self.liquid_lens_offset=39.5
        self.prev_Y_order_time=0
        
        #PID
        self.pid_z=PID.PID()
        self.pid_x=PID.PID()
        
        #threshold parameters
        self.lower_HSV=np.array([0,0,0],dtype='uint8') 
        self.upper_HSV=np.array([178,255,255],dtype='uint8')
        
        #color LED panel
        self.LEDpanel_color=[0,0,0]
        
        
    def track(self,image_data_bgr): #receive the new image from the camera (emit(data)) #color tracking or not will be decided by the threshold image received
        
        
        if self.start_tracking:
            #initial parameters
            shouldInitiatePID=False
            self.update_img_param(image_data_bgr) #update image width / cropSize / image_center
            isCropped=False
            
            #first we analyse the image
            if(self.distractionFreeMode == 1 and self.globCounter != 0 and self.flag==1):	
                isCropped=True
                image_data_bgr.shape
                pts,image_data_bgr=image_processing.crop(image_data_bgr, self.centroids[-1],self.cropSize)
                self.Rect_pt1_pt2.emit(pts)
                self.origLoc = pts[0]
                thresh_image = image_processing.threshold_image(image_data_bgr,self.lower_HSV,self.upper_HSV)
                isCentroidFound,centroidLoc = image_processing.find_centroid_basic(thresh_image) 

            elif self.globCounter==0:
                self.origLoc = np.array([0,0])
                thresh_image=image_processing.threshold_image(image_data_bgr,self.lower_HSV,self.upper_HSV)
                isCentroidFound,centroidLoc = image_processing.find_centroid_basic(thresh_image)

            else:
                self.origLoc = np.array([0,0])
                thresh_image=image_processing.threshold_image(image_data_bgr,self.lower_HSV,self.upper_HSV)
                isCentroidFound,centroidLoc = image_processing.find_centroid_enhanced(thresh_image,self.centroids[-1]) 
            
            #Then if a centroid is found we communicate with the arduino and update image position
            if isCentroidFound:  # centroid=False if no object detected
                #receive data from arduino_Wheel
                arduino_data,manualMode=self.get_img_position() #We capt the exact position and wait to know if we could store it or not
                if ((self.manualMode==1 and manualMode==0) or len(self.Time)<=1 or self.trackGapCounter>5):
                    shouldInitiatePID=True
                 
                self.trackGapCounter=0
                self.flag=1
                self.globCounter+=1
                self.manualMode=manualMode

                centroidGlob=self.origLoc+centroidLoc
                self.centroids.append(centroidGlob)
                self.centroid_glob.emit(centroidGlob)  #send the centroid position in order to draw the cercle on the screen
                if not(isCropped):                     #If the image hasn't been cropped already we do it to allow Y-tracking
                    pts,image_data_bgr=image_processing.crop(image_data_bgr, self.centroids[-1],self.cropSize)
                self.update_img_position(arduino_data)
                self.get_Yerror(image_data_bgr)  #update self.Yerror. Need to be after "self.update_img_position"
                self.update_object_position(self.image_center,centroidGlob)  
                
                self.plot_data.emit(np.array([self.Time[-1],self.Xobjet[-1],self.Yobjet[-1],self.Zobjet[-1],self.ZobjWheel[-1],self.ThetaWheel[-1]]))                   #now we have the position of the centroid
                if (self.isWheelConnected):
                    #order corresponds to [liquid_lens param,homing,tracking,Xstep,Ystep,Zstep,DeltaT]
                    orders=self.getOrder(self.image_center,centroidGlob,shouldInitiatePID)
                    self.arduino_wheel.send_to_Arduino(orders)      #send order thanks to the Arduino class
                if self.start_saving:
                    self.register_data()
                    
            else:
                
                self.flag=0
                self.trackGapCounter+=1
                self.globCounter=0
                    
            

    def update_img_param(self,image):
        self.image_center,self.image_width=image_processing.get_image_center_width(image)
        self.cropSize=round(self.image_width/self.cropRatio)

    def get_img_position(self):
    	arduino_data,manualMode=[0 for i in range(4)],1
    	if self.isWheelConnected:
            arduino_data,manualMode=self.arduino_wheel.read_from_arduino()
    	return arduino_data,manualMode
    
    def update_img_position(self,arduino_data):
        
        if self.isWheelConnected:

            [YfocusPhase,Xpos_arduino,Ypos_arduino,Zpos_arduino]=arduino_data

            YfocusPosition=self.liquid_lens_ampl*np.sin(YfocusPhase)
            self.ytracker.update_data(YfocusPhase,YfocusPosition)

            self.Ximage.append(units_converter.X_arduino_to_mm(Xpos_arduino))#We invert the postion of the motor
            self.Yimage.append(units_converter.Y_arduino_to_mm(Ypos_arduino))
            self.Zimage.append(0) #not nul when we will have a Z-axis tracking
            self.Time.append(time.time()-self.begining_Time) #The time is based on the computer, not on the arduino
            self.ThetaWheel.append(units_converter.X_arduino_to_mm(Zpos_arduino)) #Attention, the arduino count in the anti trigo sens
            #self.ThetaWheel.append(-units_converter.theta_arduino_to_rad(Zpos_arduino)) #Attention, the arduino count in the anti trigo sens
            
            
        else:
            self.Ximage.append(0)
            self.Yimage.append(0)
            self.Zimage.append(0)
            self.Time.append(time.time()-self.begining_Time)
            self.ThetaWheel.append(0)
        
        #update average DeltaT (Delta=0 when len(T)=1)
        self.update_averageDt()
        

    def update_object_position(self,imageCenter,centroidGlob):
        #to see if we take into account of not the phase

        self.Xobjet.append(self.Ximage[-1]+units_converter.px_to_mm(centroidGlob[0]- imageCenter[0],self.image_width))
        self.Yobjet.append(self.Yimage[-1])
        self.Zobjet.append(self.Zimage[-1]-units_converter.px_to_mm(centroidGlob[1]- imageCenter[1],self.image_width))

        if len(self.Time)>1:
            self.ZobjWheel.append(self.ZobjWheel[-1]+(self.Zobjet[-1]-self.Zobjet[-2])-units_converter.rad_to_mm(self.ThetaWheel[-1]-self.ThetaWheel[-2],self.Xobjet[-1]))
        else:
            self.ZobjWheel.append(0)

        #update image speed
        self.update_VobjZWheel()

        #print('Velocity of the object (mm/s):',self.VobjWheel)
        
    def get_Yerror(self,cropped_image_bgr):
        self.isYorder=0
        self.Yerror=0
        if self.start_Y_tracking:
            focusMeasure=image_processing.YTracking_Objective_Function(cropped_image_bgr)
            self.Yerror,self.isYorder= self.ytracker.get_error(focusMeasure)



    def getOrder(self,imageCenter,centroidGlob,shouldInitiatePID):
       
        
        Xerror = -units_converter.X_mm_to_step(units_converter.px_to_mm(imageCenter[0]-centroidGlob[0], self.image_width))
        
        Yerror = units_converter.Y_mm_to_step(self.Yerror)
        Yerror=round(Yerror,2)

        Zerror= units_converter.Z_mm_to_step(units_converter.px_to_mm(imageCenter[1]-centroidGlob[1] , self.image_width),self.Xobjet[-1]) #Attention, it is Z_Wheel and not Z stage
                
        #speed based control
        #Zerror=units_converter.Z_mm_to_step(self.SpeedBasedfactor*units_converter.px_to_mm(imageCenter[1]-centroidGlob[1], self.image_width)+self.VobjWheel*0.001*self.averageDt,self.Xobjet[-1])
        
        #PID control
        if shouldInitiatePID:
            self.pid_z.initiate(Zerror,self.Time[-1]) #reset the PID
            self.pid_x.initiate(Xerror,self.Time[-1]) #reset the PID
            Zorder=0
            Xorder=0
        else:
            Zorder=self.pid_z.update(Zerror,self.Time[-1])
            Zorder=round(Zorder,2)
            Xorder=self.pid_x.update(Xerror,self.Time[-1])
            Xorder=round(Xorder,2)
            
        #falling object specific parameter
        #Zorder=min(Zorder,0)

            
        if self.start_Y_tracking:

            return np.array([self.liquid_lens_freq,self.liquid_lens_ampl,self.liquid_lens_offset,self.isYorder,0,self.flag,Xorder,Yerror,Zorder,self.averageDt])
        else:
            return np.array([self.liquid_lens_freq,0,self.liquid_lens_offset,self.isYorder,0,self.flag,Xorder,0,Zorder,self.averageDt])
        
    def register_data(self):
        if self.start_Y_tracking:
            self.csv_register.write_line([[self.Time[-1],self.Xobjet[-1],self.Yobjet[-1],self.Zobjet[-1],self.ThetaWheel[-1],self.ZobjWheel[-1],self.manualMode,self.current_image_name, self.ytracker.YfocusMeasure[-1],self.ytracker.YfocusPhase[-1],self.liquid_lens_freq,self.liquid_lens_ampl,self.ytracker.maxGain, self.ytracker.YmaxFM[-1],self.LEDpanel_color[0],self.LEDpanel_color[1],self.LEDpanel_color[2]]])
        else:
        	self.csv_register.write_line([[self.Time[-1],self.Xobjet[-1],self.Yobjet[-1],self.Zobjet[-1],self.ThetaWheel[-1],self.ZobjWheel[-1],self.manualMode,self.current_image_name, 0,0,self.liquid_lens_freq,self.liquid_lens_ampl,self.ytracker.maxGain, 0,self.LEDpanel_color[0],self.LEDpanel_color[1],self.LEDpanel_color[2]]])
        self.current_image_name='' #reset image name to ''
            
    def setImageName(self,image_name):
        self.current_image_name=image_name

    def tune_pid_z(self,P,I,D):
    	self.pid_z.set_Tuning(P,I,D)
        
    def tune_pid_x(self,P,I,D):
    	self.pid_x.set_Tuning(P,I,D)

    #Calculation of derivatives
    def update_VobjZWheel(self):
        self.VobjWheel=0
        n=min(len(self.Time),10)
        if n==1:
            self.VobjWheel=0
        else:
            for i in range(1,n):
            	self.VobjWheel+=(self.ZobjWheel[-i]-self.ZobjWheel[-(i+1)])/(self.Time[-i]-self.Time[-(i+1)])
            self.VobjWheel=self.VobjWheel/n
	
    def update_averageDt(self):
        self.averageDt=0
        n=min(len(self.Time),5)
        if n==1:
            self.averageDt=0
        else:
            for i in range(1,n-1):

            	self.averageDt+=round(1000*(self.Time[-i]-self.Time[-(i+1)]),2)
            self.averageDt=self.averageDt/n
            self.averageDt=max(300,self.averageDt) #if we track and loose the guy for a long time, dt will be huge, too big for serial communication

    #not the best way to do it ...
    def initialise_data(self): #when click on "stop tracking, data is being reinitialised"

        self.globCounter=0             #number of frame a particule is tracked for a track period
        self.trackGapCounter = 0;      #Keeps track of nb of consecutive frames when object is not tracked
        self.flag=0                    #flag=1 if a centroid is detected on the current frame

        #Time
        self.begining_Time=0           #Time begin the first time we click on the start_tracking button
        self.Time=deque(maxlen=self.dequeLen)
        self.averageDt=0
        
        #Total angle traveled by the wheel (unit=rad)
        self.ThetaWheel=deque(maxlen=self.dequeLen) #trigonometric sens
        
        #Location of the left corner of the cropped image in the Image referenciel (unit=px)
        self.origLoc=np.array((0,0))   
        
        #Object position in Image referenciel (unit=px)
        self.centroids = deque(maxlen=self.dequeLen) # Create a buffer to store the tracked object centroids
        
        #Image center position in the centerline referentiel (unit=mm)
        self.Ximage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Yimage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Zimage=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        
        #Object position in the centerline referentiel (unit=mm)
        self.Xobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Yobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
        self.Zobjet=deque(maxlen=self.dequeLen)            #distance to the centerline of the flow channel
       
        self.ZobjWheel=deque(maxlen=self.dequeLen)         #Zobjet in the wheel's referentiel
        self.VobjWheel=0                                   #object's speed in the wheel referential
        
        #Y-Tracking parameters and data
        self.ytracker=YTracking.YTracker()

'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Video Acquisition
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class Camera_Functions(QtCore.QObject):
    
    image_data = QtCore.pyqtSignal(np.ndarray)  #original image resized with working size

    image_display = QtCore.pyqtSignal(np.ndarray)  #original image resized with working size
    thresh_image_display = QtCore.pyqtSignal(np.ndarray) #thresholded image (working size)
    plot_data_display=QtCore.pyqtSignal(np.ndarray) #sent the data to plot
    
    fps_data = QtCore.pyqtSignal(np.ndarray)  #real number of frame per second received by Camera_Function
    image_name = QtCore.pyqtSignal(str)  #name of the image being recorder (so we could match the tracking data with the image)
    image_width=QtCore.pyqtSignal(int)   
    
    def __init__(self,camera_port=0, CAMERA=3, parent=None): #CAMERA=2 corresponds to a classic webcam
        super().__init__(parent)
        
        self.camResolution=(640,480)
        self.camFPS=30
        self.CAMERA=CAMERA
        
        
        #thread to et the image
        self.VideoSrc = VideoStream(camera_port,self.CAMERA,resolution = self.camResolution,framerate = self.camFPS) # Grab a reference to a VideoStream object (cross-platform functionality)
        self.VideoSrc.start()
        time.sleep(2.0)
        
        #thead for saving image
        self.image_saver=ImageSaver()
        
        #imaging parameters
        self.rampFrames=30 #number of frames for the camera warm_up
        self.working_width = 720 # width of the image use for data analasys
        self.maximal_width=720 #width of the image
        
        
        self.fps_sampling=60.  #frequency of the QTimer signals. fps_real<=fps_sampling
        self.fps_displaying=24.
        self.fps_saving=15.
         
        self.fps_sampling_real=0
        self.fps_displaying_real=0
        self.fps_saving_real=0
        
        self.prev_sampling_time=0 #time of the last frame read
        self.prev_displaying_time=0
        self.prev_saving_time=0     
        
        
        self.take_photo=False
        self.photo_path=''
        
        self.record_video=False
        self.video_path=''
        self.saved_img_nb=0 #+1 for each new frame

#        self.timer = QtCore.QTimer() #produce event on a given interval
#        self.timer.setTimerType(0)
#        self.timer.setInterval (1./self.fps_sampling*1000.)#time in ms
#        self.timer.timeout.connect(self.readFrame) #each in interval of time is over, the function readFrame() is launched
        self.timer = QtCore.QBasicTimer()
        
        self.image_setting=False  
        self.contrast=0
        self.brightness=0
        self.saturation=0

        self.isGrayscale=False #if true the working image will be converted in grayscale at the very beginning
         
        self.lower_HSV=np.array([0,0,0],dtype='uint8') 
        self.upper_HSV=np.array([178,255,255],dtype='uint8')
        
        #To draw the cercle on the displayed image
        self.isCircle_todraw=False
        self.centroid=(0,0)
        self.isRect_todraw=False
        self.ptRect1=(0,0)
        self.ptRect2=(0,0)
        
        self.plot_data=np.array([0,0,0,0,0,0]) #receive the data to plot at fps_sampling and resent them at fps_display
    
    def timerEvent(self, event):
        if (event.timerId() != self.timer.timerId()):
            return
        if ((time.time()-self.prev_sampling_time)>1./self.fps_sampling):
            self.readFrame()
            
    def start_displaying(self):
        #camera warmup
        for i in range(self.rampFrames):
            temp = self.VideoSrc.read()    
        self.maximal_width=temp.shape[1]
        self.image_width.emit(temp.shape[1]) #to scale the resolution slider
        self.timer.start(0,self) #Launch the QTimer --> images will begin to be read

    def readFrame(self):
        
        current_time=time.time()
        self.set_fps_real(current_time,'sampling') #calculate the real fps
        
        data_bgr = self.VideoSrc.read() #all images are naturally encode in BRG on a computer
        
        
        # Store the raw image in grayscale format
        #data_gray = image_processing.bgr2gray(data_bgr)

        
        
        #save data if needed, in full quality
        if self.take_photo:
            cv2.imwrite(self.photo_path,data_bgr)
            self.take_photo=False
            

        
        #resize image
        data_bgr = imutils.resize(data_bgr, width = self.working_width)
        data_bgr = np.array( data_bgr,dtype="uint8")                       #To be sure the image is in 8bit int. Maybe useless but do no harm

        if self.record_video and ( (current_time-self.prev_saving_time)>1./self.fps_saving) :
            imageName='IMG_'+str(self.saved_img_nb)+'.tif'
            path=self.video_path+imageName
            
            self.image_saver.wait() #wait for the previous image to be completely
            self.image_saver.register(path,data_bgr)
            
            self.image_name.emit(imageName)
            self.saved_img_nb+=1
            self.set_fps_real(current_time,'saving')
        
        #image enhancement (super costly)
        if self.image_setting:
            data_bgr=image_enhancement.Contrast_Brightness(data_bgr,self.contrast,self.brightness)
            data_bgr=image_enhancement.Saturation(data_bgr,self.saturation)

            
        #Send image to display
        if  (current_time-self.prev_displaying_time)>1./self.fps_displaying:
            
            self.set_fps_real(current_time,'displaying')
            
            thresh_image=image_processing.threshold_image(data_bgr,self.lower_HSV,self.upper_HSV)  #The threshold image as one channel
            
            data_rgb=cv2.cvtColor(data_bgr, cv2.COLOR_BGR2RGB) #pg.ImageItem read images in RGB by default
            
            #rectangle drawing (cropped image)
            if self.isRect_todraw:
                cv2.rectangle(data_rgb, self.ptRect1, self.ptRect2,(0,0,255) , 2) #cv2.rectangle(data_bgr, (20,20), (300,300),(0,0,255) , 2)#
                self.isRect_todraw=False
                
            #cercle drawing in case of a tracked object
            if self.isCircle_todraw:
                cv2.circle(data_rgb,self.centroid, 20, (255,0,0), 2)
                self.isCircle_todraw=False
                
            self.image_display.emit(data_rgb) #send the image to 'image_widget' 
            self.thresh_image_display.emit(thresh_image) #sent to the displayer and to "Object Tracking
            self.fps_data.emit(np.array([self.fps_sampling_real,self.fps_displaying_real,self.fps_saving_real])) 
            self.plot_data_display.emit(self.plot_data) #sent the last plot_data received to the displayer
            
            
        #Sent resized image at the sampling frequency
        self.image_data.emit(data_bgr)
                
    
    def set_fps_real(self,t1,string):    
        if string=='sampling':
            fps2 = 1.0 / (t1-self.prev_sampling_time)
            self.prev_sampling_time=t1
            self.fps_sampling_real=self.fps_sampling_real * 0.9 + fps2* 0.1
        elif string=='displaying':
            fps2 = 1.0 / (t1-self.prev_displaying_time)
            self.prev_displaying_time=t1
            self.fps_displaying_real=self.fps_displaying_real * 0.9 + fps2* 0.1
        elif string=='saving':
            fps2 = 1.0 / (t1-self.prev_saving_time)
            self.prev_saving_time=t1
            self.fps_saving_real=self.fps_saving_real * 0.9 + fps2* 0.1
        
    def draw_circle(self,centroid_Glob):
        self.isCircle_todraw=True
        self.centroid=(centroid_Glob[0],centroid_Glob[1])
    
    def draw_rectangle(self,pts):
        self.isRect_todraw=True
        self.ptRect1=(pts[0][0],pts[0][1])
        self.ptRect2=(pts[1][0],pts[1][1])
        
    def stop(self):
        self.VideoSrc.stop()
        self.timer.stop()
        
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class dockAreaPlot(dock.DockArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        DockLabel.updateStyle = dstyle.updateStylePatched
        self.plot1=PlotWidget('XObjet')
        self.plot2=PlotWidget('YObjet')
        self.plot3=PlotWidget('ZObjet')
        self.plot4=PlotWidget('ZObjWheel')
        self.plot5=PlotWidget('ThetaWheel')
        
        dock1=dock.Dock('XObjet')
        dock1.addWidget(self.plot1)
        
        dock2=dock.Dock('YObjet')
        dock2.addWidget(self.plot2)
        
        dock3=dock.Dock('ZObjet')
        dock3.addWidget(self.plot3)
        
        dock4=dock.Dock('ZObjWheel')
        dock4.addWidget(self.plot4)

        dock5=dock.Dock('ThetaWheel')
        dock5.addWidget(self.plot5)
        
        self.addDock(dock1)
        self.addDock(dock2,'above',dock1)
        self.addDock(dock3,'right',dock1)
        self.addDock(dock4,'above',dock2)
        self.addDock(dock5,'above',dock4)

    def initialise_plot_area(self):
        self.plot1.initialise_plot()
        self.plot2.initialise_plot()
        self.plot3.initialise_plot()
        self.plot4.initialise_plot()
        self.plot5.initialise_plot()


class PlotWidget(pg.GraphicsLayoutWidget):
    def __init__(self,title, parent=None):
        super().__init__(parent)
        self.title=title
        #plot Zobjet
        self.Abscisse=deque(maxlen=20)
        self.Ordonnee=deque(maxlen=20)
        
        self.Abs=[]
        self.Ord=[]
        self.plot1=self.addPlot(title=title)
        self.curve=self.plot1.plot(self.Abs,self.Ord)
        #self.plot1.plot(self.Ord)
        self.plot1.enableAutoRange('xy', True)
        self.plot1.showGrid(x=True, y=True)
        
        
    def update_plot(self,data):
        
        self.Abscisse.append(data[0])
        if self.title=='XObjet':
            self.Ordonnee.append(data[1])
        elif self.title=='YObjet':
            self.Ordonnee.append(data[2])
        elif self.title=='ZObjet':
            self.Ordonnee.append(data[3])
        elif self.title=='ZObjWheel':
            self.Ordonnee.append(data[4])
        elif self.title=='ThetaWheel':
            self.Ordonnee.append(data[5])
            
        self.Abs=list(self.Abscisse)
        self.Ord=list(self.Ordonnee)

        self.curve.setData(self.Abs,self.Ord)

    def initialise_plot(self):
        self.Abscisse=deque(maxlen=20)
        self.Ordonnee=deque(maxlen=20)
        self.Abs=[]
        self.Ord=[]
        self.curve.setData(self.Abs,self.Ord)
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Video_widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class GraphicsLayoutWidget(pg.GraphicsLayoutWidget):
    
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view=self.addViewBox()
        
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img=pg.ImageItem(border='w')
        self.view.addItem(self.img)
        
    def image_data_slot(self, data_rgb):      
        
        data_rgb=cv2.rotate(data_rgb,cv2.ROTATE_90_CLOCKWISE) #pgItem display the image with 90° anticlockwise rotation
        self.img.setImage(data_rgb)
        
        
class ImgDisplayerThread(QtCore.QThread):
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.queue = Queue()
        self.graphic_layout=GraphicsLayoutWidget()

    def __del__(self):
        self.wait()
        
    def run(self):
        while True:
            data_rgb=self.queue.get()
            self.graphic_layout.image_data_slot(data_rgb)
            self.queue.task_done()

    def display_new_img(self,data_rgb):
        
        self.queue.put(data_rgb)
        
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Threshold_image
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
        
class Threshold_image(pg.GraphicsLayoutWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        self.setWindowTitle('threshold_image')
        


        self.view=self.addViewBox()
        
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.img=pg.ImageItem(border='w')
        self.view.addItem(self.img)       

    def thresh_data_slot(self, threshold_image_display):      
        
        threshold_image_display=cv2.rotate(threshold_image_display,cv2.ROTATE_90_CLOCKWISE) #pgItem display the image with 90° anticlockwise rotation
        self.img.setImage(threshold_image_display)
        
class ThresImgDisplayerThread(QtCore.QThread):
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.queue = Queue()
        self.threshold_image=Threshold_image()

    def __del__(self):
        self.wait()
        
    def run(self):
        while True:
            thres_image=self.queue.get()
            self.threshold_image.thresh_data_slot(thres_image)
            self.queue.task_done()
        

    def display_new_thresimg(self,data_rgb):
        self.queue.put(data_rgb)
       
        
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            PID class
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class PIDgroupbox(QtGui.QGroupBox):
    
    def __init__(self,name):
        super().__init__()
        
        self.setTitle(name)
        
                # Slider Groupe P
        self.labelP = QtGui.QLabel('P')
        self.hsliderP = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hsliderP.setRange(0,200)
        self.hsliderP.setValue(100)
        self.spinboxP=QtGui.QDoubleSpinBox()
        self.spinboxP.setRange(0,2)
        self.spinboxP.setSingleStep(0.01)
        self.spinboxP.setValue(1)
        self.hsliderP.valueChanged.connect(self.spinBoxP_setValue)
        self.spinboxP.valueChanged.connect(self.hsliderP_setValue)
        sliderP_layout=QtGui.QHBoxLayout()
        sliderP_layout.addWidget(self.labelP)
        sliderP_layout.addWidget(self.hsliderP)
        sliderP_layout.addWidget(self.spinboxP)
        group_sliderP=QtWidgets.QWidget()
        group_sliderP.setLayout(sliderP_layout)
        
        # Slider Groupe I
        self.labelI = QtGui.QLabel('I')
        self.hsliderI = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hsliderI.setRange(0,10)
        self.hsliderI.setValue(0)
        self.spinboxI=QtGui.QDoubleSpinBox()
        self.spinboxI.setSingleStep(0.01)
        self.spinboxI.setRange(0,0.1)
        self.spinboxI.setValue(0)
        self.hsliderI.valueChanged.connect(self.spinBoxI_setValue)
        self.spinboxI.valueChanged.connect(self.hsliderI_setValue)
        sliderI_layout=QtGui.QHBoxLayout()
        sliderI_layout.addWidget(self.labelI)
        sliderI_layout.addWidget(self.hsliderI)
        sliderI_layout.addWidget(self.spinboxI)
        group_sliderI=QtWidgets.QWidget()
        group_sliderI.setLayout(sliderI_layout)
        
        # Slider Groupe D
        self.labelD = QtGui.QLabel('D')
        self.hsliderD = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hsliderD.setRange(0,100)
        self.hsliderD.setValue(0)
        self.spinboxD=QtGui.QDoubleSpinBox()
        self.spinboxD.setRange(0,1)
        self.spinboxI.setSingleStep(0.01)
        self.spinboxD.setValue(0)
        self.hsliderD.valueChanged.connect(self.spinBoxD_setValue)
        self.spinboxD.valueChanged.connect(self.hsliderD_setValue)
        sliderD_layout=QtGui.QHBoxLayout()
        sliderD_layout.addWidget(self.labelD)
        sliderD_layout.addWidget(self.hsliderD)
        sliderD_layout.addWidget(self.spinboxD)
        group_sliderD=QtWidgets.QWidget()
        group_sliderD.setLayout(sliderD_layout)
        
                # Big PID group
        groupbox_layout_PID = QtGui.QVBoxLayout()
        groupbox_layout_PID.addWidget(group_sliderP)   
        groupbox_layout_PID.addWidget(group_sliderI)
        groupbox_layout_PID.addWidget(group_sliderD)
        
        
        self.setLayout(groupbox_layout_PID)
    
    def spinBoxP_setValue(self,value):
        newvalue=float(value)/100.
        self.spinboxP.setValue(newvalue)

    def hsliderP_setValue(self,value):
        self.hsliderP.setValue(int(value*100)) 

    def spinBoxI_setValue(self,value):
        newvalue=float(value)/100.
        self.spinboxI.setValue(newvalue)

    def hsliderI_setValue(self,value):
        self.hsliderI.setValue(int(value*100)) 

    def spinBoxD_setValue(self,value):
        newvalue=float(value)/100.
        self.spinboxD.setValue(newvalue)

    def hsliderD_setValue(self,value):
        self.hsliderD.setValue(int(value*100))
		

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Central Widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CentralWidget(QtWidgets.QWidget):
    
   
    def __init__(self):
        super().__init__()
        
        #DISPLAYING THREAD
        self.img_displayer_thread=ImgDisplayerThread()
        self.img_displayer_thread.start()
        self.thres_img_displayer_thread=ThresImgDisplayerThread()
        self.thres_img_displayer_thread.start()
        #MOST IMPORTANT WIDGET / CLASS
        
        #Display widget
        #self.image_widget=GraphicsLayoutWidget()
        self.image_widget=self.img_displayer_thread.graphic_layout
        self.plot_widget=dockAreaPlot()
        
        #Camera
        self.camera_functions=Camera_Functions()
        #Tracking class
        self.object_tracking=Object_Tracking()
        
        #OTHER WIDGETS
        self.XPID=PIDgroupbox('X PID Setting')
        self.ZPID=PIDgroupbox('Z PID Setting')
        

    
        # photo button
        self.button_photo = QtGui.QPushButton(' Take a picture')
        self.button_photo.setIcon(QtGui.QIcon('icon/photo.png'))
        self.photoName = QtGui.QLineEdit()
        self.photoName.setPlaceholderText('Name of the next pictures')
       
        # checkable video pushbutton
        self.button_video = QtGui.QPushButton(' Record a video')
        self.button_video.setIcon(QtGui.QIcon('icon/video.png'))
        self.button_video.setCheckable(True)
        self.button_video.setChecked(False)
        self.videoName = QtGui.QLineEdit()
        self.videoName.setPlaceholderText('Name of the next video folder')

        #Choice of the directory
        self.folder_path='C:/Users/Francois/Documents/11-Stage_3A/6-Code_Python'
        self.choose_directory=QtGui.QPushButton('Choose Directory')
        self.choose_directory.setIcon(QtGui.QIcon('icon/folder.png'))
        self.label_directory=QtGui.QLabel('C:/Users/Francois/Desktop')

        
        # GROUPBOX VIDEO SETTING
            
       
        #sampling frequency
        self.label_fps_sampling = QtGui.QLabel('Sampling frequency')
        self.hslider_fps_sampling = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_fps_sampling.setRange(1,200)
        self.hslider_fps_sampling.setValue(self.camera_functions.fps_sampling)
        self.spinbox_fps_sampling=QtGui.QSpinBox()
        self.spinbox_fps_sampling.setRange(1,200)
        self.spinbox_fps_sampling.setValue(self.camera_functions.fps_sampling)
        self.hslider_fps_sampling.valueChanged.connect(self.spinbox_fps_sampling.setValue)
        self.spinbox_fps_sampling.valueChanged.connect(self.hslider_fps_sampling.setValue)
        self.lcd_fps_sampling = QtGui.QLCDNumber()
        self.lcd_fps_sampling.setNumDigits(4)
        self.lcd_fps_sampling.display(self.camera_functions.fps_sampling_real)
        slider_fps_sampling_layout=QtGui.QHBoxLayout()
        slider_fps_sampling_layout.addWidget(self.label_fps_sampling)
        slider_fps_sampling_layout.addWidget(self.hslider_fps_sampling)
        slider_fps_sampling_layout.addWidget(self.spinbox_fps_sampling)
        slider_fps_sampling_layout.addWidget(self.lcd_fps_sampling)
        group_slider_fps_sampling=QtWidgets.QWidget()
        group_slider_fps_sampling.setLayout(slider_fps_sampling_layout)
              
  

        #Displaying frequency
        self.label_fps_displaying = QtGui.QLabel('Displaying frequency')
        self.hslider_fps_displaying = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_fps_displaying.setRange(1,200)
        self.hslider_fps_displaying.setValue(self.camera_functions.fps_displaying)
        self.spinbox_fps_displaying=QtGui.QSpinBox()
        self.spinbox_fps_displaying.setRange(1,200)
        self.spinbox_fps_displaying.setValue(self.camera_functions.fps_displaying)
        self.hslider_fps_displaying.valueChanged.connect(self.spinbox_fps_displaying.setValue)
        self.spinbox_fps_displaying.valueChanged.connect(self.hslider_fps_displaying.setValue)
        self.lcd_fps_displaying = QtGui.QLCDNumber()
        self.lcd_fps_displaying.setNumDigits(4)
        self.lcd_fps_displaying.display(self.camera_functions.fps_displaying_real)
        slider_fps_displaying_layout=QtGui.QHBoxLayout()
        slider_fps_displaying_layout.addWidget(self.label_fps_displaying)
        slider_fps_displaying_layout.addWidget(self.hslider_fps_displaying)
        slider_fps_displaying_layout.addWidget(self.spinbox_fps_displaying)
        slider_fps_displaying_layout.addWidget(self.lcd_fps_displaying)
        group_slider_fps_displaying=QtWidgets.QWidget()
        group_slider_fps_displaying.setLayout(slider_fps_displaying_layout)
        
        #Saving frequency
        self.label_fps_saving = QtGui.QLabel('Saving frequency')
        self.hslider_fps_saving = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_fps_saving.setRange(1,200)
        self.hslider_fps_saving.setValue(self.camera_functions.fps_saving)
        self.spinbox_fps_saving=QtGui.QSpinBox()
        self.spinbox_fps_saving.setRange(1,200)
        self.spinbox_fps_saving.setValue(self.camera_functions.fps_saving)
        self.hslider_fps_saving.valueChanged.connect(self.spinbox_fps_saving.setValue)
        self.spinbox_fps_saving.valueChanged.connect(self.hslider_fps_saving.setValue)
        self.lcd_fps_saving = QtGui.QLCDNumber()
        self.lcd_fps_saving.setNumDigits(4)
        self.lcd_fps_saving.display(self.camera_functions.fps_saving_real)
        slider_fps_saving_layout=QtGui.QHBoxLayout()
        slider_fps_saving_layout.addWidget(self.label_fps_saving)
        slider_fps_saving_layout.addWidget(self.hslider_fps_saving)
        slider_fps_saving_layout.addWidget(self.spinbox_fps_saving)
        slider_fps_saving_layout.addWidget(self.lcd_fps_saving)
        group_slider_fps_saving=QtWidgets.QWidget()
        group_slider_fps_saving.setLayout(slider_fps_saving_layout) 
        
        # resolution
        self.label_res = QtGui.QLabel('Working resolution (width)')
        self.hslider_res = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_res.setRange(100,self.camera_functions.maximal_width)
        self.hslider_res.setValue(self.camera_functions.working_width)
        self.spinbox_res=QtGui.QSpinBox()
        self.spinbox_res.setRange(100,self.camera_functions.maximal_width)
        self.spinbox_res.setValue(self.camera_functions.working_width)
        self.hslider_res.valueChanged.connect(self.spinbox_res.setValue)
        self.spinbox_res.valueChanged.connect(self.hslider_res.setValue)
        slider_res_layout=QtGui.QHBoxLayout()
        slider_res_layout.addWidget(self.label_res)
        slider_res_layout.addWidget(self.hslider_res)
        slider_res_layout.addWidget(self.spinbox_res)
        group_slider_res=QtWidgets.QWidget()
        group_slider_res.setLayout(slider_res_layout)

        #color or gray
        groupbox_type_image = QtGui.QGroupBox('Type of image')
        self.radiobutton_color = QtGui.QRadioButton('Colored image')
        self.radiobutton_gray = QtGui.QRadioButton('Grayscale image')
        self.radiobutton_color.setChecked(True)
        groupbox_layout_type_image = QtGui.QHBoxLayout()
        groupbox_layout_type_image.addWidget(self.radiobutton_color)
        groupbox_layout_type_image.addWidget(self.radiobutton_gray)
        groupbox_type_image.setLayout(groupbox_layout_type_image)
        
        groupbox_layout = QtGui.QVBoxLayout()
        groupbox_layout.addWidget(group_slider_fps_sampling)
        groupbox_layout.addWidget(group_slider_fps_displaying)
        groupbox_layout.addWidget(group_slider_fps_saving)
        groupbox_layout.addWidget(group_slider_res)
        #groupbox_layout.addWidget(groupbox_type_image)
        
        self.groupbox_video_setting = QtGui.QGroupBox('Video Setting')
        self.groupbox_video_setting.setLayout(groupbox_layout)

        

        #GROUPBOX LED PANEL
        layout_LEDPanel=QtGui.QHBoxLayout()
        self.label_LEDcolor=QtGui.QLabel('LED Color')
        self.LED_color_picker=QColorEdit()
        self.button_LED_on = QtGui.QPushButton(' LED Panel On')
        self.button_LED_on.setIcon(QtGui.QIcon('icon/video.png'))
        self.button_LED_on.setCheckable(True)
        self.button_LED_on.setChecked(False)
        self.button_LED_tracking = QtGui.QPushButton('LED Panel Tracking')
        self.button_LED_tracking.setIcon(QtGui.QIcon('icon/video.png'))
        self.button_LED_tracking.setCheckable(True)
        self.button_LED_tracking.setChecked(False)
        layout_LEDPanel.addWidget(self.label_LEDcolor)
        layout_LEDPanel.addWidget(self.LED_color_picker)
        layout_LEDPanel.addWidget(self.button_LED_on)
        layout_LEDPanel.addWidget(self.button_LED_tracking)
        
        self.LEDPanel_box = QtGui.QGroupBox('LED Panel')
        self.LEDPanel_box.setLayout(layout_LEDPanel)
        
        

        # GROUPBOX IMAGE SETTING
        
        # Slider Groupe 1
        self.label1 = QtGui.QLabel('Contrast')
        self.hslider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider1.setRange(-50,150)
        self.hslider1.setValue(0)
        self.spinbox1=QtGui.QSpinBox()
        self.spinbox1.setRange(-150,150)
        self.spinbox1.setValue(0)
        self.hslider1.valueChanged.connect(self.spinbox1.setValue)
        self.spinbox1.valueChanged.connect(self.hslider1.setValue)
        slider1_layout=QtGui.QHBoxLayout()
        slider1_layout.addWidget(self.label1)
        slider1_layout.addWidget(self.hslider1)
        slider1_layout.addWidget(self.spinbox1)
        group_slider1=QtWidgets.QWidget()
        group_slider1.setLayout(slider1_layout)
        
        # Slider Groupe 2
        self.label2 = QtGui.QLabel('Brightness')
        self.hslider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider2.setRange(-100,100)
        self.hslider2.setValue(0)
        self.spinbox2=QtGui.QSpinBox()
        self.spinbox2.setRange(-100,100)
        self.spinbox2.setValue(0)
        self.hslider2.valueChanged.connect(self.spinbox2.setValue)
        self.spinbox2.valueChanged.connect(self.hslider2.setValue)
        slider2_layout=QtGui.QHBoxLayout()
        slider2_layout.addWidget(self.label2)
        slider2_layout.addWidget(self.hslider2)
        slider2_layout.addWidget(self.spinbox2)
        group_slider2=QtWidgets.QWidget()
        group_slider2.setLayout(slider2_layout)
        
        # Slider Groupe 3
        self.label3 = QtGui.QLabel('Saturation')
        self.hslider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider3.setRange(-100,100)
        self.hslider3.setValue(0)
        self.spinbox3=QtGui.QSpinBox()
        self.spinbox3.setRange(-100,100)
        self.spinbox3.setValue(0)
        self.hslider3.valueChanged.connect(self.spinbox3.setValue)
        self.spinbox3.valueChanged.connect(self.hslider3.setValue)
        slider3_layout=QtGui.QHBoxLayout()
        slider3_layout.addWidget(self.label3)
        slider3_layout.addWidget(self.hslider3)
        slider3_layout.addWidget(self.spinbox3)
        group_slider3=QtWidgets.QWidget()
        group_slider3.setLayout(slider3_layout)
        
        # Big group
        groupbox_layout = QtGui.QVBoxLayout()
        groupbox_layout.addWidget(group_slider1)   
        groupbox_layout.addWidget(group_slider2)
        groupbox_layout.addWidget(group_slider3)
        self.image_setting_box = QtGui.QGroupBox('Image Setting')
        self.image_setting_box.setLayout(groupbox_layout)
        self.image_setting_box.setCheckable(True)
        self.image_setting_box.setChecked(self.camera_functions.image_setting)


        # TRACKING PARAMETERS
        
        # checkable start tracking pushbutton
        self.button_tracking = QtGui.QPushButton('Start Tracking')
        self.button_tracking.setCheckable(True)
        self.button_tracking.setChecked(False)
        
        self.button_YTracking = QtGui.QPushButton(' Start Y Tracking')
        self.button_YTracking.setCheckable(True)
        self.button_YTracking.setChecked(False)

        self.button_homing = QtGui.QPushButton(' Launch Homing')

        # cropRatio
        self.label_crop_ratio = QtGui.QLabel('Cropping ratio')
        self.hslider_crop_ratio = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_crop_ratio.setRange(1,50)
        self.hslider_crop_ratio.setValue(self.object_tracking.cropRatio)
        self.spinbox_crop_ratio=QtGui.QSpinBox()
        self.spinbox_crop_ratio.setRange(1,50)
        self.spinbox_crop_ratio.setValue(self.object_tracking.cropRatio)
        self.hslider_crop_ratio.valueChanged.connect(self.spinbox_crop_ratio.setValue)
        self.spinbox_crop_ratio.valueChanged.connect(self.hslider_crop_ratio.setValue)
        slider_crop_ratio_layout=QtGui.QHBoxLayout()
        slider_crop_ratio_layout.addWidget(self.label_crop_ratio)
        slider_crop_ratio_layout.addWidget(self.hslider_crop_ratio)
        slider_crop_ratio_layout.addWidget(self.spinbox_crop_ratio)
        group_slider_crop_ratio=QtWidgets.QWidget()
        group_slider_crop_ratio.setLayout(slider_crop_ratio_layout)
        
        #self.threshold_image_block=Threshold_image()
        self.threshold_image_block=self.thres_img_displayer_thread.threshold_image
        
        group_nb_tracks=QtWidgets.QWidget()
        layout_nb_tracks=QtGui.QHBoxLayout()
        self.label_nb_tracks=QtGui.QLabel('Number of tracked object')
        self.spinbox_nb_tracks = QtGui.QSpinBox()
        self.spinbox_nb_tracks.setValue(1)
        self.spinbox_nb_tracks.setEnabled(False)               #function desactivated for the moment
        layout_nb_tracks.addWidget(self.button_tracking)
        layout_nb_tracks.addWidget(self.button_YTracking)
        layout_nb_tracks.addWidget(self.button_homing)
        #layout_nb_tracks.addWidget(self.label_nb_tracks)
        #layout_nb_tracks.addWidget(self.spinbox_nb_tracks)
        group_nb_tracks.setLayout(layout_nb_tracks)
        
        #Y-TRACKING
        self.groupbox_YTracking = QtGui.QGroupBox('Y Tracking')
        
        # Liquid lens freq
        self.label_lensFreq = QtGui.QLabel('Liquid lens frequency (Hz)')
        self.hslider_lensFreq = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_lensFreq.setRange(1,5)
        self.hslider_lensFreq.setValue(2)
        self.spinbox_lensFreq=QtGui.QSpinBox()
        self.spinbox_lensFreq.setRange(1,5)
        self.spinbox_lensFreq.setValue(2)
        self.hslider_lensFreq.valueChanged.connect(self.spinbox_lensFreq.setValue)
        self.spinbox_lensFreq.valueChanged.connect(self.hslider_lensFreq.setValue)
        slider_lensFreq_layout=QtGui.QHBoxLayout()
        slider_lensFreq_layout.addWidget(self.label_lensFreq)
        slider_lensFreq_layout.addWidget(self.hslider_lensFreq)
        slider_lensFreq_layout.addWidget(self.spinbox_lensFreq)
        group_slider_lensFreq=QtWidgets.QWidget()
        group_slider_lensFreq.setLayout(slider_lensFreq_layout)
        
        # Liquid lens amplitude
        self.label_lensAmpl = QtGui.QLabel('Liquid lens amplitude (mm)')
        self.hslider_lensAmpl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_lensAmpl.setRange(0,150)
        self.hslider_lensAmpl.setValue(2*100*self.object_tracking.liquid_lens_ampl)
        self.spinbox_lensAmpl=QtGui.QDoubleSpinBox()
        self.spinbox_lensAmpl.setRange(0,1.5)
        self.spinbox_lensAmpl.setSingleStep(0.01)
        self.spinbox_lensAmpl.setValue(2*self.object_tracking.liquid_lens_ampl)
        self.hslider_lensAmpl.valueChanged.connect(self.spinbox_lensAmpl_setValue)
        self.spinbox_lensAmpl.valueChanged.connect(self.hslider_lensAmpl_setValue)
        slider_lensAmpl_layout=QtGui.QHBoxLayout()
        slider_lensAmpl_layout.addWidget(self.label_lensAmpl)
        slider_lensAmpl_layout.addWidget(self.hslider_lensAmpl)
        slider_lensAmpl_layout.addWidget(self.spinbox_lensAmpl)
        group_slider_lensAmpl=QtWidgets.QWidget()
        group_slider_lensAmpl.setLayout(slider_lensAmpl_layout)
        
        # Liquid lens gain
        self.label_lensGain = QtGui.QLabel('Liquid lens gain')
        self.hslider_lensGain = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.hslider_lensGain.setRange(0,1000)
        self.hslider_lensGain.setValue(100)
        self.spinbox_lensGain=QtGui.QDoubleSpinBox()
        self.spinbox_lensGain.setRange(0,10)
        self.spinbox_lensGain.setSingleStep(0.01)
        self.spinbox_lensGain.setValue(1)
        self.hslider_lensGain.valueChanged.connect(self.spinbox_lensGain_setValue)
        self.spinbox_lensGain.valueChanged.connect(self.hslider_lensGain_setValue)
        slider_lensGain_layout=QtGui.QHBoxLayout()
        slider_lensGain_layout.addWidget(self.label_lensGain)
        slider_lensGain_layout.addWidget(self.hslider_lensGain)
        slider_lensGain_layout.addWidget(self.spinbox_lensGain)
        group_slider_lensGain=QtWidgets.QWidget()
        group_slider_lensGain.setLayout(slider_lensGain_layout)
        
        groupbox_layout_YTracking = QtGui.QVBoxLayout()
        groupbox_layout_YTracking.addWidget(group_slider_lensFreq) 
        groupbox_layout_YTracking.addWidget(group_slider_lensAmpl)
        groupbox_layout_YTracking.addWidget(group_slider_lensGain) 
        self.groupbox_YTracking.setLayout(groupbox_layout_YTracking)

        #PARAMETERS FOR COLOR TRACKING
        self.group_color_picker=QtWidgets.QWidget()
        layout_color_picker=QtGui.QHBoxLayout()
        self.label_color_picker=QtGui.QLabel('Color of tracked object')
        self.color_picker=QColorEdit()
        layout_color_picker.addWidget(self.label_color_picker)
        layout_color_picker.addWidget(self.color_picker)
        self.group_color_picker.setLayout(layout_color_picker)
        self.group_color_picker.setEnabled(True)
        
        self.group_sliders=QtWidgets.QWidget()
        layout_sliders=QtGui.QGridLayout()
        
        self.label_Hue=QtGui.QLabel('Hue')
        self.range_slider1=rangeslider.QRangeSlider()
        self.range_slider1.setMax(178)
        self.label_Saturation=QtGui.QLabel('Saturation')
        self.range_slider2=rangeslider.QRangeSlider()
        self.label_Vibrance=QtGui.QLabel('Value')
        self.range_slider3=rangeslider.QRangeSlider()
        
        layout_sliders.addWidget(self.label_Hue,0,0,1,1)
        layout_sliders.addWidget(self.range_slider1,0,1,1,1)
        layout_sliders.addWidget(self.label_Saturation,1,0,1,1)
        layout_sliders.addWidget(self.range_slider2,1,1,1,1)
        layout_sliders.addWidget(self.label_Vibrance,2,0,1,1)
        layout_sliders.addWidget(self.range_slider3,2,1,1,1)
        self.group_sliders.setLayout(layout_sliders)
        self.group_sliders.setEnabled(True)
        
        groupbox_tracking_layout1 = QtGui.QGridLayout()
        groupbox_tracking_layout1.addWidget(group_nb_tracks,0,0,1,1)
        groupbox_tracking_layout1.addWidget(group_slider_crop_ratio,1,0,1,1)
        groupbox_tracking_layout1.addWidget(self.groupbox_YTracking,2,0,1,1)
        groupbox_tracking_layout1.addWidget(self.group_color_picker,3,0,1,1)
        groupbox_tracking_layout1.addWidget(self.threshold_image_block,0,1,4,1)
        groupbox_tracking_layout1.setColumnStretch(0,1)
        groupbox_tracking_layout1.setColumnStretch(1,1)
        
        groupbox_tracking_layout2 = QtGui.QVBoxLayout()
        groupbox_tracking_layout2.addLayout(groupbox_tracking_layout1)
        groupbox_tracking_layout2.addWidget(self.group_sliders)

        
        self.groupbox_tracking = QtGui.QGroupBox('Tracking parameters')
        self.groupbox_tracking.setLayout(groupbox_tracking_layout2)

        
        # VERTICAL LAYOUT ON THE LEFT
        vlayout_left = QtGui.QGridLayout()
        vlayout_left.addWidget(self.button_photo,0,0,1,1)
        vlayout_left.addWidget(self.photoName,0,1,1,1)
        vlayout_left.addWidget(self.button_video,1,0,1,1)
        vlayout_left.addWidget(self.videoName,1,1,1,1)
        vlayout_left.addWidget(self.choose_directory,2,0,1,1)
        vlayout_left.addWidget(self.label_directory,2,1,1,1)
        vlayout_left.addWidget(self.groupbox_video_setting,3,0,1,-1)
        vlayout_left.addWidget(self.LEDPanel_box,4,0,1,-1)
        vlayout_left.addWidget(self.image_widget,5,0,1,-1)
        vlayout_left.setContentsMargins(10, 10, 10, 10)

        # VERTICAL LAYOUT ON THE RIGHT
        vlayout_right = QtGui.QGridLayout()
        vlayout_right.addWidget(self.image_setting_box,0,0,1,1)
        vlayout_right.addWidget(self.ZPID,0,1,1,1)
        vlayout_right.addWidget(self.XPID,0,2,1,1)
        vlayout_right.addWidget(self.groupbox_tracking,1,0,1,-1)
        vlayout_right.addWidget(self.plot_widget,2,0,-1,-1)
        vlayout_right.setContentsMargins(10, 10, 10, 10)

        # horizontal layout
        hlayout = QtGui.QHBoxLayout()
        hlayout.addLayout(vlayout_left)
        hlayout.addLayout(vlayout_right)
        hlayout.setStretchFactor(vlayout_right,1)
        hlayout.setStretchFactor(vlayout_left,1)

        # Final action     
        self.setLayout(hlayout)
        
    
        
    def button_video_clicked(self):
        if self.button_video.isChecked():
            self.button_video.setText("Stop recording")
        else:
            self.button_video.setText("Record a video")
            
    def pick_new_directory(self):
        dialog = QtGui.QFileDialog()
        self.folder_path = dialog.getExistingDirectory(None, "Select Folder")
        self.label_directory.setText(self.folder_path)
        
        
    def save_picture(self):
        self.camera_functions.photo_path=self.folder_path+'/'+self.photoName.text()+'.png'
        self.camera_functions.take_photo=True

        
    def save_video(self):
        if self.button_video.isChecked():
            directory=self.folder_path+'/'+self.videoName.text()
            if not os.path.exists(directory):
                os.mkdir(self.folder_path+'/'+self.videoName.text())
                os.mkdir(self.folder_path+'/'+self.videoName.text()+'/images')
                self.camera_functions.video_path=directory+'/images/'
                self.camera_functions.record_video=True
                if self.object_tracking.start_tracking:
                    self.object_tracking.csv_register.file_directory=self.folder_path+'/'+self.videoName.text()+'/track.csv'
                    self.object_tracking.csv_register.start_write()
                    self.object_tracking.start_saving=True
            else:
                self.button_video.setChecked(False)
                QtWidgets.QMessageBox.information(self,'','The folder path already exist')
                
                
        else:
            self.camera_functions.record_video=False
            self.camera_functions.image_nb=0
            if self.object_tracking.start_saving:
                self.object_tracking.start_saving=False
                self.object_tracking.csv_register.close()
                
    def start_tracking(self): #launch the tracking + create a csv
        if self.button_tracking.isChecked():
            if self.object_tracking.start_saving:
                file_name=self.folder_path+'/'+self.videoName.text()+'/track.csv'
                if not os.path.exists( file_name):                                 #if it is the first time start_tracking is True while start_saving is true we initiate the new file
                    self.object_tracking.csv_register.file_directory= file_name
                    self.object_tracking.csv_register.start_write()
            if self.object_tracking.begining_Time==0:
                self.object_tracking.begining_Time=time.time()
            self.object_tracking.start_tracking=True
        else:
            self.object_tracking.start_tracking=False  #reinitialise time,buffer and plots
            self.object_tracking.start_Y_tracking=False
            self.button_YTracking.setChecked(False)
            self.plot_widget.initialise_plot_area()
            self.object_tracking.initialise_data()
            self.object_tracking.ytracker.initialise_ytracking()
            
            
    def set_fps_sampling(self):
        self.camera_functions.fps_sampling=float(self.spinbox_fps_sampling.value())
        #self.camera_functions.timer.setInterval(1./self.camera_functions.fps_sampling*1000.)
        self.set_Y_buffers_lenght()
        
        
    def set_fps_displaying(self):
        self.camera_functions.fps_displaying=float(self.spinbox_fps_displaying.value())
        
    def set_fps_saving(self):
        self.camera_functions.fps_saving=float(self.spinbox_fps_saving.value())
        
        
    def set_maximal_res(self,image_width):
        self.hslider_res.setRange(100,image_width)
        self.spinbox_res.setRange(100,image_width)
        
    def set_res(self,working_width):
        self.camera_functions.working_width=self.hslider_res.value()
        
    def actualise_LED_panel(self,color):
        color_rgb=color.getRgb()
        self.object_tracking.arduino_led_panel.update_Color(color_rgb[0:3])
        self.object_tracking.LEDpanel_color=self.object_tracking.arduino_led_panel.color
        
    def activate_LED_panel(self,fps):
        if self.button_LED_on.isChecked():
            self.object_tracking.arduino_led_panel.setPanel_On()
            self.object_tracking.LEDpanel_color=self.object_tracking.arduino_led_panel.color
        else:
            self.object_tracking.arduino_led_panel.setPanel_Off()
            self.object_tracking.LEDpanel_color=[0,0,0]
            
    def activate_LED_tracking(self,fps):
        if self.button_LED_on.isChecked():
            self.object_tracking.arduino_led_panel.activateTracking(True)
        else:
            self.object_tracking.arduino_led_panel.activateTracking(False)
        
    def actualise_LCD_panels(self,fps):
        self.lcd_fps_sampling.display(round(fps[0]))
        self.lcd_fps_displaying.display(round(fps[1]))
        self.lcd_fps_saving.display(round(fps[2]))
        
        
    def image_setting_action(self):
        self.camera_functions.image_setting=self.image_setting_box.isChecked()
        
    def contrast(self):
        self.camera_functions.contrast=self.hslider1.value()
        
    def brightness(self):
        self.camera_functions.brightness=self.hslider2.value()
        
    def saturation(self):
        self.camera_functions.saturation=self.hslider3.value()
            
        
    def color_tracking(self,color):
        c=color.getRgb()
        color_RGB=[c[0],c[1],c[2]]
        color_HSV=cv2.cvtColor(np.uint8([[color_RGB]]), cv2.COLOR_RGB2HSV)[0][0]
        LOWER=image_processing.default_lower_HSV(color_HSV)
        UPPER=image_processing.default_upper_HSV(color_HSV)
        
        
        self.range_slider1.setRange(int(LOWER[0]),int(UPPER[0]))
        self.range_slider2.setRange(int(LOWER[1]),int(UPPER[1]))
        self.range_slider3.setRange(int(LOWER[2]),int(UPPER[2]))
        
        self.camera_functions.lower_HSV=np.uint8(LOWER)
        self.camera_functions.upper_HSV=np.uint8(UPPER)
        
    def sliders_move(self):
        LOWER=np.array([0,0,0],dtype="uint8")
        UPPER=np.array([178,255,255],dtype="uint8")
        
        LOWER[0],UPPER[0]=self.range_slider1.getRange()
        LOWER[1],UPPER[1]=self.range_slider2.getRange()
        LOWER[2],UPPER[2]=self.range_slider3.getRange()

        self.camera_functions.lower_HSV=np.uint8(LOWER)
        self.object_tracking.lower_HSV=np.uint8(LOWER)
        self.camera_functions.upper_HSV=np.uint8(UPPER)
        self.object_tracking.upper_HSV=np.uint8(UPPER)
        
    def launchHoming(self):
        self.object_tracking.arduino_wheel.launch_homing()
        
    def tune_x_PID_P(self,value):
        self.object_tracking.tune_pid_x(value,-1,-1)
        
    def tune_x_PID_I(self,value):
        self.object_tracking.tune_pid_x(-1,value,-1)
        
    def tune_x_PID_D(self,value):
        self.object_tracking.tune_pid_x(-1,-1,value)
        
    def tune_z_PID_P(self,value):
        self.object_tracking.tune_pid_z(value,-1,-1)
        
    def tune_z_PID_I(self,value):
        self.object_tracking.tune_pid_z(-1,value,-1)
        
    def tune_z_PID_D(self,value):
        self.object_tracking.tune_pid_z(-1,-1,value)
    
    def YTrackingActivation(self):
        
        if self.button_YTracking.isChecked():
            self.button_YTracking.setText("Stop Y Tracking")
            self.object_tracking.start_Y_tracking=True
        else:
            self.button_YTracking.setText("Start Y Tracking")
            self.object_tracking.start_Y_tracking=False
            self.object_tracking.ytracker.initialise_ytracking()

    def set_Y_buffers_lenght(self):
        YdequeLen=round(float(self.camera_functions.fps_sampling)/(self.object_tracking.liquid_lens_freq)) #to get to period of the liquid lens mvmt in the buffers
        self.object_tracking.ytracker.resize_buffers(YdequeLen)

    def spinbox_lensAmpl_setValue(self,value):
        newvalue=float(value)/100.
        self.spinbox_lensAmpl.setValue(newvalue)
        self.object_tracking.liquid_lens_ampl=newvalue/2
        self.object_tracking.ytracker.set_ampl(newvalue/2)

    def hslider_lensAmpl_setValue(self,value):
        self.hslider_lensAmpl.setValue(int(value*100))
        
    def spinbox_lensGain_setValue(self,value):
        newvalue=float(value)/100.
        self.spinbox_lensGain.setValue(newvalue)
        self.object_tracking.ytracker.set_maxGain(newvalue)

    def hslider_lensGain_setValue(self,value):
        self.hslider_lensGain.setValue(int(value*100))

    def liquid_lensFreq(self,value):
        self.object_tracking.liquid_lens_freq=value 
        self.set_Y_buffers_lenght()
        self.object_tracking.ytracker.set_freq(value)
            
    def set_cropRatio(self):
        self.object_tracking.cropRatio=self.spinbox_crop_ratio.value()
        
    def new_plot_data(self,plot_data):
        self.camera_functions.plot_data=plot_data

    def set_isGrayscale(self):
        if self.radiobutton_color.isChecked():
            self.camera_functions.isGrayscale=False
        else:
            self.camera_functions.isGrayscale=True

    #All the connection between the signal and the function define here above
    def connect_all(self):
        
        #save picture / video
        self.button_photo.clicked.connect(self.save_picture)
        self.button_video.clicked.connect(self.button_video_clicked)
        self.button_video.clicked.connect(self.save_video)
        #Directory choice
        self.choose_directory.clicked.connect(self.pick_new_directory)
        #image setting
        self.image_setting_box.clicked.connect(self.image_setting_action)
        self.hslider1.valueChanged.connect(self.contrast)
        self.hslider2.valueChanged.connect(self.brightness)
        self.hslider3.valueChanged.connect(self.saturation)
        
        
        
        #Displaying fps
        self.camera_functions.fps_data.connect(self.actualise_LCD_panels)
        
        self.spinbox_fps_sampling.valueChanged.connect(self.set_fps_sampling)
        self.spinbox_fps_displaying.valueChanged.connect(self.set_fps_displaying)
        self.spinbox_fps_saving.valueChanged.connect(self.set_fps_saving)
        
        self.hslider_res.valueChanged.connect(self.set_res)
         
        self.button_tracking.clicked.connect(self.start_tracking)
        self.button_YTracking.clicked.connect(self.YTrackingActivation)
        self.button_homing.clicked.connect(self.launchHoming)
        
        self.spinbox_crop_ratio.valueChanged.connect(self.set_cropRatio)
        
        self.hslider_lensFreq.valueChanged.connect(self.liquid_lensFreq)
        
        self.color_picker.colorChanged.connect(self.color_tracking)
        self.range_slider1.startValueChanged.connect(self.sliders_move)
        self.range_slider2.startValueChanged.connect(self.sliders_move)
        self.range_slider3.startValueChanged.connect(self.sliders_move)
        self.range_slider1.endValueChanged.connect(self.sliders_move)
        self.range_slider2.endValueChanged.connect(self.sliders_move)
        self.range_slider3.endValueChanged.connect(self.sliders_move)
        
        #Displaying and sending thresh_image
        #self.camera_functions.image_display.connect(self.image_widget.image_data_slot)
        self.camera_functions.image_display.connect(self.img_displayer_thread.display_new_img)
        #self.camera_functions.thresh_image_display.connect(self.threshold_image_block.thresh_data_slot)
        self.camera_functions.thresh_image_display.connect(self.thres_img_displayer_thread.display_new_thresimg)
        self.camera_functions.image_data.connect(self.object_tracking.track)      
        self.camera_functions.image_name.connect(self.object_tracking.setImageName)
        self.camera_functions.image_width.connect(self.set_maximal_res)
        
        #draw circle / rectangle for tracking
        self.object_tracking.centroid_glob.connect(self.camera_functions.draw_circle)
        self.object_tracking.Rect_pt1_pt2.connect(self.camera_functions.draw_rectangle)
        #Displaying Plot
        self.object_tracking.plot_data.connect(self.new_plot_data)
        self.camera_functions.plot_data_display.connect(self.plot_widget.plot1.update_plot)
        self.camera_functions.plot_data_display.connect(self.plot_widget.plot2.update_plot)
        self.camera_functions.plot_data_display.connect(self.plot_widget.plot3.update_plot)
        self.camera_functions.plot_data_display.connect(self.plot_widget.plot4.update_plot)
        self.camera_functions.plot_data_display.connect(self.plot_widget.plot5.update_plot)
        #LED PANEL
        self.LED_color_picker.colorChanged.connect(self.actualise_LED_panel)
        self.button_LED_on.clicked.connect(self.activate_LED_panel)
        self.button_LED_tracking.clicked.connect(self.activate_LED_tracking)
        #Grayscale or colored image
        #self.radiobutton_color.clicked.connect(self.set_isGrayscale)
        #self.radiobutton_gray.clicked.connect(self.set_isGrayscale)
        
        #PID
        self.XPID.spinboxP.valueChanged.connect(self.tune_x_PID_P)
        self.XPID.spinboxI.valueChanged.connect(self.tune_x_PID_I)
        self.XPID.spinboxD.valueChanged.connect(self.tune_x_PID_D)
        
        self.ZPID.spinboxP.valueChanged.connect(self.tune_z_PID_P)
        self.ZPID.spinboxI.valueChanged.connect(self.tune_z_PID_I)
        self.ZPID.spinboxD.valueChanged.connect(self.tune_z_PID_D)


    

'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Main Window
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
        
class MainWindowMill(QtWidgets.QMainWindow):
    
   
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('The WaterMill Software')
        self.setWindowIcon(QtGui.QIcon('icon/icon.png'))
        self.statusBar().showMessage('Ready')
        
        
        #WIDGETS 
        self.central_widget=CentralWidget()  
        self.setCentralWidget(self.central_widget)
           
    
      
    def closeEvent(self, event):
        
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)

        if reply == QtWidgets.QMessageBox.Yes:

            self.central_widget.camera_functions.stop()
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

    #To prevent the error "Kernel died": Spyder is Qt app
    
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
    
    
    #connection and initialisation
    win.central_widget.connect_all()
    win.central_widget.camera_functions.start_displaying()

        
    win.show()
    splash.finish(win)
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
