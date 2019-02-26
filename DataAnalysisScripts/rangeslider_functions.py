#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 19:21:15 2018

@author: deepak
"""
import cv2
def callback(value):
	pass
# Track bars for selecting the image
def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)





def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

def getColorThreshold(imageName, filterName = 'HSV'):
   
    
    range_filter = filterName.upper()

   
    image = cv2.imread(imageName)

    if range_filter == 'RGB':
        frame_to_thresh = image.copy()
    else:
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    

    setup_trackbars(range_filter)

    while True:
        

        if range_filter == 'RGB':
            frame_to_thresh = image.copy()
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)

        key = cv2.waitKey(100) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)
            
    return v1_min, v2_min, v3_min, v1_max, v2_max, v3_max