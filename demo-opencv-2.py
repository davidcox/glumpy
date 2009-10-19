#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# glumpy - Fast OpenGL numpy visualization
# Copyright (c) 2009 - Nicolas P. Rougier
#
# This file is part of glumpy.
#
# glumpy is free  software: you can redistribute it and/or  modify it under the
# terms of  the GNU General  Public License as  published by the  Free Software
# Foundation, either  version 3 of the  License, or (at your  option) any later
# version.
#
# glumpy is  distributed in the  hope that it  will be useful, but  WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy  of the GNU General Public License along with
# glumpy. If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
import numpy as np
import pyglet
pyglet.options['debug_gl'] = False
import glumpy
from opencv import cv, adaptors, highgui


def cartesian(rho, theta):
    ''' Polar to cartesian coordinates. '''
    x = rho*np.cos(theta)
    y = rho*np.sin(theta)
    return x,y

def logpolar(rho, theta):
    ''' Polar to logpolar coordinates. '''
    A = 3.0  # Shift in the SC mapping function in deg 
    Bx = 1.4 # Collicular magnification along u axe in mm/rad 
    By = 1.8 # Collicular magnification along v axe in mm/rad 
    xmin, xmax = 0.0, 4.80743279742
    ymin, ymax = -2.76745559565, 2.76745559565
    rho = rho*90.0
    x = Bx*np.log(np.sqrt(rho*rho+2*A*rho*np.cos(theta)+A*A)/A)
    y = By*np.arctan(rho*np.sin(theta)/(rho*np.cos(theta)+A))
    x = (x-xmin)/(xmax-xmin)
    y = (y-ymin)/(ymax-ymin)
    return x,y


def retinotopy(Rs,Ps):
    ''' '''
    s = 4
    rho = ((np.logspace(start=0, stop=1, num=s*Rs[1],base=10)-1)/9.)
    theta = np.linspace(start=-np.pi/2,stop=np.pi/2, num=s*Rs[0])
    rho = rho.reshape((s*Rs[1],1))
    rho = np.repeat(rho,s*Rs[0], axis=1)
    theta = theta.reshape((1,s*Rs[0]))
    theta = np.repeat(theta,s*Rs[1], axis=0)
    y,x = cartesian(rho,theta)
    a,b = x.min(), x.max()
    x = (x-a)/(b-a)
    a,b = y.min(), y.max()
    y = (y-a)/(b-a)

    Px = np.ones(Ps, dtype=int)*0
    Py = np.ones(Ps, dtype=int)*0

    xi = (x*(Rs[0]-1)).astype(int)
    yi = ((0.5+0.5*y)*(Rs[1]-1)).astype(int)
    yc,xc = logpolar(rho,theta)
    a,b = xc.min(), xc.max()
    xc = (xc-a)/(b-a)
    a,b = yc.min(), yc.max()
    yc = (yc-a)/(b-a)
    xc = (xc*(Ps[0]-1)).astype(int)
    yc = ((.5+yc*0.5)*(Ps[1]-1)).astype(int)
    Px[xc,yc] = xi
    Py[xc,yc] = yi

    xi = (x*(Rs[0]-1)).astype(int)
    yi = ((0.5-0.5*y)*(Rs[1]-1)).astype(int)
    yc,xc = logpolar(rho,theta)
    a,b = xc.min(), xc.max()
    xc = (xc-a)/(b-a)
    a,b = yc.min(), yc.max()
    yc = (yc-a)/(b-a)
    xc = (xc*(Ps[0]-1)).astype(int)
    yc = (((1-yc)*0.5)*(Ps[1]-1)).astype(int)
    Px[xc,yc] = xi
    Py[xc,yc] = yi

    return Px, Py

device = 0
capture = highgui.cvCreateCameraCapture (device)
if not capture:
    print "Error opening capture device"
    sys.exit (1)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 512)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FRAME_WIDTH, 512)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FPS, 3)

# Capture the first frame to get some propertie on it
frame_rgb = highgui.cvQueryFrame (capture)
size = cv.cvGetSize(frame_rgb)
print 'Video capture device %d at %dx%d' % (device,size.width,size.height)

# Create a grey frame and a grey downscale one
frame_grey = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
w,h = size.width, size.height
size = cv.cvSize(w//2,h//2)
frame = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)

Z = adaptors.Ipl2NumPy(frame)
Zi = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Grey)

V = np.zeros((h//4,w//4),dtype=np.float32)
Px,Py = retinotopy(Z.shape,V.shape)
Vi = glumpy.Image(V, interpolation='nearest', cmap=glumpy.colormap.Grey)

#window = pyglet.window.Window(Z.shape[1], Z.shape[0], vsync=0)
window = pyglet.window.Window(V.shape[1]*2, V.shape[0]*2, vsync=0)
fps_display = pyglet.clock.ClockDisplay()


@window.event
def on_draw():
    window.clear()
    Vi.blit(0,0,window.width,window.height)
    fps_display.draw()

def update(dt):
    frame_rgb = highgui.cvQueryFrame (capture)
    cv.cvCvtColor(frame_rgb, frame_grey, cv.CV_RGB2GRAY)
    cv.cvResize(frame_grey, frame, cv.CV_INTER_LINEAR)
    Z[...] = adaptors.Ipl2NumPy(frame)

    V[...] = Z[Px,Py]
    Vi.update()

    #Zi.update()

pyglet.clock.schedule(update)
pyglet.app.run()

