#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
# Adapted from a post on comp.lang.python by Alberto Santini 
# Topic: Real-Time Fluid Dynamics for Games...
# Date: 02/20/05
# 
# Mouse click to add smoke
# Mouse move to add some turbulences
# -----------------------------------------------------------------------------
import sys
import numpy, glumpy
from solver import vel_step, dens_step

N = 50
size = N+2
dt = 0.1
diff = 0.0
visc = 0.0
force = 1
source = 25.0
u     = numpy.zeros((size,size), dtype=numpy.float32)
u_    = numpy.zeros((size,size), dtype=numpy.float32)
v     = numpy.zeros((size,size), dtype=numpy.float32)
v_    = numpy.zeros((size,size), dtype=numpy.float32)
dens  = numpy.zeros((size,size), dtype=numpy.float32)
dens_ = numpy.zeros((size,size), dtype=numpy.float32)
Z = numpy.zeros((N,N),dtype=numpy.float32)

cmap = glumpy.colormap.Colormap("BlueGrey",
                                (0., (0.,0.,0.)), (1., (0.75,0.75,1.00)))
I = glumpy.Image(Z, interpolation='bicubic', cmap=cmap, vmin=0, vmax=5)
t, t0, frames = 0,0,0

window = glumpy.Window(800,800)
window.last_drag = None

@window.event
def on_mouse_drag(x, y, dx, dy, button):
    window.last_drag = x,y,dx,dy,button

@window.event
def on_mouse_motion(x, y, dx, dy):
    window.last_drag = x,y,dx,dy,0

@window.event
def on_key_press(key, modifiers):
    global dens, dens_, u, u_, v, v_
    if key == glumpy.key.ESCAPE:
        sys.exit()
    elif key == glumpy.key.SPACE:
        dens[...] = dens_[...] = 0.0
        u[...] = u_[...] = 0.0
        v[...] = v_[...] = 0.0

@window.event
def on_idle(*args):
    global dens, dens_, u, u_, v, v_, N, visc, dt, diff
    window.clear()
    dens_[...] = u_[...] = v_[...] = 0.0
    if window.last_drag:
        x,y,dx,dy,button = window.last_drag
        j = min(max(int((N+2)*x/float(window.width)),0),N+1)
        i = min(max(int((N+2)*(window.height-y)/float(window.height)),0),N+1)
        if not button:
            u_[i,j] = -force * dy
            v_[i,j] = force * dx
        else:
            dens_[i,j] = source
    window.last_drag = None
    vel_step(N, u, v, u_, v_, visc, dt)
    dens_step(N, dens, dens_, u, v, diff, dt)
    Z[...] = dens[0:-2,0:-2]
    I.update()
    I.blit(0,0,window.width,window.height)
    window.draw()

    global t, t0, frames
    t += args[0]
    frames = frames + 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames,t0 = 0, t

window.mainloop()


