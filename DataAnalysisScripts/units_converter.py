#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 19:18:21 2018

@author: deepak
"""

#============================================================================== 
def mmPerPixel(resolution_width):
    return 1./628/(resolution_width/1440)   #for a 1440x1080 image
def pixelPermm(resolution_width):
    return 628*resolution_width/1440
#==============================================================================