# -*- coding: utf-8 -*-

import numpy as np

    

# --------------------------------------------------
#  X Stepper (Linear Stage)
# --------------------------------------------------

StepsPerRev_X = 20
mmPerRev_X = 0.5            # Pitch of the lead screw in mm

# --------------------------------------------------
#  Y Stepper (Focussing Stage)
# --------------------------------------------------

StepsPerRev_Y = 20
mmPerRev_Y = 0.5 
# StepsPerRev_Y = 20
# mmPerStep_Y = 0.001524;     # Pitch of the lead screw in mm

# --------------------------------------------------
# Z stepper (Phidget Stepper) that drives the Wheel
# --------------------------------------------------

gearRatio = 99+1044/float(2057) 					# Gear ratio of Phidgets Stepper
Rcenter = 87.5 										         # Radius to the center line of the fluidic chamber in mm
mmPerRev_Z = 2*np.pi*Rcenter          			# Displacement along the centerline of wheel in mm for 1 revolution of the output shaft
StepsPerRev_Z = gearRatio * 200            # No:of steps of the main motor shaft for 1 Rev of the output shaft


# --------------------------------------------------
# Z encoder
# --------------------------------------------------
CountsPerRev_Zenc = 600

# --------------------------------------------------
# Distance in mm between the center of the Wheel and the origin of Arduino's Xpos
# --------------------------------------------------

DeltaX_Arduino_mm=102.1 #_A VERIFIER

# --------------------------------------------------
# Distance in mm between the plane of the Wheel and the origin of Arduino's Ypos
# --------------------------------------------------
DeltaY_Arduino_mm=0.35 #_ Non nul apres l'installation d'un second limitSwitch

# --------------------------------------------------
# Functions
# --------------------------------------------------

def px_to_mm(Dist,resolution_width):
    return 1./628/(resolution_width/1440)*Dist   #for a 1440x1080 image

def mm_to_px(Dist,resolution_width):
    return Dist*628*resolution_width/1440

#---------------------------------------------------

def X_mm_to_step(Xmm):
    Xstep=Xmm/mmPerRev_X*StepsPerRev_X
    return Xstep

def Y_mm_to_step(Ymm):
    Ystep=Ymm/mmPerRev_Y*StepsPerRev_Y
    return Ystep

def mmPerRev_Z(Xpos_mm):                            #Xpos_mm position in the centerlign of the fluid channel's referenciel
    return 2*np.pi*(Rcenter)#+Xpos_mm)


def Z_mm_to_step(Zmm,Xpos_mm):
    Zstep=Zmm/mmPerRev_Z(Xpos_mm)*StepsPerRev_Z
    return Zstep

#---------------------------------------------------
def X_step_to_mm(Xstep):
    Xmm=Xstep*mmPerRev_X/StepsPerRev_X
    return Xmm

def Y_step_to_mm(Ystep):
    Ymm=Ystep*mmPerRev_Y/StepsPerRev_Y
    return Ymm
 
def X_microstep_to_mm(Xstep):                #Arduino card send the data for X and Y in Microstep
    Xmm=Xstep*mmPerRev_X/(StepsPerRev_X*16)
    return Xmm

def Y_microstep_to_mm(Ystep):
    Ymm=Ystep*mmPerRev_Y/(StepsPerRev_Y*16)
    return Ymm

def Z_step_to_mm(Zstep,Xpos_mm):
    Zmm=Zstep*mmPerRev_Z(Xpos_mm)/StepsPerRev_Z
    return Zmm

#---------------------------------------------------
#Give the absolute position of the image in the referentiel of the centerline of the flow channel
def X_arduino_to_mm(Xarduino):
    Xmm=X_microstep_to_mm(Xarduino)
    Xpos_mm=Xmm+DeltaX_Arduino_mm-Rcenter
    return Xpos_mm

def Y_arduino_to_mm(Yarduino):
    Ymm=Y_microstep_to_mm(Yarduino)
    Ypos_mm=Ymm+DeltaY_Arduino_mm
    return Ypos_mm

def theta_arduino_to_rad(Zarduino):
    theta=Zarduino/StepsPerRev_Z*2*np.pi
    return theta

def rad_to_mm(ThetaWheel,Xobjet):
    return ThetaWheel/(2*np.pi)*(Rcenter+Xobjet)