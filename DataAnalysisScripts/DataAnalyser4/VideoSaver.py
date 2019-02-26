# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 21:24:38 2018

@author: Francois
"""

from threading import Thread
from queue import Queue
import cv2 as cv2
from cv2 import VideoWriter, VideoWriter_fourcc


class VideoSaver():
    
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.stopped = False
        self.initiated=False
        self.fps = 30
           
            
    def start(self,recorded_folder_path,fps):
        # start the thread to read frames from the video stream
        t = Thread(target=self.run, args=())
        t.daemon = True
        t.start()
        
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.recorded_folder_path=recorded_folder_path
        self.is_color=True
        self.initiated=False
        self.vid_image=None
        self.vid_plotx=None
        self.vid_ploty=None
        self.vid_plotz=None
        self.vid_plot3D=None
        
        self.fps = 30
        
        return self
        
    
    def run(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            [img,plotx,ploty,plotz,plot3d]=self.queue.get()
            if not(self.initiated):
                size1 = img.shape[1], img.shape[0]
#                self.vid_image=VideoWriter(self.recorded_folder_path+"/images.avi", -1, int(self.fps), size1, self.is_color)

                self.vid_image=VideoWriter(self.recorded_folder_path+"/images.avi", self.fourcc, int(self.fps), size1, self.is_color)
                size2 = plotx.shape[1], plotx.shape[0]
                self.vid_plotx=VideoWriter(self.recorded_folder_path+'/plotx.avi', self.fourcc, int(self.fps), size2, self.is_color)
                size3 = ploty.shape[1], ploty.shape[0]
                self.vid_ploty=VideoWriter(self.recorded_folder_path+'/ploty.avi', self.fourcc, int(self.fps), size3, self.is_color)
                size4 = plotz.shape[1], plotz.shape[0]
                self.vid_plotz=VideoWriter(self.recorded_folder_path+'/plotz.avi', self.fourcc, int(self.fps), size4, self.is_color)
                size5 = plot3d.shape[1], plot3d.shape[0]
                self.vid_plot3d=VideoWriter(self.recorded_folder_path+'/plot3d.avi', self.fourcc, int(self.fps), size5, self.is_color)
                self.initiated=True
                
            self.vid_image.write(img)
            self.vid_plotx.write(plotx)
            self.vid_ploty.write(ploty)
            self.vid_plotz.write(plotz)
            self.vid_plot3d.write(plot3d)
            self.queue.task_done()
            
    def register(self,img,plotx,ploty,plotz,plot3d):
        self.queue.put([img,plotx,ploty,plotz,plot3d]) 
        
    def wait(self):
        self.queue.join()
            
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.vid_image.release()
        self.vid_plotx.release()
        self.vid_ploty.release()
        self.vid_plotz.release()
        self.vid_plot3d.release()