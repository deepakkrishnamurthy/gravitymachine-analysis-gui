# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 16:48:01 2018

@author: deepak90
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate as interpolate
import scipy.signal as signal
import scipy.ndimage as ndimage
import matplotlib.patches as patches
from numpy.polynomial import polynomial as Poly
import cmocean
import math



cmap = plt.get_cmap('rainbow')

nRows = 100
nColumns = 100

ColorMatrix = np.zeros((nRows,nColumns))

minValue = 1
maxValue_deep = 0.2
maxValue = -1


for ii in range(nRows):
    
    maxValue_curr = maxValue - (maxValue - maxValue_deep)*ii/nRows
    ColorMatrix[ii,:] = np.linspace(minValue, maxValue_curr,nColumns)
    
    
    

plt.figure()
ax1 = plt.imshow(ColorMatrix, cmap = plt.get_cmap('gist_rainbow'))
plt.colorbar(ax1)
#plt.axis('image')
ax = plt.gca()
#ax.set_yscale('log')
#ax.set_xscale('log')
ax.set_yticklabels([])
ax.set_xticklabels([])
plt.savefig('DepthSpectrum.svg',dpi=150)
plt.show()