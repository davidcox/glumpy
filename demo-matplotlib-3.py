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
from glumpy.pylab import *
import matplotlib.pyplot as plt

def func3(x,y):
    return (1- x/2 + x**5 + y**3)*numpy.exp(-x**2-y**2)
dx, dy = 0.05, 0.05
x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
X,Y = numpy.meshgrid(x, y)

xmin, xmax = numpy.amin(x), numpy.amax(x)
ymin, ymax = numpy.amin(x), numpy.amax(x)
extent = xmin, xmax, ymin, ymax
fig = plt.figure()
Z1 = numpy.array(([0,1]*4 + [1,0]*4)*4, dtype=numpy.float32)
Z1.shape = 8,8  # chessboard
im1 = imshow(Z1, cmap=plt.cm.gray, interpolation='nearest', extent=extent)
Z2 = func3(X, Y)
im2 = imshow(Z2, cmap=plt.cm.jet, alpha=.9,
             interpolation='bilinear', extent=extent)

show()
window = glumpy.active_window()
window.mainloop()
