#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 15:50:13 2018

@author: deepak
"""

import csv as csv
import numpy as np

class CSV_Register():
    
    def __init__(self, header, parent=None):
        self.file_directory=None
        self.header = header
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

#    def readCSV(self,fileName):
#        Data=[]
#        reader = csv.reader(open(fileName,newline=''))
#        for row in reader:
#            Data.append(row)
#        n=len(Data) 
#        
#        #Time=np.array([float(Data[i][0])-float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
#        Time=np.array([float(Data[i][0]) - float(Data[1][0]) for i in range(1,n)])    # Time stored is in seconds
#        Xobj=np.array([float(Data[i][1]) for i in range(1,n)])                    # Xpos in the image in mm
#        Yobj=np.array([float(Data[i][2]) for i in range(1,n)])                    # Ypos in motor full-steps
#        Zobj=np.array([float(Data[i][3]) for i in range(1,n)])                    # Zpos in the image in mm
#        ThetaWheel=np.array([float(Data[i][4]) for i in range(1,n)])
#        ZobjWheel=np.array([float(Data[i][5]) for i in range(1,n)])
#        ManualTracking=np.array([int(Data[i][6]) for i in range(1,n)])              # 0 for auto, 1 for manual
#        ImageName=np.array([Data[i][7] for i in range(1,n)])
#        focusMeasure=np.array([float(Data[i][8]) for i in range(1,n)])
#        focusPhase=np.array([float(Data[i][9]) for i in range(1,n)])
#        MaxfocusMeasure=np.array([float(Data[i][10]) for i in range(1,n)])
#        LED_R = np.array([float(Data[i][11]) for i in range(1,n)])	
#        LED_G = np.array([float(Data[i][12]) for i in range(1,n)])	
#        LED_B = np.array([float(Data[i][13]) for i in range(1,n)])	
#
#        return Time, Xobj, Yobj, Zobj, ThetaWheel, ZobjWheel, ManualTracking,ImageName, focusMeasure, focusPhase, MaxfocusMeasure, LED_R, LED_G, LED_B
