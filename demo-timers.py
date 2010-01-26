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

@window.timer(5.0)
def timer_1(dt):
    print 'tick 1'
    window.clear()
    window.draw()

@window.timer(2.0)
def timer_2(dt):
    print 'tick 2'
    window.clear()
    window.draw()

window.mainloop()

