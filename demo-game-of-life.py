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

n = 512
Z = numpy.random.randint(0,2,(n,n)).astype(numpy.uint8)
window = pyglet.window.Window(512, 512, vsync=0)
viewport = [0,0,1]
Zi = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Grey,
                  vmin=1, vmax=0)
fps_display = pyglet.clock.ClockDisplay()
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

@window.event
def on_mouse_motion(x, y, dx, dy):
    zoom = viewport[2]
    x = x/float(window.width)
    y = y/float(window.height)
    x = min(max(x,0),1)
    y = min(max(y,0),1)
    viewport[0] = x*window.width*(1-zoom)
    viewport[1] = y*window.height*(1-zoom)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    zoom = viewport[2]
    if scroll_y > 0:
        zoom *= 1.25
    elif scroll_y < 0:
        zoom /= 1.25
    viewport[2] = min(max(zoom,1),20)
    on_mouse_motion(x,y,0,0)

@window.event
def on_draw():
    window.clear()
    x,y,s = viewport
    Zi.blit(x, y, s*window.width, s*window.height)
    fps_display.draw()

def update(dt):
    # Code by Tom Wright
    # http://tat.wright.name/game-of-life/game-of-life.py
    N = numpy.zeros(Z.shape)
    N[1:, 1:] += Z[:-1, :-1]
    N[1:, :-1] += Z[:-1, 1:]
    N[:-1, 1:] += Z[1:, :-1]
    N[:-1, :-1] += Z[1:, 1:]
    N[:-1, :] += Z[1:, :]
    N[1:, :] += Z[:-1, :]
    N[:, :-1] += Z[:, 1:]
    N[:, 1:] += Z[:, :-1]
    Z[...] = ((Z == 1) & (N < 4) & (N > 1)) | ((Z == 0) & (N == 3))
    Zi.update()

pyglet.clock.schedule(update)
pyglet.app.run()
