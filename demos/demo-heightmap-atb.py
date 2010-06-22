#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from ctypes import *
import numpy
import glumpy
import glumpy.atb as atb
import OpenGL.GL as gl
import OpenGL.GLUT as glut



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

    window = glumpy.Window(900,600)
    trackball = glumpy.Trackball(60,30,0.85)
    mesh = Mesh(64)
    def func3(x,y):
        return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
    dx, dy = .05, .05
    x = numpy.arange(-3.0, 3.0, dx, dtype=numpy.float32)
    y = numpy.arange(-3.0, 3.0, dy, dtype=numpy.float32)
    Z = func3(*numpy.meshgrid(x, y))
    I = glumpy.Image(Z, interpolation='bilinear',
                     cmap=glumpy.colormap.Hot,
                     lighted=True, grid=(32,32,0), elevation = 0.5)

    diffuse = (c_float*4)(1.0, 1.0, 1.0, 1.0)
    ambient = (c_float*4)(0.3, 0.3, 0.3, 1.0)
    specular = (c_float*4)(0.0, 0.0, 0.0, 0.0)
    position = (c_float*4)(2.0, 2.0, 2.0, 0.0)

    Interpolation = {'nearest' : 0, 'bilinear' : 1, 'bicubic' : 2}
    def set_interpolation(interpolation):
        d = dict(zip(Interpolation.values(), Interpolation.keys()))
        I.interpolation = d.get(interpolation,0)
    def get_interpolation():
        return Interpolation[I.interpolation]

    Colormap = {'IceAndFire' : 0, 'Hot'       : 1,  'Ice'        : 2,
                'Fire'       : 3, 'Grey'      : 4,  'Grey_r'     : 5,
                'DarkRed'    : 6, 'DarkBlue'  : 7,  'DarkGreen'  : 8,
                'LightRed'   : 9, 'LightBlue' : 10, 'LightGreen' : 11}
    def set_cmap(cmap):
        d = dict(zip(Colormap.values(), Colormap.keys()))
        I.cmap = getattr(glumpy.colormap, d.get(cmap,0))
    def get_cmap():
        return Colormap[I.cmap.name]

    bar = atb.Bar(name="Controls", label="Controls",
                  help="Scene controls", position=(10, 10), size=(200, 320))
    bar.add_var("Trackball/Phi", step=0.5,
                getter=trackball._get_phi, setter=trackball._set_phi)
    bar.add_var("Trackball/Theta", step=0.5,
                getter=trackball._get_theta, setter=trackball._set_theta)
    bar.add_var("Trackball/Zoom", step=0.01,
                getter=trackball._get_zoom, setter=trackball._set_zoom)
    bar.add_var("Light/State", getter=I._get_lighted, setter=I._set_lighted)
    bar.add_var("Light/Position", position, vtype=atb.TW_TYPE_QUAT4F)
    bar.add_var("Light/Diffuse", diffuse)
    bar.add_var("Light/Ambient", ambient)
    bar.add_var("Light/Specular", specular)
    bar.add_var("Object/Elevation", step=0.01,
                getter=I._get_elevation, setter=I._set_elevation)
    bar.add_var("Object/Interpolation", vtype=atb.enum("Interpolation",Interpolation),
                getter=get_interpolation, setter=set_interpolation)
    bar.add_var("Object/Colormap", vtype=atb.enum("Colormap",Colormap),
                getter=get_cmap, setter=set_cmap)
    bar.add_separator("")
    bar.add_button("Quit", quit, key="ESCAPE", help="Quit application")


    def draw_background():
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_DEPTH_TEST)
        gl.glPolygonMode (gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glBegin(gl.GL_QUADS)
        gl.glColor(1.0,1.0,1.0)
        gl.glVertex(0,0,-1)
        gl.glVertex(viewport[2],0,-1)
        gl.glColor(0.0,0.0,1.0)
        gl.glVertex(viewport[2],viewport[3],0)
        gl.glVertex(0,viewport[3],0)
        gl.glEnd()

    def on_draw():
        gl.glClearColor(1,1,1,1)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE, diffuse)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT, ambient)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR,specular)
        window.clear()
        draw_background()
        trackball.push()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glTranslatef(0,0, -I.elevation/2.)
        gl.glColor4f(1,1,1,1)
        I.shader.bind(I.texture,I._lut)
        mesh.draw()
        I.shader.unbind()
        trackball.pop()

    def on_init():
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR,(0.0, 0.0, 0.0, 1.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION,(2.0, 2.0, 2.0, 0.0))

    def on_mouse_drag(x, y, dx, dy, button):
        trackball.drag_to(x,y,dx,dy)
        bar.update()
        window.draw()

    def on_mouse_scroll(x, y, dx, dy):
        trackball.zoom_to(x,y,dx,dy)
        bar.update()
        window.draw()

    window.push_handlers(on_mouse_drag, on_mouse_scroll) #, on_key_press)
    window.push_handlers(atb.glumpy.Handlers(window))
    window.push_handlers(on_init, on_draw)

    window.mainloop()
