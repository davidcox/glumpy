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
import OpenGL.GL as gl

window = glumpy.Window(512, 512)
A = glumpy.Image(numpy.random.random((100,100)).astype(numpy.float32),
                 cmap=glumpy.colormap.Grey)
B = glumpy.Image(numpy.random.random((50,50)).astype(numpy.float32),
                 cmap=glumpy.colormap.Grey)
C = glumpy.Image(numpy.random.random((30,30)).astype(numpy.float32),
                 cmap=glumpy.colormap.Grey)

shape, items = glumpy.layout([ [(A,1.05), '-'],
                               [(C,5/3.), B  ] ], padding=5, border=5)

window.set_size(int(shape[0]*600), int(shape[1]*600))

@window.event
def on_draw():
    window.clear()
    gl.glColor4f(1,1,1,1)
    for item in items:
        Z,x,y,w,h = item
        x,y = x*600*shape[0],   y*600*shape[1]
        w,h = w*600*shape[0]-1, h*600*shape[1]+1
        Z.blit(x,y,w,h)

window.mainloop()

