#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 23:09:36 2018

@author: deepak
"""

import os

import scipy as sp
import scipy.misc

import imreg_dft as ird


basedir = os.path.join('..', 'examples')
# the TEMPLATE
im0 = sp.misc.imread(os.path.join(basedir, "sample1.png"), True)
# the image to be transformed
im1 = sp.misc.imread(os.path.join(basedir, "sample2.png"), True)
result = ird.translation(im0, im1)
tvec = result["tvec"].round(4)
# the Transformed IMaGe.
timg = ird.transform_img(im1, tvec=tvec)

# Maybe we don't want to show plots all the time
if os.environ.get("IMSHOW", "yes") == "yes":
    import matplotlib.pyplot as plt
    ird.imshow(im0, im1, timg)
    plt.show()

print("Translation is {}, success rate {:.4g}"
      .format(tuple(tvec), result["success"]))