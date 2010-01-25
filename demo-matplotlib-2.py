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


n = 120
t0, frames, t = 0,0,0

X = numpy.empty((n,n), dtype=numpy.float32)
X.flat = numpy.arange(n)*2*numpy.pi/n
Y = numpy.empty((n,n), dtype=numpy.float32)
Y.flat = numpy.arange(n)*2*numpy.pi/n
Y = numpy.transpose(Y)
Z = numpy.sin(X) + numpy.cos(Y)
fig = plt.figure(figsize=(7,7))
plt.suptitle('''Generated using matplotlib,\n'''
             '''Displayed using glumpy !''', fontsize=16)
ax = plt.subplot(111)
ax = imshow(Z, origin='upper', interpolation='nearest', cmap=plt.cm.hot)
plt.grid()
show()

window = glumpy.active_window()

@window.event
def on_idle(dt):
    global X, Y, t, t0, frames

    t += dt
    frames = frames + 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames,t0 = 0, t

    X += numpy.pi/15
    Y += numpy.pi/20
    for image, axis, alpha in items:
        image.data[...] = numpy.sin(X) + numpy.cos(Y)
        image.update()
    window.draw()

window.mainloop()




