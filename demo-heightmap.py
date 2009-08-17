#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# glumpy - Fast OpenGL numpy visualization
# Copyright (c) 2009 - Nicolas P. Rougier
#
# This file is part of glumpy.
#
# glumpy is free  software: you can redistribute it and/or  modify it under the
# terms of  the GNU General  Public License as  published by the  Free Software
# Foundation, either  version 3 of the  License, or (at your  option) any later
# version.
#
# glumpy is  distributed in the  hope that it  will be useful, but  WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy  of the GNU General Public License along with
# glumpy. If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
import pyglet
import numpy as np
import glumpy


class Mesh(object):
    def __init__(self, n=64):
        indices, vertices, texcoords = [], [], []
        for xi in range(n):
            for yi in range(n):
                x,y,z = xi/float(n-1), yi/float(n-1), 0
                vertices  += [x-0.5,y-0.5,z]
                texcoords += [x,y]
        for yi in range(n-1):
            for xi in range(n-1):
                i = yi*n + xi
                indices += [i,i+1,i+n+1,i+n]
        self.vlist = pyglet.graphics.vertex_list_indexed(n*n, indices,
                                                         ('v3f', vertices),
                                                         ('t2f', texcoords))
    def draw(self):
        self.vlist.draw(gl.GL_QUADS)



if __name__ == '__main__':

    window = pyglet.window.Window(width=800,height=600,
                                  vsync=0,resizable=True, visible=False)
    trackball = glumpy.Trackball(60,30,1.1)
    mesh = Mesh(64)

    def func3(x,y):
        return np.sin(x*x+y*y)*np.cos(x+y*y)*np.sin(y) 
    #return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
    dx, dy = .05, .05
    x = np.arange(-4.0, 4.0, dx, dtype=np.float32)
    y = np.arange(-4.0, 4.0, dy, dtype=np.float32)
    Z = func3(*np.meshgrid(x, y))

    I = glumpy.Image(Z, interpolation='bilinear',
                     cmap=glumpy.colormap.Hot, displace=True)
   
    @window.event
    def on_draw():
        gl.glClearColor(1,1,1,1)
        window.clear()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        angle = 15+105*(trackball.zoom-1)
        gl.gluPerspective(angle, window.width / float(window.height), .1, 1000)
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
        fps_display.draw()

    @window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        ''' Computes new rotation according to mouse drag '''
        x  = (x*2.0 - window.width)/float(window.width)
        dx = 2*dx/float(window.width)
        y  = (y*2.0 - window.height)/float(window.height)
        dy = 2*dy/float(window.height)
        trackball.drag_to(x,y,dx,dy)
        return True

    @window.event
    def on_mouse_scroll(x, y, dx, dy):
        ''' Computes new zoom according to mouse scroll '''
        trackball.zoom_to(x,y,dx,dy)
        return True

    fps_display = pyglet.clock.ClockDisplay()
    window.set_visible(True)
    pyglet.app.run()
