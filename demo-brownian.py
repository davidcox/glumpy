#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy, glumpy

n = 256
Z = numpy.random.randint(-1,2,(n,n)).astype(numpy.float32)
N = numpy.zeros(Z.shape).astype(numpy.float32)
P = numpy.zeros((n,), dtype=[('x',int),('y',int), ('c',float)])
P['x'] = numpy.random.randint(0,n,P.shape)
P['y'] = numpy.random.randint(0,n,P.shape)
P['c'] = numpy.random.random(P.shape)*2-1

window = glumpy.Window(512, 512)
I = glumpy.Image(Z, interpolation='bicubic', cmap=glumpy.colormap.Hot, vmin=-1, vmax=1)


@window.event
def on_draw():
    window.clear()
    I.blit(0,0,window.width,window.height)

@window.event
def on_idle(dt):
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
    window.draw()

window.mainloop()
