#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2008, dunkfordyce - 2010, Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import sys
import glumpy
import glumpy.atb as atb
import OpenGL.GL as gl, OpenGL.GLUT as glut
from ctypes import *


def quit(*args, **kwargs):
    sys.exit()

if __name__ == '__main__':
    window = glumpy.Window(800, 600)
    trackball = glumpy.Trackball(45,135,1.25,4)
    bar = atb.Bar(name="Controls", label="Controls",
                  help="Scene controls", position=(10, 10), size=(200, 320))

    fill = c_int(1)
    color = (c_float * 3)(1.0,1.0,0.3)
    shape = c_int()
    bar.add_var("Trackball/Phi", step=0.5,
                getter=trackball._get_phi, setter=trackball._set_phi)
    bar.add_var("Trackball/Theta", step=0.5,
                getter=trackball._get_theta, setter=trackball._set_theta)
    bar.add_var("Trackball/Zoom", step=0.01,
                getter=trackball._get_zoom, setter=trackball._set_zoom)
    Shape = atb.enum("Shape", {'Cube':0, 'Torus':1, 'Teapot':2})
    bar.add_var("Object/Shape", shape, vtype=Shape)
    bar.add_var("Object/Fill", fill)
    bar.add_var("Object/Color", color, open=True)
    bar.add_separator("")
    bar.add_button("Quit", quit, key="ESCAPE", help="Quit application")


    def draw_background():
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_DEPTH_TEST);
        gl.glBegin(gl.GL_QUADS)
        gl.glColor(1.0,1.0,1.0)
        gl.glVertex(0,0,-1)
        gl.glVertex(viewport[2],0,-1)
        gl.glColor(0.0,0.0,1.0)
        gl.glVertex(viewport[2],viewport[3],0)
        gl.glVertex(0,viewport[3],0)
        gl.glEnd()

    def draw_teapot():
        if fill.value:
            gl.glEnable (gl.GL_LIGHTING)
            gl.glEnable (gl.GL_DEPTH_TEST)
            gl.glColor3f(color[0],color[1],color[2])
            gl.glPolygonOffset (1, 1)
            gl.glEnable (gl.GL_POLYGON_OFFSET_FILL)
            if shape.value == 0:
                glut.glutSolidCube(1)
            elif shape.value == 1:
                glut.glutSolidTorus(0.25, 0.50, 32, 32)
            else:
                glut.glutSolidTeapot(.75)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_POLYGON_OFFSET_FILL)
        gl.glEnable (gl.GL_LINE_SMOOTH)
        gl.glEnable (gl.GL_BLEND)                     
        gl.glDepthMask (gl.GL_FALSE)
        gl.glColor4f(0,0,0,.5)
        if shape.value == 0:
            glut.glutWireCube(1)
        elif shape.value == 1:
            glut.glutWireTorus(0.25, 0.50, 32, 32)
        else:
            glut.glutWireTeapot(.75)
        gl.glDepthMask (gl.GL_TRUE)

    def on_init():
        gl.glEnable (gl.GL_LIGHT0)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT,  (0.1, 0.1, 0.1, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION, (0.0, 1.0, 2.0, 1.0))
        gl.glEnable (gl.GL_BLEND)
        gl.glEnable (gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_draw():
        window.clear()
        draw_background()
        trackball.push()
        #gl.glRotate(90,1,0,0)
        draw_teapot()
        trackball.pop()

    def on_mouse_drag(x, y, dx, dy, button):
        trackball.drag_to(x,y,dx,dy)
        bar.update()
        window.draw()

    def on_mouse_scroll(x, y, dx, dy):
        trackball.zoom_to(x,y,3*dx,3*dy)
        bar.update()
        window.draw()

    def on_key_press(symbol, modifiers):
        if symbol == glumpy.key.ESCAPE:
            sys.exit()

    window.push_handlers(on_init,on_mouse_drag, on_mouse_scroll, on_key_press)
    window.push_handlers(atb.glumpy.Handlers(window))
    window.push_handlers(on_draw)
    window.mainloop()



