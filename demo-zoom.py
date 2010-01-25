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
import numpy, glumpy

window = glumpy.Window(512, 512)
Z = numpy.random.random((128,128)).astype(numpy.float32)
I = glumpy.Image(Z, interpolation='bicubic', cmap=glumpy.colormap.Grey)
viewport = [0,0,1]

@window.event
def on_mouse_motion(x, y, dx, dy):
    zoom = viewport[2]
    x = x/float(window.width)
    y = y/float(window.height)
    x = min(max(x,0),1)
    y = min(max(y,0),1)
    viewport[0] = x*window.width*(1-zoom)
    viewport[1] = y*window.height*(1-zoom)
    window.draw()

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
    I.blit(x, y, s*window.width, s*window.height)

window.mainloop()

