#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy, glumpy

def func3(x,y):
    return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
dx, dy = .01, .01
x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
X,Y = numpy.meshgrid(x, y)
Z = func3(X,Y)
Zc = Z.copy()
t0, frames, t = 0,0,0

window = glumpy.Window(512, 512)
I = glumpy.Image(Zc, interpolation='bicubic',
                 cmap=glumpy.colormap.IceAndFire, vmin=-0.5, vmax=1.0)

@window.event
def on_draw():
    window.clear()
    I.blit(0,0,512,512)

@window.event
def on_idle(dt):
    global t, t0, frames

    t += dt
    frames = frames + 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames,t0 = 0, t
    Zc[...] = Z*numpy.cos(t)
    I.update()
    window.draw()

window.mainloop()
