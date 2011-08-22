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
This example demonstrates Vetrx Buffer creation & display.
'''
import numpy as np
import OpenGL.GL as gl
from glumpy import figure, VertexBuffer, Trackball


# --------------------------------------------------------------------- Cube ---
class Cube(object):
    def __init__(self, size=.5):
        s = size
        p = ( ( s, s, s), (-s, s, s), (-s,-s, s), ( s,-s, s),
              ( s,-s,-s), ( s, s,-s), (-s, s,-s), (-s,-s,-s) )
        n = ( ( 0, 0, 1), (1, 0, 0), ( 0, 1, 0),
              (-1, 0, 1), (0,-1, 0), ( 0, 0,-1) );
        c = ( ( 1, 1, 1), ( 1, 1, 0), ( 1, 0, 1), ( 0, 1, 1),
              ( 1, 0, 0), ( 0, 0, 1), ( 0, 1, 0), ( 0, 0, 0) );
        vertices = np.array(
            [ (p[0],n[0],c[0]), (p[1],n[0],c[1]), (p[2],n[0],c[2]), (p[3],n[0],c[3]),
              (p[0],n[1],c[0]), (p[3],n[1],c[3]), (p[4],n[1],c[4]), (p[5],n[1],c[5]),
              (p[0],n[2],c[0]), (p[5],n[2],c[5]), (p[6],n[2],c[6]), (p[1],n[2],c[1]),
              (p[1],n[3],c[1]), (p[6],n[3],c[6]), (p[7],n[3],c[7]), (p[2],n[3],c[2]),
              (p[7],n[4],c[7]), (p[4],n[4],c[4]), (p[3],n[4],c[3]), (p[2],n[4],c[2]),
              (p[4],n[5],c[4]), (p[7],n[5],c[7]), (p[6],n[5],c[6]), (p[5],n[5],c[5]) ], 
            dtype = [('position','f4',3), ('normal','f4',3), ('color','f4',3)] )
        self.buffer = VertexBuffer(vertices)
        self.trackball = Trackball(65, 135, 1.25, 3.5)

    def on_init(self):
        gl.glEnable( gl.GL_BLEND )
        gl.glEnable( gl.GL_LINE_SMOOTH )
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_mouse_drag(self, x, y, dx, dy, button):
        self.trackball.drag_to(x,y,dx,dy)
        fig.draw()

    def on_draw(self):
        fig.clear()
        self.trackball.push()

        gl.glEnable( gl.GL_POLYGON_OFFSET_FILL )
        gl.glPolygonOffset (1, 1)
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_FILL )
        self.buffer.draw( gl.GL_QUADS, 'pnc' )

        gl.glDisable( gl.GL_POLYGON_OFFSET_FILL )
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE )
        gl.glDepthMask( gl.GL_FALSE )
        gl.glColor( 0.0, 0.0, 0.0, 0.5 )
        self.buffer.draw( gl.GL_QUADS, 'p' )
        gl.glDepthMask( gl.GL_TRUE )

        self.trackball.pop()


# -------------------------------------------------------------------- main ---
if __name__ == '__main__':
    fig = figure(size=(400,400))
    cube = Cube()
    fig.push(cube)
    fig.show()
