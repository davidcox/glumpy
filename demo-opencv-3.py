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
import pyglet.gl as gl
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
frame_rgb = highgui.cvQueryFrame (capture)
size = cv.cvGetSize(frame_rgb)
print 'Video capture device %d at %dx%d' % (device,size.width,size.height)
w,h = size.width, size.height
size = cv.cvSize(w,h)
frame = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
Z = adaptors.Ipl2NumPy(frame)
Zi = glumpy.Image(Z)

cube = pyglet.graphics.Batch()
dx0,dx1 = 0,1
dy0,dy1 = 0,1
if w > h:
    dx0 = (w/float(h)-1)/2
    dx1 = 1-(w/float(h)-1)/2
elif h < w:
    dy0 = (h/float(w)-1)/2
    dy1 = 1-(h/float(w)-1)/2
cube.add(24, gl.GL_QUADS, None,
         ('n3f', ( 0, 0, 1)*4+( 0, 0,-1)*4+( 0, 1, 0)*4+
           ( 0,-1, 0)*4+( 1, 0, 0)*4+(-1, 0, 0)*4),
         ('v3f', (-.5,-.5, .5)+( .5,-.5, .5)+( .5, .5, .5)+(-.5, .5, .5)+
          (-.5,-.5,-.5)+(-.5, .5,-.5)+( .5, .5,-.5)+( .5,-.5,-.5)+
          (-.5, .5,-.5)+(-.5, .5, .5)+( .5, .5, .5)+( .5, .5,-.5)+
          (-.5,-.5,-.5)+( .5,-.5,-.5)+( .5,-.5, .5)+(-.5,-.5, .5)+
          ( .5,-.5,-.5)+( .5, .5,-.5)+( .5, .5, .5)+( .5,-.5, .5)+
          (-.5,-.5,-.5)+(-.5,-.5, .5)+(-.5, .5, .5)+(-.5, .5,-.5)),
         ('t2f', (dx0,dy0)+(dx1,dy0)+(dx1,dy1)+(dx0,dy1)+
                 (dx1,dy0)+(dx1,dy1)+(dx0,dy1)+(dx0,dy0)+
                 (dx0,dy1)+(dx0,dy0)+(dx1,dy0)+(dx1,dy1)+
                 (dx1,dy1)+(dx0,dy1)+(dx0,dy0)+(dx1,dy0)+
                 (dx1,dy0)+(dx1,dy1)+(dx0,dy1)+(dx0,dy0)+
                 (dx0,dy0)+(dx1,dy0)+(dx1,dy1)+(dx0,dy1)))
window = pyglet.window.Window(width=800,height=600, vsync=0)
trackball = glumpy.Trackball(60,30,1.1)

@window.event
def on_draw():
    gl.glClearColor(0,0,0,1)
    window.clear()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    angle = 15+105*(trackball.zoom-1)
    gl.gluPerspective(angle, window.width / float(window.height), .1, 1000)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glTranslatef(0, 0, -5)
    gl.glMultMatrixf(trackball.matrix)
    gl.glEnable(gl.GL_DEPTH_TEST)

    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(Zi.texture.target, Zi.texture.id)
    gl.glColor4f(1,1,1,1)
    gl.glEnable (gl.GL_POLYGON_OFFSET_FILL)
    gl.glPolygonOffset (1.0,1.0)
    gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    cube.draw()

    gl.glDisable(gl.GL_TEXTURE_2D)
    gl.glDisable (gl.GL_POLYGON_OFFSET_FILL)
    gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_LINE_SMOOTH)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glColor4f(0,0,0,1)
    cube.draw()

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()


@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    x  = (x*2.0 - window.width)/float(window.width)
    dx = 2*dx/float(window.width)
    y  = (y*2.0 - window.height)/float(window.height)
    dy = 2*dy/float(window.height)
    trackball.drag_to(x,y,dx,dy)
    return True

@window.event
def on_mouse_scroll(x, y, dx, dy):
    trackball.zoom_to(x,y,dx,dy)
    return True

def update(dt):
     frame_rgb = highgui.cvQueryFrame (capture)
     cv.cvResize(frame_rgb, frame, cv.CV_INTER_LINEAR)
     Z[...] = adaptors.Ipl2NumPy(frame)
     Zi.update()
     return

pyglet.clock.schedule(update)
pyglet.app.run()

