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
import glumpy

def func3(x,y):
    return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
dx, dy = .01, .01
x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
X,Y = numpy.meshgrid(x, y)
Z = func3(X,Y)
Zc = Z.copy()

window = pyglet.window.Window(512, 512, vsync=0)
I = glumpy.Image(Zc, interpolation='bicubic', cmap=glumpy.colormap.IceAndFire, vmin=-0.5, vmax=1.0)
t = 0
fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
    I.blit(0,0,window.width,window.height)
    fps_display.draw()

def update(dt):
    global t
    t = t + dt*.5
    Zc[...] = Z*numpy.cos(t)
    I.update()

pyglet.clock.schedule(update)
pyglet.app.run()
