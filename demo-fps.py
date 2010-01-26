#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy, glumpy

window = glumpy.Window(512,512)
Z = numpy.random.random((32,32)).astype(numpy.float32)
I = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Grey)
t0, t, frames = 0, 0, 0

@window.timer(30.0)
def timer(dt):
    global t, t0, frames

    t += dt
    frames = frames + 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames,t0 = 0, t
    window.clear()
    window.draw()

window.mainloop()

