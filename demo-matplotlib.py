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
import matplotlib.pyplot as plt
from glumpy.pylab import *

def func3(x,y):
    return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
dx, dy = .05, .05
x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
Z = func3(*numpy.meshgrid(x, y))

fig = plt.figure(figsize=(7,7), facecolor='.9')
plt.suptitle('''Generated using matplotlib,\n'''
             '''Displayed using glumpy !''', fontsize=16)
ax = plt.subplot(111)
cmap = plt.cm.hot
cmap.set_under((0,0,1))
cmap.set_over((0,1,0))
ax = imshow(Z, origin='lower', interpolation='bicubic', cmap=cmap,
            extent=[0,Z.shape[0],0,Z.shape[1]], vmin=-0.5, vmax=0.5)
plt.grid()

show()
window = glumpy.active_window()
window.mainloop()

