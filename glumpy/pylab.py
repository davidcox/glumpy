#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
import sys
import numpy, glumpy
import OpenGL.GL as gl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_frame = None
_transparent = numpy.array([1,2,3,255])
_items = []
items = _items

def imshow(X, cmap=None, norm=None, aspect=None, interpolation=None,
           alpha=1.0, vmin=None, vmax=None, origin=None, extent=None,
           **kwargs):

    '''pylab imshow proxy function.

       This function first call the pylab original imshow function using an
       alpha level of 0 (fully transparent). It then set axes background with a
       dedicated 'transparent' color that will be replaced later by a truly
       transparent color.

       Warning: any pixel with 'transparent' color will be replaced by a
                transparent pixel. If this causes problem, you will have to
                change the definition of 'transparent' to something else.
    '''
    axis = plt.imshow(X, cmap=cmap, norm=norm, aspect=aspect,
                      interpolation='nearest', alpha=0, vmin=vmin,
                      vmax=vmax, origin=origin, extent=extent, **kwargs)

    r,g,b,a = _transparent/255.0
    cmap = axis.cmap
    under = cmap(-1.0)
    over = cmap(2.0)
    axis.cmap.set_over((r,g,b), alpha=0)
    axis.cmap.set_under((r,g,b), alpha=0)
    axis.cmap.set_bad((r,g,b), alpha=0)
    axes = axis.get_axes()
    axes.patch.set_facecolor((r,g,b))
    axes.patch.set_alpha(a)

    # Build glumpy colormap from matplotlib colormap
    colors=[]
    for i in range(510):
        colors.append((i/510.0, cmap(i/510.0, alpha=alpha)))
    cmap = glumpy.colormap.Colormap(*colors,
                                     over=glumpy.Color(over),
                                     under=glumpy.Color(under))
    image = glumpy.Image(X,interpolation=interpolation,
                         cmap=cmap, vmin=vmin, vmax=vmax)
    image.update()
    _items.append([image,axis,alpha])
    return axis


def show(interpolation='nearest'):
    ''' pylab show proxy function. '''
    global frame

    # Draw current figure to rgba buffer
    fig = plt.gcf()
    fig.canvas.draw()
    buffer = fig.canvas.buffer_rgba(0,0)
    x,y,w,h = fig.bbox.bounds
    F = numpy.fromstring(buffer,numpy.uint8).copy()
    F.shape = h,w,4

    # Replace 'transparent' color with a real transparent color
    v = numpy.array(_transparent,dtype=numpy.uint8).view(dtype=numpy.int32)[0]
    Ft = numpy.where(F.view(dtype=numpy.int32) == v, 0, F)

    # Create main frame 
    window = glumpy.Window(512,512) #Ft.shape[1], Ft.shape[0])
    frame = glumpy.Image(Ft,interpolation=interpolation)
    frame.update()

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    @window.event
    def on_resize(width,height):
        global frame

        fig = plt.gcf()
        dpi = float(fig.dpi)        
        winch = width/dpi
        hinch = height/dpi
        fig.set_size_inches(winch, hinch)
        fig.canvas.draw()
        buffer = fig.canvas.buffer_rgba(0,0)
        x,y,w,h = fig.bbox.bounds
        F = numpy.fromstring(buffer,numpy.uint8).copy()
        F.shape = h,w,4
        # Replace 'transparent' color with a real transparent color
        v = numpy.array(_transparent,dtype=numpy.uint8).view(dtype=numpy.int32)[0]
        Ft = numpy.where(F.view(dtype=numpy.int32) == v, 0, F)
        # Create main frame 
        frame = glumpy.Image(Ft,interpolation=interpolation)
        frame.update()

    @window.event
    def on_draw():
        window.clear()
        for image,axis, alpha in _items:
            x,y,w,h = axis.get_axes().bbox.bounds
            x /= float(frame.shape[1])
            y /= float(frame.shape[0])
            w /= float(frame.shape[1])
            h /= float(frame.shape[0])
            gl.glColor4f(1,1,1,alpha)
            image.blit(x*window.width,y*window.height,
                       w*window.width,h*window.height)
        gl.glColor4f(1,1,1,1)
        frame.blit(0,0,window.width, window.height)


    @window.event
    def on_key_press(symbol, modifiers):
        #if symbol == pyglet.window.key.SPACE:
        #    savefig('test.png', window.width, window.height)
        if symbol == glumpy.key.ESCAPE:
            if (window.width == frame.shape[1] and
                window.height == frame.shape[0]):
                sys.exit()
            else:
                window.set_size(frame.shape[1], frame.shape[0])
            return True

    return window
