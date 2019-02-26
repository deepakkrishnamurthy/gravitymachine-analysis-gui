# -*- coding: utf-8 -*-
"""
Created on Wed May 16 14:29:00 2018

@author: Francois
"""

import serial 	
import platform
import sys
import time
import numpy as np

'''       
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                        Arduino Communication
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
class Arduino_Communication():
    def __init__(self,parent=None):

        self.serialconn=None
        self.platformName = platform.system()

    def send_Integer(self,entier):
        if(sys.version_info[0] < 3):
            self.serialconn.write('%d\n' % entier)
            
        elif(sys.version_info[0] == 3):
            # Serial write for Python 3
            cmd_str0 = '{:d}\n'.format(entier)
            cmd0 = bytearray(cmd_str0.encode())
            self.serialconn.write(cmd0)

    def send_Float(self,entier):
        if(sys.version_info[0] < 3):
            self.serialconn.write('%f\n' % entier)
            
        elif(sys.version_info[0] == 3):
            # Serial write for Python 3
            cmd_str0 = '{:f}\n'.format(entier)
            cmd0 = bytearray(cmd_str0.encode())
            self.serialconn.write(cmd0)
        
            
    def hand_shaking_protocole(self):
        # Read string from Arduino
        print('try handshaking')
        initial_number = ord(self.serialconn.read())
        print(initial_number)
        print('first number received')
        if(initial_number == 1):
            print('\n ------------Communication established with the Arduino------------\n')
            cmd=bytearray(1)
            cmd[0]=2
            self.serialconn.write(cmd)

        second_number = ord(self.serialconn.read())
            
        if(second_number == 2):
            print('\n ------------Communication established both ways with the Arduino------------\n')
        print('handshaking finished')

class Arduino_Wheel(Arduino_Communication):

    def __init__(self,parent=None):
        super().__init__(parent)

    		# Serial communication setup with Arduino initialization
        if self.platformName.lower() == 'darwin':
            self.serialconn = serial.Serial('/dev/cu.usbmodem1411', 115200)
        elif self.platformName.lower() == 'linux':
            self.serialconn = serial.Serial('/dev/ttyACM0', 2000000)
        elif self.platformName.lower() == 'windows':
            self.serialconn=serial.Serial('COM6', 115200,timeout=1)
            
        self.serialconn.close()
        self.serialconn.open()
        time.sleep(2.0)
        print('Serial Connection Open')
        
        self.hand_shaking_protocole()
    
    
    def split_int_2byte(self,number):
        return int(number)% 256,int(number) >> 8

    def split_signed_int_2byte(self,number):
        if number!=abs(number):
            number=65536+number
        return int(number)% 256,int(number) >> 8

    def data2byte_to_int(self,a,b):
        return a+256*b

    def data2byte_to_signed_int(self,a,b):
        nb= a+256*b
        if nb>32767:
            nb=nb-65536
        return nb
        
    def send_to_Arduino(self,command):  #function connected to the signal sent by Object Tracking
        #print('command sent to arduino',command)
        cmd=bytearray(17)
        cmd[0],cmd[1]=self.split_int_2byte(round(command[0]*100))                #liquid_lens_freq
        cmd[2],cmd[3]=self.split_int_2byte(round(command[1]*1000))               #liquid_lens_ampl
        cmd[4],cmd[5]=self.split_int_2byte(round(command[2]*100))                #liquidLens_offset
        cmd[6]=int(command[3])
        cmd[7]=int(command[4])                                                   #Homing
        cmd[8]=int(command[5])                                                   #tracking
        cmd[9],cmd[10]=self.split_signed_int_2byte(round(command[6]*100))         #Xerror
        cmd[11],cmd[12]=self.split_signed_int_2byte(round(command[7]*100))       #Yerror                           
        cmd[13],cmd[14]=self.split_signed_int_2byte(round(command[8]*100))       #Zerror
        cmd[15],cmd[16]=self.split_int_2byte(round(0))#command[9]*10))               #averageDt (millisecond with two digit after coma) BUG
        
        # signed_int:complement to 65536, max value:32767
        #use of round and '*100': transforme a float with two digit after coma into an integer


        self.serialconn.write(cmd)
        #print('commande sent_to arduino',cmd)

        #we send 9 numbers encoded on 16 bytes
    
    def read_from_arduino(self):
        data=[]
        for i in range(12):
            data.append(ord(self.serialconn.read()))
        YfocusPhase = self.data2byte_to_int(data[0],data[1])*2*np.pi/65535.
        Xpos_arduino = self.data2byte_to_signed_int(data[2],data[3])
        Ypos_arduino = self.data2byte_to_signed_int(data[4],data[5])
        Zpos_arduino = data[7]*2**24 + data[8]*2**16+data[9]*2**8 + data[10]
        if data[6]==1:
            Zpos_arduino =-Zpos_arduino

        manualMode = data[11]

        #print('arduino data',[YfocusPhase,Xpos_arduino,Ypos_arduino,Zpos_arduino],manualMode)
        return [YfocusPhase,Xpos_arduino,Ypos_arduino,Zpos_arduino],manualMode



        
    def launch_homing(self):

        self.send_to_Arduino([0,0,0,0,1,0,0,0,0,0]) #[lens_freq,lens_ampl,lensoffset,homing,tracking,Xstep,Ystep,Zstep,Dt]
        
        while not self.serialconn.in_waiting:
            pass
        
        #HomingFlag = int(self.serialconn.read())

        #if HomingFlag == 1:
        #    print('Stage Homing Completed!')
        #else:
            
        #    ('Warning... Stage Homing not completed!')
        
        self.serialconn.read(12) #ping pong game
        
    def launchYstacks(self):
        
        # Send an initial command to the Arduino to start the Y-stack subroutine
        self.send_to_Arduino([0,0,0,0,1,0,0,0,0,0]) #[lens_freq,lens_ampl,lensoffset,homing,tracking,Xstep,Ystep,Zstep,Dt]
        
        while not self.serialconn.in_waiting:
            pass
        
        #HomingFlag = int(self.serialconn.read())

        #if HomingFlag == 1:
        #    print('Stage Homing Completed!')
        #else:
            
        #    ('Warning... Stage Homing not completed!')
        
        self.serialconn.read(12) #ping pong game

    

class Arduino_LED_Panel(Arduino_Communication):
    
    def __init__(self,parent=None):
        
        super().__init__(parent)
        
        self.color=[0,0,0]
        self.isActivated=False
        self.isTrackingActivated=False
        self.previousTimeUpdate=0
        
    		# Serial communication setup with Arduino initialization
        if self.platformName.lower() == 'darwin':
            self.serialconn = serial.Serial('/dev/cu.usbmodem1411', 115200)
        elif self.platformName.lower() == 'linux':
            self.serialconn = serial.Serial('/dev/ttyACM0', 115200)
        elif self.platformName.lower() == 'windows':
            self.serialconn=serial.Serial('COM7', 115200,timeout=1) #Timeout de 1000
            
        self.serialconn.close()
        self.serialconn.open()
        
        self.hand_shaking_protocole()
    
        
    def update_Panel(self):        
        if self.isActivated:
            activation_nb=1
        else:
            activation_nb=0
        colorR=self.color[0]
        colorG=self.color[1]
        colorB=self.color[2]
        self.send_Float(activation_nb)
        self.send_Float(colorR)
        self.send_Float(colorG)
        self.send_Float(colorB)
        print('Instruction sent',[activation_nb,colorR,colorG,colorB])
        self.receive()
        
        
    def setPanel_On(self):
        self.isActivated=True
        self.update_Panel()
        return
    
    def setPanel_Off(self):
        self.isActivated=False
        self.update_Panel()
        return
    
    def update_Color(self,colorRGB):
        self.color=self.rgb_conversion(colorRGB)
        t=time.time()
        if (t-self.previousTimeUpdate>0.5): #maximum ten instruction by second
            self.update_Panel()
            self.previousTimeUpdate=t
        
    def rgb_conversion(self,colorRGB):
        return [int(colorRGB[0]),int(colorRGB[1]),int(colorRGB[2])]
        
    def receive(self):
        print('Arduino')
        print(int(self.serialconn.readline()))
        print(int(self.serialconn.readline()))
        print(int(self.serialconn.readline()))
        print(int(self.serialconn.readline()))
        
    def activateTracking(self,Z):
        #if self.isTrackingActivated:   
        #else:
            
        return