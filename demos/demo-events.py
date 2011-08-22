#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
'''
This example shows figure available events.
'''

import OpenGL.GL as gl
from glumpy import figure

fig = figure(size=(400,400))

@fig.event
def on_init():
    print 'Inititalization'

@fig.event
def on_draw():
    print 'Drawing requested'

@fig.event
def on_resize(width,height):
    print 'Figure resized (width=%.1f, height=%.1f)'% (width,height)

@fig.timer(1.0)
def timer(elapsed):
    print 'Timed event (%.2f second(s) elapsed)' % elapsed

# @fig.event
# def on_idle(dt):
#     print 'Idle event'

@fig.event
def on_key_press(symbol, modifiers):
    print 'Key pressed (symbol=%s, modifiers=%s)'% (symbol,modifiers)

@fig.event
def on_key_release(symbol, modifiers):
    print 'Key released (symbol=%s, modifiers=%s)'% (symbol,modifiers)

@fig.event
def on_mouse_press(x, y, button):
    print 'Mouse button pressed (x=%.1f, y=%.1f, button=%d)' % (x,y,button)

@fig.event
def on_mouse_release(x, y, button):
    print 'Mouse button released (x=%.1f, y=%.1f, button=%d)' % (x,y,button)

@fig.event
def on_mouse_motion(x, y, dx, dy):
    print 'Mouse motion (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f)' % (x,y,dx,dy)

@fig.event
def on_mouse_drag(x, y, dx, dy, button):
    print 'Mouse drag (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f, button=%d)' % (x,y,dx,dy,button)


fig.show()
