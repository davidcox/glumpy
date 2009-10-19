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

n = 256
Z = numpy.random.randint(-1,2,(n,n)).astype(numpy.float32)
N = numpy.zeros(Z.shape).astype(numpy.float32)
P = numpy.zeros((n,), dtype=[('x',int),('y',int), ('c',float)])
P['x'] = numpy.random.randint(0,n,P.shape)
P['y'] = numpy.random.randint(0,n,P.shape)
P['c'] = numpy.random.random(P.shape)*2-1

window = pyglet.window.Window(512, 512, vsync=0)
I = glumpy.Image(Z, interpolation='bicubic', cmap=glumpy.colormap.Hot, vmin=-1, vmax=1)


@window.event
def on_draw():
    window.clear()
    I.blit(0,0,window.width,window.height)

def update(dt):
    global N,P,Z
    P['x'] += (numpy.random.randint(0,3,P.size)-1)
    P['y'] += (numpy.random.randint(0,3,P.size)-1)
    P['x'] = numpy.minimum(numpy.maximum(P['x'],0), Z.shape[0]-1)
    P['y'] = numpy.minimum(numpy.maximum(P['y'],0), Z.shape[0]-1)
    Z[P['x'], P['y']] = P['c']
    N[...] = 0
    N[1:,1:] += Z[:-1, :-1]
    N[1:,:-1] += Z[:-1, 1:]
    N[:-1,1:] += Z[1:, :-1]
    N[:-1,:-1] += Z[1:, 1:]
    N[:-1,:] += Z[1:, :]
    N[1:,:] += Z[:-1, :]
    N[:,:-1] += Z[:, 1:]
    N[:,1:] += Z[:, :-1]
    N /= 8.0
    Z[...] = 0.5*Z+ 0.5*N
    I.update()

pyglet.clock.schedule(update)
pyglet.app.run()
