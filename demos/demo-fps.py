#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import glumpy
import OpenGL.GL as gl
import OpenGL.GLUT as glut

window = glumpy.Window(512,512)
t0, t, frames = 0, 0, 0


@window.event
def on_idle(dt):
    global text, t, t0, frames
    t += dt
    frames += 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames, t0 = 0, t
    window.clear()

print 'Computing FPS...'
window.mainloop()

