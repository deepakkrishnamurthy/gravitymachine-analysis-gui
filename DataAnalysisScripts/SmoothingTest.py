#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 16:36:02 2018

@author: deepak
"""

import numpy as np
from smoothn import smoothn 
import matplotlib.pyplot as plt


X = np.linspace(0,10,100)
Y = np.sin(X) + np.random.rand(len(X),)

f = plt.figure(1)
plt.plot(X,Y,color='r')
plt.plot(X,smoothn(Y,2.0),color='b')
