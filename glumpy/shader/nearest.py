#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
''' Nearest interpolation shaders '''
from shader import Shader, read_shader
import OpenGL.GL as gl

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
