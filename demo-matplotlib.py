#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
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

