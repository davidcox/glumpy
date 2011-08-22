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
This script demonstrates event combined event handling.
'''
import os
import sys
import PIL
import numpy as np
from glumpy import Figure, Image, Label

if not os.path.exists('./Arial.ttf'):
    print '''This demo requires the font 'Arial.ttf' to be present in the current directory'''
    sys.exit()

fig  = Figure(size=(600,800))
fig1 = fig.add_figure(cols=3,rows=4, position=[0,1], size=[3,3])
fig2 = fig.add_figure(cols=3,rows=4, position=[0,0], size=[1,1])
fig3 = fig.add_figure(cols=3,rows=4, position=[1,0], size=[1,1])
fig4 = fig.add_figure(cols=3,rows=4, position=[2,0], size=[1,1])

label1 = Label("Lena",     x=fig1.X+5, y=fig1.Y+5, size=24, filename='./Arial.ttf')
label2 = Label("Nearest",  x=fig2.X+5, y=fig2.Y+5, size=24, filename='./Arial.ttf')
label3 = Label("Bilinear", x=fig3.X+5, y=fig3.Y+5, size=24, filename='./Arial.ttf')
label4 = Label("Bicubic",  x=fig4.X+5, y=fig4.Y+5, size=24, filename='./Arial.ttf')

n = 32
Z = np.asarray(PIL.Image.open('lena.png'),dtype=np.uint8)
I1 = Image(Z, interpolation='bicubic')
I2 = Image(np.ones((n,n,3), dtype=np.uint8), interpolation='nearest')
I3 = Image(np.ones((n,n,3), dtype=np.uint8), interpolation='bilinear')
I4 = Image(np.ones((n,n,3), dtype=np.uint8), interpolation='bicubic')

@fig.event
def on_draw():
    fig.clear()
    for I,F,L in zip([I1,I2,I3,I4],
                     [fig1,fig2,fig3,fig4],
                     [label1,label2,label3,label4]):
        I.blit(*F.viewport)
        L.draw()

@fig1.event
def on_mouse_motion(x,y,dx,dy):
    x = (      x/fig1.width ) * I1.shape[1]-n//2
    y = (1.0 - y/fig1.height) * I1.shape[0]-n//2
    x = int(min(max(x,0), I1.shape[1]-n))
    y = int(min(max(y,0), I1.shape[0]-n))
    for I in [I2,I3,I4]:
        I.data[...] = I1.data[y:y+n, x:x+n]
        I.update()
    fig.draw()
    
fig.show()

