#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import sys
import numpy, glumpy
from OpenGL.GL import *

window = glumpy.Window(512,512)
Z = numpy.random.random((32,32)).astype(numpy.float32)
_I = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Grey)

@window.timer(30.0)
def draw(dt):
    window.clear()
    _I.update()
    _I.blit(0,0,window.width,window.height)
    window.draw()

@window.event
def on_key_press(key, modifiers):
    if key == glumpy.key.ESCAPE:
        sys.exit()

I = glumpy.Proxy(_I,window)
window.mainloop(interactive=True, namespace=locals())
