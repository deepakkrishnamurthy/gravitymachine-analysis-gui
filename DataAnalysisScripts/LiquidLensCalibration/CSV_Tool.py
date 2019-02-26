# -*- coding: utf-8 -*-
"""
Created on Wed May 16 14:24:17 2018

@author: Francois
"""
import csv

'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                             CSV Communication
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class CSV_Register():
    
    def __init__(self,parent=None):
        self.file_directory=None
        self.header = [['Time', 'Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Liquid Lens Freq','Liquid Lens Ampl','Liquid Lens maxGain','Y FM maximum','LEDPanel color R','LEDPanel color G','LEDPanel color B']]
        self.currTrackFile=None
        self.writer=None
        
        
    def start_write(self):
        
        self.currTrackFile=open(self.file_directory,'w')
        csv.register_dialect('myDialect', delimiter=',', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
        self.writer = csv.writer(self.currTrackFile , dialect='myDialect')
        self.writer.writerows(self.header)
        
    def write_line(self,data):
        self.writer.writerows(data)
        
    def close(self):
        self.currTrackFile.close()