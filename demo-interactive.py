#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# glumpy - Fast OpenGL numpy visualization
# Copyright (c) 2009, 2010 - Nicolas P. Rougier
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
