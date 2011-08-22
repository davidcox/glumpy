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
Text label
'''
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from font import get_font
from vertex_buffer import VertexBuffer


class Label(object):
    '''
    '''
    def __init__( self, text, family='Sans', size=16, bold=False, italic=False,
                  color=(1.0, 1.0, 1.0, 1.0), x=0, y=0, z=0,
                  anchor_x='left', anchor_y='baseline', filename='./Arial.ttf'):
        self._text = text
        self._font = get_font(filename, size)
        self._color = color
        self._x = x
        self._y = y
        self._z = z
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self.build()



    def build(self):
        self.vertices = np.zeros( len(self._text)*4,
                                  dtype = [('position',  'f4',3),
                                           ('tex_coord', 'f4',2),
                                           ('color',     'f4',4)] )
        self.indices  = np.zeros( (len(self._text)*6, ), dtype=np.uint32 )

        prev = None
        x,y = 0, 0
        for i,charcode in enumerate(self._text):
            glyph = self._font[charcode]
            kerning = glyph.get_kerning(prev)/64.0
            x0 = int(x + glyph.offset[0] + kerning)
            y0 = int(y + glyph.offset[1])
            x1 = x0 + glyph.size[0]
            y1 = y0 - glyph.size[1]
            u0 = glyph.texcoords[0]
            v0 = glyph.texcoords[1]
            u1 = glyph.texcoords[2]
            v1 = glyph.texcoords[3]
            index     = i*4
            indices   = [index, index+1, index+2, index, index+2, index+3]
            vertices  = [[x0,y0,0],[x0,y1,0],[x1,y1,0], [x1,y0,0]]
            texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]
            colors    = [self._color,]*4
            self.indices[i*6:i*6+6] = indices
            self.vertices['position'][i*4:i*4+4] = vertices
            self.vertices['tex_coord'][i*4:i*4+4] = texcoords
            self.vertices['color'][i*4:i*4+4] = colors
            x += glyph.advance[0]/64.0 + kerning
            y += glyph.advance[1]/64.0
            prev = charcode
        width = x+glyph.advance[0]/64.0+glyph.size[0]

        if self._anchor_y == 'top':
            dy = -round(self._font.ascender)
        elif self._anchor_y == 'center':
            dy = +round(-self._font.height/2-self._font.descender)
        elif self._anchor_y == 'bottom':
            dy = -round(self._font.descender)
        else:
            dy = 0
        if self._anchor_x == 'right':
            dx = -width/1.0
        elif self._anchor_x == 'center':
            dx = -width/2.0
        else:
            dx = 0
        self.vertices['position'] += self._x+round(dx), self._y+round(dy), self._z
        self.buffer = VertexBuffer(self.vertices, self.indices)


    def draw(self):
        gl.glDisable (gl.GL_TEXTURE_1D)
        gl.glEnable( gl.GL_TEXTURE_2D )
        gl.glDisable( gl.GL_DEPTH_TEST )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self._font.texid )
        gl.glEnable( gl.GL_BLEND )
        gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
        gl.glColor(1,1,1,1)
        self.buffer.draw(gl.GL_TRIANGLES)


    def _get_position(self):
        return self._x, self.y, self._z
    def _set_position(self, position):
        x,y = position
        self.vertices['position'] -= self._x, self._y, 0
        self._x, self._y = x,y
        self.vertices['position'] += x, y, 0
        self.vbo.upload()
    position = property(_get_position, _set_position)
