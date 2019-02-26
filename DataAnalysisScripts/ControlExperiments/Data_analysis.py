# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 14:23:14 2018

@author: Francois
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import lines
from scipy import stats
import csv
import copy as cp
from matplotlib.lines import Line2D

#--------------------------------------------------------------------------
#                       Plots parameters
#--------------------------------------------------------------------------
from matplotlib import rcParams
from matplotlib import rc
rcParams['axes.titlepad'] = 20 
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)
plt.rc('font', family='serif')

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                          Geometrical parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

# ------------------------------------------------------------------------
# Z axis
# ------------------------------------------------------------------------

gearRatio = 99 + (1044/2057)
encoderCountPerRev_motor = 600
encoderCountPerRev_output = gearRatio*encoderCountPerRev_motor
Radius_X0=88.036                         # distance from the motor axis in mm when X=0 (calculation on illustrator)

def mmPercount_Z(X):
    return (Radius_X0+X)*2*np.pi/encoderCountPerRev_output

mmPercount_Z_simple=(Radius_X0)*2*np.pi/encoderCountPerRev_output

# ------------------------------------------------------------------------
# Y axis
# ------------------------------------------------------------------------
StepsPerRev_Y = 200
mmPerStep_Y = 0.001524

# ------------------------------------------------------------------------
# X axis
# ------------------------------------------------------------------------
StepsPerRev_X = 20
mmPerRev_X = 0.5
mmPerStep_X = mmPerRev_X/StepsPerRev_X

# ------------------------------------------------------------------------
# Beads / focus parameters
# ------------------------------------------------------------------------
diameter_m=(212.+250.)*10**(-6)/2               #diameter of the bead in m
diameter_pix=65                                 #for beads 3
mm_per_pix=10**3*diameter_m/diameter_pix


'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            Theoretical velocity and bead parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
nu=10**(-6)
diameter={'green':[212.,250.],'orange':[212.,250.],'purple':[212.,250.],'blue':[250.,300.],'red':[212.,250.],'pale_blue':[212.,250.]}
density={'green':1.02,'orange':1.04,'purple':1.06,'blue':1.08,'red':1.09,'pale_blue':1.13}
COLORS=['green','orange','purple','blue','red','pale_blue']

def radius(color):
    return (diameter[color][0]+diameter[color][1])/4*10**(-6)

#standart deviation
def sigma_radius(color):
    return (diameter[color][1]-diameter[color][0])/2*10**(-6)/3**0.5
#standart deviation
def sigma_density(color):
    return 0.005/(3**0.5)


def v(color):                             #theoretical speed of the beads in mm/s 
    n= density[color]
    r=radius(color)                        
    return 1000*2*r**2*(n-1)*9.81/(9*nu)

#standart deviation
def sigma_v(color):
    n= density[color]
    r=radius(color)
    return v(color)*(4/r**2*sigma_radius(color)**2+1/(n-1)**2*sigma_density(color)**2)**0.5

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                    Statistical function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

def mean_sum(A):
    return np.sum([A[i][1] for i in range(len(A))])/len(A)

def std_deviation_somme(A):
    s=0
    if len(A)!=0:
        for i in range(len(A)):
            s+=(A[i][1]-mean_sum(A))**2
        s=s/len(A)
    return s

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            Data Initialisation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
Time_Tot=[]
TrackDisp_Tot=[]
WheelRotation_Tot=[]
TrackSpeed_Tot=[]

TimeAuto_Tot=[]
TrackDispAuto_Tot=[]
TrackSpeedAuto_Tot=[]

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                              Data Extraction
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

#address="S:/Projects/GravityMachine/DensityBeads_Control_Wheel_2018_04_31/"

address = '/Volumes/GRAVMACH1/GravityMachine/DensityBeads_Control_Wheel_2018_04_31/'
file="/Tracks/track_1.csv"
Colors_nb={'green':8,'orange':12,'purple':10,'blue':8,'red':10,'pale_blue':8}


#for i in range(len(COLORS)):
for i in range(0,6):
    color=COLORS[i]
    print(color)
    for j in range(1,Colors_nb[color]+1):
        subfolder_nb=str(j)
        folder=color+'Beads/'
        subfolder=color+'Bead'+subfolder_nb
        path=address+folder+subfolder+file
    
        # ------------------------------------------------------------------------
        #                            Extract the data
        # ------------------------------------------------------------------------
        Data=[]
        reader = csv.reader(open(path,newline=''))
        for row in reader:
            Data.append(row)
        Time=[int(Data[i][0]) for i in range(1,len(Data))]             # Time stored is in milliseconds
        Xpos=[int(Data[i][1]) for i in range(1,len(Data))]             # Xpos in motor full-steps
        Ypos=[int(Data[i][2]) for i in range(1,len(Data))]             # Ypos in motor full-steps
        Zpos=[int(Data[i][3]) for i in range(1,len(Data))]             # Zpos is in encoder units
        ImageZcoord=[int(Data[i][4]) for i in range(1,len(Data))]      # In pixel?
        ImageXcoord=[int(Data[i][5]) for i in range(1,len(Data))]      # In pixel?
        ManualTracking=[int(Data[i][6]) for i in range(1,len(Data))]   # 0 for auto, 1 for manual
        
        
        #------------------------------------------------------------------------
        # Find the start of the track. i.e the first instance where the tracking
        # switches from manual to automatic.
        #------------------------------------------------------------------------
        
        startIndex = ManualTracking.index(0)

        
        #------------------------------------------------------------------------
        # Restrict the arrays to start from the index where Automated tracking
        # starts
        #------------------------------------------------------------------------
        
        Time = 0.001*np.array(Time[startIndex:]) # Time in seconds
        Xpos = np.array(Xpos[startIndex:])
        Ypos = np.array(Ypos[startIndex:])
        Zpos = np.array(Zpos[startIndex:])
        ImageZcoord=np.array(ImageZcoord[startIndex:])
        ImageXcoord=np.array(ImageXcoord[startIndex:])
        ManualTracking = np.array(ManualTracking[startIndex:])
        
        
        #Calculate the displacement in mm
        Xdisp= (Xpos - Xpos[0])*mmPerStep_X
        Ydisp= (Ypos - Ypos[0])*mmPerStep_Y 
        Zdisp= (Zpos - Zpos[0])*mmPercount_Z_simple
        Time = Time- Time[0]
        
        wheelRotation=(Zdisp/encoderCountPerRev_output) #number of wheel revolution
        
        # Converting to Physical Units
        ImageCoord_mm=np.array([ImageXcoord*mm_per_pix,ImageZcoord*mm_per_pix])
        #Correction for the beads not being centered in the image
        TrackCoord_mm=np.array([Xdisp + ImageCoord_mm[0], Ydisp, Zdisp + ImageCoord_mm[1]])
        
        
        # ------------------------------------------------------------------------
        #              Compute the time difference and the velocity
        # ------------------------------------------------------------------------
        
        TimeDiff = Time[1:] - Time[:-1];
        Vx=(TrackCoord_mm[0][1:]-TrackCoord_mm[0][:-1])/TimeDiff[:]
        Vy=(TrackCoord_mm[1][1:]-TrackCoord_mm[1][:-1])/TimeDiff[:]
        Vz=(TrackCoord_mm[2][1:]-TrackCoord_mm[2][:-1])/TimeDiff[:]
        
        TrackVel = [Vx,Vy,Vz]
        
        TrackSpeed = [np.abs(Vx),np.abs(Vy),np.abs(Vz),color]      #velocity in absolute value
        
        
        # ------------------------------------------------------------------------
        #                         Select automated part
        # ------------------------------------------------------------------------
        
        TimeAuto = []
        TrackCoordAuto=[[],[],[],color]
        TrackSpeedAuto=[[],[],[],color]
        OneTrack=True                          # = True if there is only one automated track (otherwise we do not consider the data set)
        HasBeenAuto=False                      #enables to know if it is the time the auto-mode is taken into account
        TimetoWait=0                           #if TimetoWait=x the first 'x's of the auto mode are not taken into account
                           
        for k in range(len(Time)-1):
            if (ManualTracking[k]==0 and Time[k]>TimetoWait):
                HasBeenAuto=True
                TimeAuto.append(Time[k])
                for l in range(3):
                    TrackCoordAuto[l].append(TrackCoord_mm[l][k])
                    TrackSpeedAuto[l].append(TrackSpeed[l][k])
            if (k!=0 and HasBeenAuto==True and ManualTracking[k]==1 and ManualTracking[k-1]==1 ):
                OneTrack=False
  
        
        if OneTrack:                                  #deepcopy: To prevent issues linked to the problem of mutable variable
            Time_Tot.append(cp.deepcopy(Time))                     
            TrackDisp_Tot.append(cp.deepcopy(TrackCoord_mm))
            WheelRotation_Tot.append(cp.deepcopy(wheelRotation))          
            TrackSpeed_Tot.append(cp.deepcopy(TrackSpeed))
            TimeAuto_Tot.append(cp.deepcopy(TimeAuto))
            TrackDispAuto_Tot.append(cp.deepcopy(TrackCoordAuto))
            TrackSpeedAuto_Tot.append(cp.deepcopy(TrackSpeedAuto))
            

        fig=plt.figure()     
        plt.plot(TimeAuto,TrackSpeedAuto[2])
        plt.savefig(address+folder+subfolder+'/speed.png')
        plt.close(fig)
        
        fig=plt.figure()     
        plt.plot(Time,TrackCoord_mm[2])
        plt.savefig(address+folder+subfolder+'/Zpos.png')
        plt.close(fig)

ZSpeedAutoGreen=[]
ZSpeedAutoOrange=[]
ZSpeedAutoPurple=[]
ZSpeedAutoBlue=[]
ZSpeedAutoRed=[]
ZSpeedAutoPale_Blue=[]
colornb=[0,0,0,0,0,0]



for i in range(len(TrackSpeed_Tot)):
    if TrackSpeed_Tot[i][3]=='green':
        colornb[0]+=1
        ZSpeedAutoGreen=np.concatenate((ZSpeedAutoGreen,TrackSpeed_Tot[i][2]))
    elif TrackSpeed_Tot[i][3]=='orange':
        colornb[1]+=1
        ZSpeedAutoOrange=np.concatenate((ZSpeedAutoOrange,TrackSpeed_Tot[i][2]))
    elif TrackSpeed_Tot[i][3]=='purple':
        colornb[2]+=1
        ZSpeedAutoPurple=np.concatenate((ZSpeedAutoPurple,TrackSpeed_Tot[i][2]))
    elif TrackSpeed_Tot[i][3]=='blue':
        colornb[3]+=1
        ZSpeedAutoBlue=np.concatenate((ZSpeedAutoBlue,TrackSpeed_Tot[i][2]))
    elif TrackSpeed_Tot[i][3]=='red':
        colornb[4]+=1
        ZSpeedAutoRed=np.concatenate((ZSpeedAutoRed,TrackSpeed_Tot[i][2]))
    elif TrackSpeed_Tot[i][3]=='pale_blue':
        colornb[5]+=1
        ZSpeedAutoPale_Blue=np.concatenate((ZSpeedAutoPale_Blue,TrackSpeed_Tot[i][2]))
        

print(colornb)

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                              TrackSpeed Histogram
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

def TraceTheoreticalSpeed(axes,color):
    if color=='pale_blue':
        colorLine='cyan'
    else:
        colorLine=color
    axes.add_artist(lines.Line2D((v(color), v(color)), (-10, 100),linestyle='solid',color = colorLine, linewidth = 1))
     
def TraceTheoreticalDeviation(axes,color):
    if color=='pale_blue':
        colorLine='cyan'
    else:
        colorLine=color
    axes.add_artist(lines.Line2D((v(color)+sigma_v(color), v(color)+sigma_v(color)), (-10, 100),linestyle='dotted',color = colorLine, linewidth = 1)) 
    axes.add_artist(lines.Line2D((v(color)-sigma_v(color), v(color)-sigma_v(color)), (-10, 100),linestyle='dotted',color = colorLine, linewidth = 1)) 

def histo1(color):
    plt.figure()
    
    if color=='green':
        myarray=ZSpeedAutoGreen
    elif color=='orange':
        myarray=ZSpeedAutoOrange
    elif color=='purple':
        myarray=ZSpeedAutoPurple
    elif color=='blue':
        myarray=ZSpeedAutoBlue     
    elif color=='red':
        myarray=ZSpeedAutoRed
    elif color=='pale_blue':
        myarray=ZSpeedAutoPale_Blue
        
    weights = np.ones_like(myarray)/float(len(myarray))
    
    if color=='pale_blue':
        colorLine='cyan'
    else:
        colorLine=color
    plt.hist(myarray,bins=100,weights=weights,color=colorLine)
    
    
    plt.xlabel('Speed on Z axis (mm.s-1)')
    plt.ylabel('Distribution')
    plt.title(color+" Beads")
    plt.xlim(0,7)
    axes = plt.gca()

    TraceTheoreticalSpeed(axes,'green')
    TraceTheoreticalSpeed(axes,'orange')
    TraceTheoreticalSpeed(axes,'purple')
    TraceTheoreticalSpeed(axes,'blue')
    TraceTheoreticalSpeed(axes,'red')
    TraceTheoreticalSpeed(axes,'pale_blue')
    TraceTheoreticalDeviation(axes,'green')
    TraceTheoreticalDeviation(axes,'orange')
    TraceTheoreticalDeviation(axes,'purple')
    TraceTheoreticalDeviation(axes,'blue')
    TraceTheoreticalDeviation(axes,'red')
    TraceTheoreticalDeviation(axes,'pale_blue')
    
    plt.savefig(address+color+'Beads/histogram.png',dpi=400)
    
    

    
    return

histo1('green')

histo1('orange')

histo1('purple')

histo1('blue')

histo1('red')

histo1('pale_blue')




'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                  Linear Regression on automated part
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

SpeedReg=[]

#linear regression
for i in range(len(TrackDispAuto_Tot)):
    slope, intercept, r_value, p_value, std_err = stats.linregress(Time_Tot[i],TrackDisp_Tot[i][2])
    SpeedReg.append([TrackDispAuto_Tot[i][3],np.abs(slope),std_err])   #[color,slope,stderror]
'''
SpeedReg=sorted(SpeedReg,key=lambda SpeedReg:SpeedReg[1] )
'''

SPEEDS=[[],[],[],[],[],[]]
for i in range(len(SpeedReg)):
    SPEEDS[COLORS.index(SpeedReg[i][0])].append(SpeedReg[i])
    
    
velocityWheel=[mean_sum(SPEEDS[i]) for i in range(len(SPEEDS))]
errorWheel=[std_deviation_somme(SPEEDS[i]) for i in range(len(SPEEDS))]
labelWheel=COLORS
y_pos=np.arange(len(SPEEDS))



with plt.style.context(('ggplot')):
    plt.figure()
    
    plt.barh(y_pos, velocityWheel, xerr=errorWheel, align='center')
    plt.yticks(y_pos,labelWheel)

    plt.xlim((0,5))
    plt.title('Tracking velocity values for each data set')
    
    
    axes = plt.gca()
    TraceTheoreticalSpeed(axes,'green')
    TraceTheoreticalSpeed(axes,'orange')
    TraceTheoreticalSpeed(axes,'purple')
    TraceTheoreticalSpeed(axes,'blue')
    TraceTheoreticalSpeed(axes,'red')
    TraceTheoreticalSpeed(axes,'pale_blue')
    TraceTheoreticalDeviation(axes,'green')
    TraceTheoreticalDeviation(axes,'orange')
    TraceTheoreticalDeviation(axes,'purple')
    TraceTheoreticalDeviation(axes,'blue')
    TraceTheoreticalDeviation(axes,'red')
    TraceTheoreticalDeviation(axes,'pale_blue')
    
    plt.xlabel('Speed on Z axis (mm.s-1)')
    plt.ylabel('Type of Beads')
    
    plt.savefig(address+'Velocity_vs_colors.png')
    
    
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                  Comparison with the cuvette
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                               Folder
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

#address2='"S:/Projects/GravityMachine/DensityBeads_Control_Cuvette_2018_04_26'
address2 = '/Volumes/GRAVMACH1/GravityMachine/DensityBeads_Control_Cuvette_2018_04_26'

folder_green='/1-GreenBeads/GreenBeads'
folder_orange='/2-OrangeBeads/OrangeBeads'
folder_purple='/3-PurpleBeads/PurpleBeads'
folder_blue='/4-BlueBeads/BlueBeads'
folder_red='/5-RedBeads/RedBeads'
folder_pale_blue='/6-PaleBlueBeads/PaleBlueBeads'

FOLDERS=[folder_green,folder_orange,folder_purple,folder_blue,folder_red,folder_pale_blue]
COLORS=['green','orange','purple','blue','red','pale_blue']


'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                        Data recuperation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''
SPEEDS=[]
velocityCuvette=[]
errorCuvette=[]

for i in range(len(COLORS)):
    colors=COLORS[i]
    folder=FOLDERS[i]
    SPEED_COLOR=[]
    for j in range(1,11):
        exist=True
        subfolder_nb=str(j)
        Data=[]
        path=address2+folder+subfolder_nb
        try:
            f = csv.reader(open(path+'/'+'SPEED'+colors+subfolder_nb+'.csv',newline=''))
        except FileNotFoundError as F_error:
            print("Here is the error: ", F_error)
            print()
            exist=False
        finally:
            if exist:
                for row in f:
                    Data.append(row[0].split(';'))
                for i in range(1,len(Data[1])):
                    if float(Data[1][i])!=0:
                        SPEED_COLOR.append([colors,float(Data[1][i]),float(Data[2][i])])
    SPEEDS.append(SPEED_COLOR)
    velocityCuvette.append(mean_sum(SPEED_COLOR))
    errorCuvette.append(std_deviation_somme(SPEED_COLOR))

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                        Final plot
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''


plt.figure()

width = 0.35  # the width of the bars

plt.barh(y_pos+width/2, velocityWheel,width, xerr=errorWheel,color=['darkgreen','darkorange','darkviolet','navy','darkred','dodgerblue'])
plt.barh(y_pos-width/2, velocityCuvette,width, xerr=errorCuvette,color=['palegreen','peachpuff','violet','royalblue','salmon','skyblue'])

dark_patch = mpatches.Patch(color='gray', label='Wheel')
pale_patch = mpatches.Patch(color='lightgray', label='Cuvette')

LABEL=[u'Green Beads \n'+u'$r=[212,250] \mu m, d=1,02 \pm 0,005$',u'Orange Beads \n'+r'$r=[212,250] \mu m, d=1,04 \pm 0,005$',u'Purple Beads \n' +r'$r=[212,250] \mu m, d=1,06 \pm 0,005$',u'Blue Beads \n'+r'$r=[250,300] \mu m, d=1,08 \pm 0,005$',u'Red Beads \n'+r'$ r=[212,250] \mu m, d=1,09 \pm 0,005$',u'Pale blue Beads \n'+r'$ r=[212,250] \mu m, d=1,13 \pm 0,005$']
plt.yticks(y_pos,LABEL)

axes = plt.gca()
TraceTheoreticalSpeed(axes,'green')
TraceTheoreticalSpeed(axes,'orange')
TraceTheoreticalSpeed(axes,'purple')
TraceTheoreticalSpeed(axes,'blue')
TraceTheoreticalSpeed(axes,'red')
TraceTheoreticalSpeed(axes,'pale_blue')
TraceTheoreticalDeviation(axes,'green')
TraceTheoreticalDeviation(axes,'orange')
TraceTheoreticalDeviation(axes,'purple')
TraceTheoreticalDeviation(axes,'blue')
TraceTheoreticalDeviation(axes,'red')
TraceTheoreticalDeviation(axes,'pale_blue')

plt.xlabel('Speed on Z axis (mm.s-1)')
plt.ylabel('Type of beads')
plt.xlim((0,5))
plt.title("Beads' velocities, Wheel vs. Cuvette")
lgd=plt.legend(handles=[dark_patch,pale_patch])

#plt.savefig(address+'Velocity_Wheel_vs_Cuvette.png',dpi=400,bbox_extra_artists=(lgd,), bbox_inches='tight')


# Figure of Wheel vs Cuvette data
plt.figure(dpi=150)

width = 0.35  # the width of the bars

plt.scatter(y_pos, velocityCuvette, s=70, facecolors = 'none',edgecolors =['darkgreen','darkorange','darkviolet','navy','darkred','dodgerblue'], marker ='s',label='Cuvette', linewidths = 2)
plt.scatter(y_pos, velocityWheel, s=70, facecolors = 'none',  edgecolors=['darkgreen','darkorange','darkviolet','navy','darkred','dodgerblue'], marker ='o',label = 'Annular Fluidic Chamber', linewidths = 2)
#plt.barh(y_pos-width/2, velocityCuvette,width, xerr=errorCuvette,color=['palegreen','peachpuff','violet','royalblue','salmon','skyblue'])

plt.errorbar(y_pos, velocityWheel,yerr=errorWheel, fmt ='k-',ecolor=['darkgreen','darkorange','darkviolet','navy','darkred','dodgerblue'])
plt.errorbar(y_pos, velocityCuvette,yerr=errorCuvette, fmt ='k--',ecolor=['darkgreen','darkorange','darkviolet','navy','darkred','dodgerblue'])
dark_patch = mpatches.Patch(color='gray', label='Wheel')
pale_patch = mpatches.Patch(color='lightgray', label='Cuvette')

legend_elements = [Line2D([0], [0], marker='o', color='w', label='Annular Fluidic Chamber',
                          markerfacecolor='none', markeredgecolor = 'k', markersize=10)
                   ,Line2D([0], [0], marker='s', color='w', label='Vertical Cuvette',
                          markerfacecolor='none',  markeredgecolor = 'k',markersize=10) ]

#LABEL=[u'Green Beads \n'+u'$r=[212,250] \mu m, d=1,02 \pm 0,005$',u'Orange Beads \n'+r'$r=[212,250] \mu m, d=1,04 \pm 0,005$',u'Purple Beads \n' +r'$r=[212,250] \mu m, d=1,06 \pm 0,005$',u'Blue Beads \n'+r'$r=[250,300] \mu m, d=1,08 \pm 0,005$',u'Red Beads \n'+r'$ r=[212,250] \mu m, d=1,09 \pm 0,005$',u'Pale blue Beads \n'+r'$ r=[212,250] \mu m, d=1,13 \pm 0,005$']
#plt.yticks(y_pos,LABEL)

axes = plt.gca()
#TraceTheoreticalSpeed(axes,'green')
#TraceTheoreticalSpeed(axes,'orange')
#TraceTheoreticalSpeed(axes,'purple')
#TraceTheoreticalSpeed(axes,'blue')
#TraceTheoreticalSpeed(axes,'red')
#TraceTheoreticalSpeed(axes,'pale_blue')
#TraceTheoreticalDeviation(axes,'green')
#TraceTheoreticalDeviation(axes,'orange')
#TraceTheoreticalDeviation(axes,'purple')
#TraceTheoreticalDeviation(axes,'blue')
#TraceTheoreticalDeviation(axes,'red')
#TraceTheoreticalDeviation(axes,'pale_blue')
#LABEL=[u'$d=[212,250], \rho=1,02 \pm 0,005$','$d=[212,250] \mu m, \rho=1,04 \pm 0,005$',u'Purple Beads \n' +r'$r=[212,250] \mu m, d=1,06 \pm 0,005$',u'Blue Beads \n'+r'$r=[250,300] \mu m, d=1,08 \pm 0,005$',u'Red Beads \n'+r'$ r=[212,250] \mu m, d=1,09 \pm 0,005$',u'Pale blue Beads \n'+r'$ r=[212,250] \mu m, d=1,13 \pm 0,005$']
#plt.xticks(y_pos,LABEL)
plt.xlabel('Type of bead')
plt.ylabel('Sedimenting velocity (mm/s)')
#plt.xlim((0,5))
plt.title("Beads' velocities, Wheel vs. Cuvette")

#lgd=plt.legend(['s','o'],['Cuvette','Wheel'])
plt.legend(handles = legend_elements,loc='upper left',fontsize = 12)

'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                        Other Final plot
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

#theoretical_velocity=[v(SpeedReg[i][2]) for i in range(len(SpeedReg))]
#theoretical_error=[sigma_v(SpeedReg[i][2]) for i in range(len(SpeedReg))]
#
#plt.figure()
#
#plt.errorbar(velocityWheel,y_pos,xerr=errorWheel,fmt='o',label='experimental values')
#plt.errorbar(velocityCuvette,y_pos,yerr=errorCuvette,fmt='o',label='theoretical values')
#plt.yticks(y_pos,LABEL)
#plt.ylim((0,3.5))
#
#plt.xlabel('Speed on Z axis (mm.s-1)')
#plt.ylabel('Type of beads')
#  
#lgd=plt.legend()
#
#plt.xlim((0,5))
#
#plt.title("Beads' velocities, Wheel vs. Cuvette")
#plt.savefig(address+'Velocity_Wheel_vs_Cuvette_bis.png',dpi=400,bbox_extra_artists=(lgd,), bbox_inches='tight')
