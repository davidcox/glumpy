#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from PIL import Image
import numpy, glumpy

window = glumpy.Window(512,512)
Z = numpy.asarray(Image.open('lena.png'))
n = 12
L = glumpy.Image(Z, interpolation='bicubic')
N = glumpy.Image(numpy.ones((n,n,3), dtype=numpy.uint8),
                 interpolation='nearest')
BL = glumpy.Image(numpy.zeros((n,n,3), dtype=numpy.uint8),
                 interpolation='bilinear')
BC = glumpy.Image(numpy.zeros((n,n,3), dtype=numpy.uint8),
                 interpolation='bicubic')

z = 512/(3.0*n)
shape, items = glumpy.layout([ [L, '-', '-'],
                               [(N,z), (BL,z), (BC,z)] ]
                               , padding=0, border=0)
window.set_size(int(shape[0]*600), int(shape[1]*600))

@window.event
def on_mouse_motion(x,y,dx,dy):
    global L,N,BN,BC,n

    i,x0,y0,w,h = items[0]
    x0, y0 = x0*600*shape[0],   y0*600*shape[1]
    w, h = w*600*shape[0]-1, h*600*shape[1]+1
    x = min(max(x-x0,0),w)/float(w)*512
    y = (1-min(max(y-y0,0),h)/float(h))*512
    x = max(min(x,512-n//2),n//2)
    y = max(min(y,512-n//2),n//2)
    N.data[...]  = L.data[y-n//2:y+n//2, x-n//2:x+n//2]
    BL.data[...] = L.data[y-n//2:y+n//2, x-n//2:x+n//2]
    BC.data[...] = L.data[y-n//2:y+n//2, x-n//2:x+n//2]
    window.draw()

@window.event
def on_draw():
    window.clear()
    for item in items:
        img,x,y,w,h = item
        x,y = x*600*shape[0],   y*600*shape[1]
        w,h = w*600*shape[0]-1, h*600*shape[1]+1
        img.update()
        img.blit(x,y,w,h)

window.mainloop()
