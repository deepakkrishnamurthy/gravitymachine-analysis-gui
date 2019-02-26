#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 23:47:16 2018

@author: deepak
"""

def plotPIVdata(image,x,y,u,v, U, orgContour,figname=1,saveFileName='PIVdata.tif'):
    # Plots the PIV vector field overlaid on the raw image
    x_centroid = findCentroid(orgContour)
    #cv2.drawContours(image, [orgContour] ,-1, color=[0,255,0], thickness = 1)
#    x_fine,y_fine = np.meshgrid(np.linspace(np.min(x),np.max(x),2*np.shape(x)[1]), np.linspace(np.min(y),np.max(y),2*np.shape(y)[0]))
    
   
    
 
#    plt.scatter(x,y,color='b')
#    plt.scatter(x_fine,y_fine,marker='.',color='r')
#    plt.show()
    
   
    
    
#    U_fine_func = scipy.interpolate.Rbf(x,y,U)
#    U_fine = U_fine_func(x_fine,y_fine)
       
#    U_min = 0
#    U_max = 1.2
    
    fig = plt.figure(1)
    plt.clf()
     
    ax1 = plt.imshow(image,cmap=plt.cm.gray,alpha=1.0)
    ax2 = plt.contourf(x, y, U, cmap = cmocean.cm.amp, alpha=1.0,linewidth=0,linestyle=None)
    
    #ax2 = plt.pcolor(x,y,U,cmap = cmocean.cm.amp)
    #ax1 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.solar)
    #ax3 = plt.streamplot(x,y,u,v)
    
#    ax3 = plt.quiver(x,y,u,v,U,cmap = cmocean.cm.amp)
    ax4 = plt.streamplot(x,y,u,-v,color='blue',linewidth = 1, density = 1.5, arrowsize=0.1)

    ax3 = plt.quiver(x[::2],y[::2],u[::2],v[::2],color='k')
    plt.scatter(x_centroid[0], x_centroid[1])
    cbar = plt.colorbar(ax2)
    cbar.ax.set_ylabel('Flow velocity magnitude (mm/s)')


    plt.xlabel('X')
    plt.ylabel('Z')
    #    cbar.set_label('Speed')
    plt.axis('image')
    plt.pause(0.001)
#    
#    plt.savefig(saveFileName,dpi=300)
#    plt.show(block=False)
    plt.show()