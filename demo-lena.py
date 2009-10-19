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
from PIL import Image
import numpy
import pyglet
import glumpy

window = pyglet.window.Window(512,512)
Z = numpy.asarray(Image.open('lena.png'))
I = glumpy.Image(Z, interpolation='bicubic')

@window.event
def on_draw():
    window.clear()
    I.blit(0, 0, window.width, window.height)

pyglet.app.run()
