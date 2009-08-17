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
''' Nearest interpolation shaders '''
from shader import Shader, read_shader
import pyglet.gl as gl

class Nearest(Shader):
    def __init__(self, use_lut=False, displace=False):

        if displace:
            vert = read_shader('vertex_displacement_nearest.txt')
        else:
            vert = read_shader('vertex_standard.txt')

        interpolation = read_shader('fragment_nearest.txt')
        lut = read_shader('fragment_lut.txt')
        if use_lut:
            line = 'color = texture1D_lut(lut, color.a);'
        else:
            line = ''
        frag = interpolation + lut + '''
             uniform sampler2D texture;
             uniform sampler1D lut;
             uniform vec2 pixel;
             void main() {
                 vec2 uv = gl_TexCoord[0].xy;
                 vec4 color = texture2D_nearest(texture, uv);
                 %s
                 gl_FragColor = color*gl_Color;
             } ''' % line
        Shader.__init__(self, vert = [vert], frag = [frag])


    def bind(self, texture, lut=None):
        ''' Bind the program and relevant parameters '''

        Shader.bind(self)
        if lut is not None:
            gl.glActiveTexture(gl.GL_TEXTURE1)
            gl.glBindTexture(lut.target, lut.id)
            self.uniformi('lut', 1)
        gl.glEnable(texture.target)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(texture.target, texture.id)
        self.uniformi('texture', 0)
        self.uniformf('pixel', 1.0/texture.width, 1.0/texture.height)
