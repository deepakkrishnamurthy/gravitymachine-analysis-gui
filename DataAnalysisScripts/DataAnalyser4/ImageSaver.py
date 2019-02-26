# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 21:24:38 2018

@author: Francois
"""

from threading import Thread
from queue import Queue
import cv2 as cv2
import os as os


class ImageSaver():
    
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.queue_name = Queue()
        self.stopped = False
        self.count=1
           
            
    def start(self,recorded_folder_path,fps):
        # start the thread to read frames from the video stream
        t = Thread(target=self.run, args=())
        t.daemon = True
        t.start()
        
        self.recorded_folder_path=recorded_folder_path
        dir1=self.recorded_folder_path + "/pictures"
        dir2=self.recorded_folder_path + "/plotx"
        dir3=self.recorded_folder_path + "/ploty"
        dir4=self.recorded_folder_path + "/plotz"
        dir5=self.recorded_folder_path + "/plot3d"
        
        print(dir1)
        
        self.dirs= [dir1,dir2,dir3,dir4,dir5]
        self.names=["/IMG_","/IMG_plotx_","/IMG_ploty_","/IMG_plotz_","/IMG_plot3d_"]
        
        for i in range(5):
            if not(os.path.exists(self.dirs[i])):
                print('mk')
                os.mkdir(self.dirs[i])
                print('ok')
            
        return self
        
    
    def run(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next bucket of frame from the stream
            self.images=self.queue.get() #images=[img,plotx,ploty,plotz,plot3d]
            name=self.queue_name.get() 
            self.names[0]= "/"+name
            
            cv2.imwrite(self.dirs[0] + self.names[0] + ".jpg", self.images[0])
            for i in range(1,5):
                cv2.imwrite(self.dirs[i] + self.names[i] +str(self.count) + ".jpg", self.images[i])
            self.count+=1
            self.queue.task_done()
            
    def register(self,img_name,img,plotx,ploty,plotz,plot3d):
        self.queue.put([img,plotx,ploty,plotz,plot3d]) 
        
         # otherwise, read the next bucket of frame from the stream
#        self.images=self.queue.get() #images=[img,plotx,ploty,plotz,plot3d]
#        name=self.queue_name.get() 
#        print('Saved Image: {}'.format(img_name))
#
#        self.images = [img,plotx,ploty,plotz,plot3d]
#        name = img_name
#        self.names[0]= "/"+name[:-4]
#        
#        cv2.imwrite(self.dirs[0] + self.names[0] + ".jpg", self.images[0])
#        for i in range(1,5):
#            cv2.imwrite(self.dirs[i] + self.names[i] +str(self.count) + ".jpg", self.images[i])
#        self.count+=1
        
    def register_name(self,name):
        self.queue_name.put(name)
        
    def wait(self):
        self.queue.join()

            
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True