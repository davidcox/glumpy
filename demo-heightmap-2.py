#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy, glumpy
from glumpy.pylab import *
import matplotlib.pyplot as plt

class Mesh(object):
    def __init__(self, n=64):
        self.indices  = numpy.zeros((n-1,n-1,4), dtype=numpy.float32)
        self.vertices = numpy.zeros((n,n,3), dtype=numpy.float32)
        self.texcoords= numpy.zeros((n,n,2), dtype=numpy.float32)
        for xi in range(n):
            for yi in range(n):
                x,y,z = xi/float(n-1), yi/float(n-1), 0
                self.vertices[xi,yi] =  x-0.5,y-0.5,z
                self.texcoords[xi,yi] = x,y
        for yi in range(n-1):
            for xi in range(n-1):
                i = yi*n + xi
                self.indices[xi,yi] = i,i+1,i+n+1,i+n
    def draw(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY);
        gl.glVertexPointerf(self.vertices)
        gl.glTexCoordPointerf(self.texcoords)
        gl.glDrawElementsus(gl.GL_QUADS, self.indices)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY);




if __name__ == '__main__':

    window = glumpy.Window(width=800,height=600)
    trackball = glumpy.Trackball(60,30,1.1)
    mesh = Mesh(32)

    # def func3(x,y):
    #     return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
    # dx, dy = .01, .01
    # x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
    # y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
    # Z = func3(*numpy.meshgrid(x, y))

    n = 256.0
    X = numpy.empty((n,n), dtype=numpy.float32)
    X.flat = numpy.arange(n)*2*numpy.pi/n
    Y = numpy.empty((n,n), dtype=numpy.float32)
    Y.flat = numpy.arange(n)*2*numpy.pi/n
    Y = numpy.transpose(Y)
    Z = numpy.sin(X) + numpy.cos(Y)
    I = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Hot, displace=True)


    @window.event
    def on_draw():
        gl.glClearColor(1,1,1,1)
        window.clear()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        angle = 15+105*(trackball.zoom-1)
        glu.gluPerspective(angle, window.width / float(window.height), .1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glTranslatef(0, 0, -3)
        gl.glMultMatrixf(trackball.matrix)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glPolygonOffset (1.0, 1.0)
        gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glEnable (gl.GL_POLYGON_OFFSET_FILL)

        gl.glPushMatrix()
        gl.glScalef(1,1,0.25)
        gl.glTranslatef(0,0,-0.5)
        gl.glColor4f(1,1,1,1)
        I.shader.bind(I.texture,I._lut)
        mesh.draw()
        gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glDisable (gl.GL_POLYGON_OFFSET_FILL)
        gl.glColor4f(0,0,0,.25)
        mesh.draw()
        I.shader.unbind()
        gl.glPopMatrix()

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

        gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_FILL)


    @window.event
    def on_mouse_drag(x, y, dx, dy, button):
        ''' Computes new rotation according to mouse drag '''
        x  = (x*2.0 - window.width)/float(window.width)
        dx = 2*dx/float(window.width)
        y  = (y*2.0 - window.height)/float(window.height)
        dy = 2*dy/float(window.height)
        trackball.drag_to(x,y,dx,dy)
        window.draw()

    @window.event
    def on_mouse_scroll(x, y, dx, dy):
        ''' Computes new zoom according to mouse scroll '''
        trackball.zoom_to(x,y,dx,dy)
        window.draw()

    @window.timer(30.0)
    def update(dt):
        global X,Y
        X += numpy.pi/150.
        Y += numpy.pi/200.
        Z[...] = numpy.sin(X) + numpy.cos(Y)
        I.update()
        window.draw()

    window.mainloop()


