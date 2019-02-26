#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 19:37:41 2019

@author: deepak
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots()

x = np.arange(0, 2*np.pi, 0.01)
#line, = ax.plot(x, np.sin(x))

scat = ax.scatter(x,np.sin(x),20, color='k', animated = True)


def init():  # only required for blitting to give a clean slate.
#    line.set_ydata([np.nan] * len(x))
    data = np.hstack(([np.nan],[np.nan]))
    scat.set_offsets(data)
    return scat


def animate(i):
#    line.set_ydata(np.sin(x + i / 100))  # update the data.
    data = np.hstack(([x+i/100], [np.sin(x + i/100)]))
    scat.set_offsets(data)
    return scat


ani = animation.FuncAnimation(fig, animate, init_func=init, interval=2, blit=True, save_count=50)

# To save the animation, use e.g.
#
# ani.save("movie.mp4")
#
# or
#
# from matplotlib.animation import FFMpegWriter
# writer = FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
# ani.save("movie.mp4", writer=writer)

plt.show()