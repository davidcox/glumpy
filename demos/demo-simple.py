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
I = glumpy.Image(Z)

@window.event
def on_draw():
    I.blit(0,0,window.width,window.height)
window.mainloop()
