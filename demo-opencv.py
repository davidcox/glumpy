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
import numpy
import pyglet
pyglet.options['debug_gl'] = False
import glumpy
from opencv import cv, adaptors, highgui

device = 0
capture = highgui.cvCreateCameraCapture (device)
if not capture:
    print "Error opening capture device"
    sys.exit (1)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 640)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FRAME_WIDTH, 480)
highgui.cvSetCaptureProperty (capture, highgui.CV_CAP_PROP_FPS, 3)

# Capture the first frame to get some propertie on it
frame_rgb = highgui.cvQueryFrame (capture)
size = cv.cvGetSize(frame_rgb)
print 'Video capture device %d at %dx%d' % (device,size.width,size.height)

# Create a grey frame and a grey downscale one
frame_grey = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
w,h = size.width, size.height
size = cv.cvSize(w,h)
frame = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)

Z = adaptors.Ipl2NumPy(frame)
window = pyglet.window.Window(Z.shape[1], Z.shape[0], vsync=0)
Zi = glumpy.Image(Z, interpolation='bicubic', cmap=glumpy.colormap.Grey)
fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
    Zi.blit(0,0,window.width,window.height)
    fps_display.draw()

def update(dt):
    frame_rgb = highgui.cvQueryFrame (capture)
    cv.cvCvtColor(frame_rgb, frame_grey, cv.CV_RGB2GRAY)
    cv.cvResize(frame_grey, frame, cv.CV_INTER_LINEAR)
    Z[...] = adaptors.Ipl2NumPy(frame)
    Zi.update()
    return

pyglet.clock.schedule(update)
pyglet.app.run()

