#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 15:33:28 2019

@author: deepak
"""

from flowtrace import flowtrace
import os

videoFolder = '/Volumes/My Book/2019 Monterey Trip/Tunicates/LarvaeReleaseImaging/2019_08_10/images'
saveFolder = os.path.join(videoFolder, 'FlowTrace/')
flowtrace(videoFolder,30,saveFolder)