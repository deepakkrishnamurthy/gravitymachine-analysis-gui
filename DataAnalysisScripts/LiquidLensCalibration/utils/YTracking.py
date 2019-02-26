# -*- coding: utf-8 -*-
"""
Created on Thu May 17 12:17:20 2018

@author: Francois
"""

#Tuning the parameters:
    #Integrator max(resp .min): max nb of steps the motor can make in DeltaT

from collections import deque
import scipy.optimize as opt
import scipy.interpolate as interpolate
import scipy.signal as signal
import numpy as np


#the sliding average has to be centered otherwise it induces an additional phase lag
def sliding_average(data,n):
    new_data=[]
    if len(data)<=2*n:
        new_data=data
    else:        
        for j in range(0,n):
            y=data[j]
            for i in range(1,j+1):
                y+=data[j+i]+data[j-i]
            new_data.append(y/(2*j+1))
        for j in range(n,len(data)-n):
            y=data[j]
            for i in range(1,n+1):
                y+=data[j-i]+data[j+i]
            new_data.append(y/(2*n+1))
        for j in range(len(data)-n,len(data)):
            y=data[j]
            for i in range(1,len(data)-j):
                y+=data[j+i]+data[j-i]
            new_data.append(y/(2*(len(data)-1-j)+1))
            
    return new_data

        
    
class YTracker():
    
    def __init__(self,parent=None):
        
        self.YdequeLen=50
        self.YfocusMeasure = deque(maxlen = self.YdequeLen)  #The lenght of the buffer must be ~fps_sampling/liquid_lens_freq
        self.YfocusPosition = deque(maxlen = self.YdequeLen) #in mm
        self.YfocusPhase = deque(maxlen = self.YdequeLen)
        
        #in order to auto tune the gain
        self.YmaxFM = deque(maxlen=10*self.YdequeLen) #stock the value of the focus mesure in order to tune the gain
        self.gain=1
        self.minGain=1
        self.maxGain=1
        
        
        self.ampl=0.075
        self.freq=2
        
        #freq,ampl,phase_lag=[1,2],[0.2,0.2],[6./100*2*np.pi,6./100*2*np.pi]
        freq=[0.2,8,9,10,13.92,12.001,13,13.99,15,0.4999,0.9976,2.0002,3.0000,4.0001,5,6,6.9995]
        phase_lag=[0.067,0.9173,0.9738,1.0315,1.0766,1.1163,1.1367,1.1812,1.1957,0.1335,0.2188,0.3655,0.5047,0.6294,0.7103,0.7759,0.8456]
        self.phase_lag_funct=interpolate.interp1d(freq,phase_lag)
        
        self.phase_lag=self.phase_lag_funct(self.freq)
        
        self.count_between_peaks=0
        self.lastPeakIndex=0 
        
        self.interp_coef=3 #The interpolation operation will increase the number of points
        
        

    def update_data(self,phase,position):
        self.YfocusPhase.append(phase)
        self.YfocusPosition.append(position)
        


    def get_error(self,focusMeasure):
        self.YfocusMeasure.append(focusMeasure)
        
        focusMeasure_list=list(self.YfocusMeasure) #because "YfocusMeasure" is a deque
        focusMeasure_list=sliding_average(focusMeasure_list,2)
        
        focusPosition_list=list( self.YfocusPosition)
        focusPosition_list=sliding_average(focusPosition_list,2) #new change added. Replace sinus interpolation
        
        Yerror=0
        isYorder=0
        
        if len(focusMeasure_list)==self.YdequeLen: #don't do anything while the buffer is not full
            
            try:
                
                new_time,new_focusMeasure=self.make_interpolation(focusMeasure_list)
                new_time,new_focusPosition=self.make_interpolation(focusPosition_list)
                
            except Exception:  #use of try/expect before, when sinus fitting was used because sinus fitting can fail
                print(Exception)
                new_focusMeasure=np.array(focusMeasure_list)
                new_focusPosition=np.array(focusPosition_list)
                pass

            
            #Finding the new peak
            dist=len(new_focusMeasure)/3
            FMmaxIndex=signal.find_peaks(new_focusMeasure,distance=dist,width=9)#return the index and other stats
            FMmaxIndex=FMmaxIndex[0]
            
    
            self.count_between_peaks+=self.interp_coef   #the interpolation give three time more point
                

            if len(FMmaxIndex)>0:
                maxIndex=FMmaxIndex[-1] #we take the last peak
                if (abs(self.lastPeakIndex-self.count_between_peaks-maxIndex)>2):
                    self.lastPeakIndex=maxIndex
                    self.count_between_peaks=0
                    Yerror=new_focusPosition[maxIndex]
                    self.YmaxFM.append(new_focusMeasure[maxIndex])
                    isYorder=1
                    self.update_gain()
                    print('gain',self.gain,'maxGain',self.maxGain)
            
        else: #if the buffer is not full / for testing / not usefull
            new_focusMeasure=np.array(focusMeasure_list)
            new_focusPosition=np.array(focusPosition_list)
        
        # uncomment on the return file to test
        return self.gain*Yerror,isYorder,focusMeasure_list,new_focusMeasure,focusPosition_list,new_focusPosition,self.gain
    
    def update_gain(self): #linear fitting of the gain
        if len(self.YmaxFM)>self.YdequeLen:
            print('Ok')
            self.gain=(self.maxGain*(max(self.YmaxFM)-self.YmaxFM[-1])+self.minGain*(self.YmaxFM[-1]-min(self.YmaxFM)))/(max(self.YmaxFM)-min(self.YmaxFM)+1)
    
    #used when the lens frequency or the sampling frequency changes
    def resize_buffers(self,buffer_size):
        self.YdequeLen=buffer_size
        self.YfocusMeasure=deque(self.YfocusMeasure,maxlen = self.YdequeLen)
        self.YfocusPosition=deque(self.YfocusPosition,maxlen = self.YdequeLen)
        self.YfocusPhase=deque(self.YfocusPhase,maxlen = self.YdequeLen)
        self.YmaxFM=deque(self.YmaxFM,maxlen = self.YdequeLen)
        
    def set_ampl(self,ampl):
        self.ampl=ampl
            
    def set_freq(self,freq):
        self.freq=freq
        self.phase_lag=self.phase_lag_funct(self.freq)
        
    def set_maxGain(self,maxGain):
        self.maxGain=maxGain
    
    #optimisation function for the sinus fitting (see function below)
    def opt_function_pos(self,x,freq,phi,offset):
        return self.ampl*np.sin(2*np.pi*freq*x+phi)+offset
    
        
    def sinus_fitting(self,data):
        
        time=np.linspace(0,1,len(data))
        data_param, data_stat=opt.curve_fit(self.opt_function_pos,time,data,[1.5,np.pi,0],bounds=((1,-np.inf,-np.inf),(2,np.inf,np.inf)))
        new_time=np.linspace(0,1,len(data)*self.interp_coef)
        new_data=self.opt_function_pos(new_time,data_param[0],data_param[1]-self.phase_lag,data_param[2])
        return new_time,new_data
    
    #add points to the focus measure & liquidlens position
    def make_interpolation(self,data):
        time=np.linspace(0,1,len(data))
        f = interpolate.interp1d(time, data)
        new_time=np.linspace(0,1,len(data)*self.interp_coef)
        new_data=f(new_time)
        
        return new_time,new_data
    

    def initialise_ytracking(self):
        self.YfocusMeasure = deque(maxlen = self.YdequeLen)  #The lenght of the buffer must be ~fps_sampling/liquid_lens_freq
        self.YfocusPosition = deque(maxlen = self.YdequeLen) #in mm
        self.YfocusPhase = deque(maxlen = self.YdequeLen)
        
        #in order to auto tune the gain
        self.YmaxFM = deque(maxlen=10*self.YdequeLen) #stock the value of the focus mesure in order to tune the gain
        self.gain=1
        self.count_between_peaks=0
        self.lastPeakIndex=0
        
'''    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                      function for  TEST           
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

#to plot to set of data corresponding to differents physical value on the same plot
def two_scales(ax1, time, data1, data2,label1,label2, c1, c2):

    ax2 = ax1.twinx()

    ax1.plot(time, data1, color=c1)
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel(label1)

    ax2.plot(time, data2, color=c2)
    ax2.set_ylabel(label2)
    return ax1, ax2

# Change color of each axis
def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)
    return None

def get_sampling_freq(Time):
    T1=np.array(Time[:-1])
    T2=np.array(Time[1:])
    return int(round(1/np.mean(T2-T1)))

'''    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                           TEST  part        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

if __name__ == "__main__":
	
    import matplotlib.pyplot as plt
    import csv as csv

    
    path="C:/Users/Francois/Documents/11-Stage_3A/4-Code_Python/YTracking_TestData/"
    file="track.csv"
    
    Data=[]
    reader = csv.reader(open(path+file,newline=''))
    for row in reader:
        Data.append(row)
    n=len(Data)
    
    #correspond to the latest CSV file structure. Will raise error with older ones
    Time=[float(Data[i][0]) for i in range(1,n)]               # Time stored is in milliseconds
    Xobjet=[float(Data[i][1]) for i in range(1,n)]             # Xpos in motor full-steps
    Yobjet=[float(Data[i][2]) for i in range(1,n)]             # Ypos in motor full-steps
    Zobjet=[float(Data[i][3]) for i in range(1,n)]             # Zpos is in encoder units
    ThetaWheel=[float(Data[i][4]) for i in range(1,n)]
    ZobjWheel=[float(Data[i][5]) for i in range(1,n)]
    ManualTracking=[int(Data[i][6]) for i in range(1,n)]       # 0 for auto, 1 for manual
    ImageName=[Data[i][7] for i in range(1,n)]
    focusMeasure=[float(Data[i][8]) for i in range(1,n)]
    LiquidLensPhase=[float(Data[i][9]) for i in range(1,n)]
    LiquidLensFreq=[float(Data[i][10]) for i in range(1,n)]
    LiquidLensAmpl=[float(Data[i][11]) for i in range(1,n)]
    LiquidLensMaxGain=[float(Data[i][12]) for i in range(1,n)]
    MaxfocusMeasure=[float(Data[i][13]) for i in range(1,n)]
    LEDPanelR=[float(Data[i][14]) for i in range(1,n)]
    LEDPanelG=[float(Data[i][15]) for i in range(1,n)]
    LEDPanelB=[float(Data[i][16]) for i in range(1,n)]
    
    focusAmpl=np.mean(LiquidLensAmpl)
    fps_sampling=get_sampling_freq(Time)
    focusfreq=np.mean(LiquidLensFreq)
    maxGain=np.mean(LiquidLensMaxGain)
    buffer_lenght=2*int(round(fps_sampling/focusfreq)) #the buffer size correspond to 2 period of the liquid length
    
    print('focusAmpl',focusAmpl)
    print('fps_sampling',fps_sampling)
    print('focusfreq',focusfreq)
    print('maxGain',maxGain)
    print('buffer_lenght',buffer_lenght)
    
    yerror=[]
    gain_list=[]

    ytracker=YTracker()
    ytracker.resize_buffers(buffer_lenght)
    ytracker.set_ampl(focusAmpl)
    ytracker.set_freq(focusfreq)
    ytracker.set_maxGain(maxGain)
    
    position=[ytracker.ampl*np.sin(LiquidLensPhase[i]) for i in range(len(LiquidLensPhase))]
    focusMeasure=sliding_average(focusMeasure,2)
    
    for i in range(len(LiquidLensPhase)):
        ytracker.update_data(LiquidLensPhase[i],position[i])
        yerr,isYorder,focusMeasure_buffer,new_focusMeasure,focusPosition_buffer,new_focusPosition,gain=ytracker.get_error(focusMeasure[i])
        yerror.append(yerr)
        gain_list.append(gain)


    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, Time, focusMeasure, Yobjet,'focusMeasure','Yobjet', 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('focus measure vs position of stage')
    plt.savefig(path+"FMvsYobjet.png")
    
#    fig, ax = plt.subplots()
#    ax1, ax2 = two_scales(ax, Time, focusMeasure, position,'focusMeasure',"lens'Position", 'r', 'b')
#    color_y_axis(ax1, 'r')
#    color_y_axis(ax2, 'b')
#    plt.title('focus measure vs position of the lens')
#    plt.savefig(path+"FMvsYobjet.png")
    
    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, Time, yerror, position,'yerror',"lens'Position", 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('yerror vs position of the lens')
    plt.savefig(path+"YerrorvslensPos.png")  
    
    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, Time, yerror, gain_list,'yerror',"gain", 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('yerror vs gain')
    plt.savefig(path+"YerrorvsGain.png") 
    
    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, Time, yerror, Yobjet,'yerror','Yobjet', 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('yerror vs position of stage')
    plt.savefig(path+"yerrorvsYobjet.png")



    #%%%%%%%%%%%%%%%%%%%%%%%   Plots on the last buffer    %%%%%%%%%%%%%%%%%%%%%%%%%%%

 
    time1=np.linspace(0,1,len(focusPosition_buffer))
    time2=np.linspace(0,1,len(new_focusPosition))
    
    plt.figure()
    plt.plot(time1,focusMeasure_buffer,'k^:')
    plt.plot(time2,new_focusMeasure)
    plt.title('focus Measure buffer')
    plt.savefig(path+"lastFMbuffer.png")
    
    plt.figure()
    plt.plot(time1,focusPosition_buffer,'k^:')
    plt.plot(time2,new_focusPosition)
    plt.title('focus Position buffer')
    plt.savefig(path+"lastposbuffer.png")
      

    # Create axes
    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, time2, new_focusMeasure, new_focusPosition,'focusMeasure','focusPosition', 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('focus measure vs position on buffer')
    plt.savefig(path+"pos_FM_buffer.png")
    
    maxIndex=signal.find_peaks(new_focusMeasure,distance=len(new_focusMeasure)/3,width=9)
    
    maxIndex=maxIndex[0]
    
    
    maxList=[0 for i in range(len(new_focusMeasure))]
    for i in maxIndex:
        maxList[i]=1
    
    fig, ax = plt.subplots()
    ax1, ax2 = two_scales(ax, time2, new_focusMeasure, maxList,'focusMeasure','maxima', 'r', 'b')
    color_y_axis(ax1, 'r')
    color_y_axis(ax2, 'b')
    plt.title('focus measure vs maxima')
    plt.savefig(path+"pos_FM_buffer.png")  


    plt.show()


