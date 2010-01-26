#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
from shader import Shader, read_shader
import OpenGL.GL as gl

class Bilinear(Shader):
    def __init__(self, use_lut=False, displace=False):
        if displace:
            vert = read_shader('vertex_displacement_bilinear.txt')
        else:
            vert = read_shader('vertex_standard.txt')
        interpolation = read_shader('fragment_bilinear.txt')
        lut = read_shader('fragment_lut.txt')
        if use_lut:
            line = 'color = texture1D_lut(lut, color.a);'
        else:
            line = ''
        Shader.__init__(self,
          vert = [interpolation] + [vert],
          frag = [interpolation] + [lut] + ['''
             uniform sampler2D texture;
             uniform sampler1D lut;
             uniform vec2 pixel;
             void main() {
                 vec2 uv = gl_TexCoord[0].xy;
                 vec4 color = texture2D_bilinear(texture, uv, pixel);
                 %s
                 gl_FragColor = color*gl_Color;
             }''' % line] )

    def bind(self, texture, lut=None):
        ''' Bind the program, i.e. use it. '''
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
