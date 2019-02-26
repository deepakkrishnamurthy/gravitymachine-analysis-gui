# -*- coding: utf-8 -*-
"""
Spyder Editor
Script to obtain Z-stacks
Outline:
    1. User prompt for the liquid lens offset
    2. Send liquid lens command to the Arduino
    3. User prompt to obtain Z-stack
    4. Send commands to Arduino to obtain the Z-stack
    5. Return to 1.

This is a temporary script file.
"""
import sys
import os

import cv2
import numpy as np

import CSV_Tool
import Arduino_Tool

from camera.VideoStream import VideoStream as VideoStream

import time
import imutils



# Main menu
def main_menu():
	os.system('clear')
	
	print("Welcome to a Gravity Machine Experiment Session,\n")
	print("Please choose the experiment to run:")
	print("1. Obtain Z-stacks (Liquid Lens Calibration)")
	# print("3. Track Objects (Abiotic)")
	print("\n 0. Quit \n")
	choice = raw_input(" >>  ")
	exec_menu(choice)
 
	return

# Execute menu
def exec_menu(choice):
	os.system('clear')
	ch = choice.lower()
	if ch == '':
		menu_actions['main_menu']()
	else:
		try:
			menu_actions[ch]()
		except KeyError:
			print("Invalid selection, please try again.\n")
			menu_actions['main_menu']()
	return

# Menu 1
def Z_Stack():
	
    # Start the Video Stream
    camResolution=(640,480)
    camFPS=30
    CAMERA=2
    
    
    #thread to et the image
    VideoSrc = VideoStream(camera_port,self.CAMERA,resolution = self.camResolution,framerate = self.camFPS) # Grab a reference to a VideoStream object (cross-platform functionality)
    VideoSrc.start()
    time.sleep(2.0)

    while True:
        
        image = VideoSrc.read()
        
        cv2.imshow('frame',image)
        
    

	print("9. Back To Main Menu")
	print("0. Quit \n")
	choice = raw_input(" >>  ")
	exec_menu(choice)
	return
 
 
# # Menu 2
# def menu2():
#     print("Hello Menu 2 !\n")
#     print("9. Back")
#     print("0. Quit")
#     choice = raw_input(" >>  ")
#     exec_menu(choice)
#     return
 
# Back to main menu
def back():
	menu_actions['main_menu']()
 
# Exit program
def exit():
	sys.exit()

	# =======================
#    MENUS DEFINITIONS
# =======================
 
# Menu definition
menu_actions = {
	'main_menu': main_menu,
	'1': Z_Stack,
	'9': back,
	'0': exit,
}

# =======================
#      MAIN PROGRAM
# =======================
 
# Main Program
if __name__ == "__main__":
	# Launch main menu
	main_menu()







