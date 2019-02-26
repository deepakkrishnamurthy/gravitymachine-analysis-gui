#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 23:45:34 2018

@author: deepak
"""

def callback(value):
	pass
# Track bars for selecting the image
def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-c", "--picamera", type=int, default=-1,
    help="whether or not the Raspberry Pi camera should be used")
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter. RGB or HSV')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    args = vars(ap.parse_args())

    if not xor(bool(args['image']), bool(args['webcam'])):
        ap.error("Please specify only one image source")

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please speciy a correct filter.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

def getColorThreshold(image, filterName = 'HSV'):
   
    
    range_filter = filterName.upper()

   
    

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

def colorThreshold(image,thresh_low,thresh_high):
    
    thresh_low = np.array(thresh_low,dtype='uint8')
    thresh_high = np.array(thresh_high,dtype='uint8')
    
    print(thresh_low)
    print(thresh_high)
    
    im_th = cv2.inRange(image, thresh_low, thresh_high)
    
    kernel3 = np.ones((3,3),np.uint8)
    kernel5 = np.ones((5,5),np.uint8)
    kernel7 = np.ones((7,7),np.uint8)
    kernel15 = np.ones((15,15),np.uint8)
    
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel5)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel7)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_OPEN, kernel7)
    
    im_th = cv2.morphologyEx(im_th, cv2.MORPH_CLOSE, kernel15)

    
#    plt.matshow (im_th , cmap=cm.Greys_r )
#    plt.show()
    
    # Select the largest contour as the final mask
    cnts = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    print('No:of contours:{}'.format(len(cnts)))
    
   
    largestContour = max(cnts, key=cv2.contourArea)
    
    M = cv2.moments(largestContour)
    
    # Approximate the contour to 1% of its arcLength
    epsilon = 0.01*cv2.arcLength(largestContour,True)
    approxContour = cv2.approxPolyDP(largestContour,epsilon,True)
            
    ((x, y), radius) = cv2.minEnclosingCircle(largestContour)
    
    orgCentroid = np.array((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
    
    cv2.circle(im_th,(orgCentroid[0],orgCentroid[1]),int(4*radius),color=255,thickness=-1)
    
    cnts_circle = cv2.findContours(im_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]

    print('No:of contours in circle masked image:{}'.format(len(cnts_circle)))
    
    circleContour = max(cnts_circle, key=cv2.contourArea)
    
    
    
    return im_th, approxContour, circleContour, orgCentroid 
