#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import sys
import glumpy
import OpenGL.GL as gl
import OpenGL.GLUT as glut

if __name__ == '__main__':

    window = glumpy.Window(fullscreen=True)
    trackball = glumpy.Trackball(65,135,1.25,3)

    def draw_background():
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_DEPTH_TEST);
        gl.glBegin(gl.GL_QUADS)
        gl.glColor(1.0,1.0,1.0)
        gl.glVertex(0,0,-1)
        gl.glVertex(viewport[2],0,-1)
        gl.glColor(0.0,0.5,1.0)
        gl.glVertex(viewport[2],viewport[3],0)
        gl.glVertex(0,viewport[3],0)
        gl.glEnd()

    def draw_teapot():
        gl.glEnable (gl.GL_LIGHTING)
        gl.glEnable (gl.GL_DEPTH_TEST)
        gl.glColor3f(1,1,0)
        gl.glPolygonOffset (1, 1)
        gl.glEnable (gl.GL_POLYGON_OFFSET_FILL)
        glut.glutSolidTeapot(.5)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_POLYGON_OFFSET_FILL)
        gl.glEnable (gl.GL_LINE_SMOOTH)
        gl.glDepthMask (gl.GL_FALSE)
        gl.glColor4f(0,0,0,.25)
        glut.glutWireTeapot(.5)
        gl.glDepthMask (gl.GL_TRUE)

    @window.event
    def on_init():
        gl.glEnable (gl.GL_LIGHT0)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION,(0.0, 2.0, 2.0, 0.0))
        gl.glEnable (gl.GL_BLEND)
        gl.glEnable (gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    @window.event
    def on_draw():
        window.clear()
        draw_background()
        trackball.push()
        gl.glRotate(90,1,0,0)
        draw_teapot()
        trackball.pop()

    @window.event
    def on_mouse_drag(x, y, dx, dy, button):
        trackball.drag_to(x,y,dx,dy)
        window.draw()

    @window.event
    def on_mouse_scroll(x, y, dx, dy):
        trackball.zoom_to(x,y,dx,dy)
        window.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == glumpy.key.TAB:
            if window.fullscreen:
                window.fullscreen = False
            else:
                window.fullscreen = True

    window.mainloop()
