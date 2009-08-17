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
import math
import ctypes
import pyglet.gl as gl
from shader import Shader, read_shader


def build_kernel(size=256):
    # From GPU Gems
    # Chapter 24. High-Quality Filtering
    # Kevin Bjorke, NVIDIA
    # http://http.developer.nvidia.com/GPUGems/gpugems_ch24.html
    #
    # Mitchell Netravali Reconstruction Filter
    # a = 1.0, b = 0.0  - cubic B-spline
    # B = 1/3, b = 1/3  - recommended
    # a = 0.5, b = 0.0  - Catmull-Rom spline
    def MitchellNetravali(x, a=1, b=0):
        x = math.fabs(x)
        if x < 1.0:
            return ((12-9*a-6*b) *x*x*x + (-18+12*a+6*b)*x*x + (6-2*a))/6.0
        elif x < 2.0:
            return ((-a-6*b)*x*x*x + (6*a+30*b)*x*x + (-12*a-48*b)*x + (8*a+24*b))/6.0
        else:
            return 0
    
    data = (gl.GLfloat*(4*size))()
    for i in range(size):
        x = i/float(size-1)
        data[i*4+0] = MitchellNetravali(x+1)
        data[i*4+1] = MitchellNetravali(x)
        data[i*4+2] = MitchellNetravali(1-x)
        data[i*4+3] = MitchellNetravali(2-x)
    texid = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(texid))
    kernel = texid.value
    gl.glPixelStorei (gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glPixelStorei (gl.GL_PACK_ALIGNMENT, 1)
    gl.glBindTexture (gl.GL_TEXTURE_1D, texid)
    gl.glTexParameterf (gl.GL_TEXTURE_1D,
                        gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameterf (gl.GL_TEXTURE_1D,
                        gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameterf (gl.GL_TEXTURE_1D,
                        gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
    gl.glTexParameterf (gl.GL_TEXTURE_1D,
                        gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
    gl.glTexImage1D (gl.GL_TEXTURE_1D,  0, gl.GL_RGBA16, size, 0,
                     gl.GL_RGBA, gl.GL_FLOAT, data)
    return kernel


class Bicubic(Shader):
    def __init__(self, use_lut=False, displace=False):
        if displace:
            vert = read_shader('vertex_displacement_bicubic.txt')
        else:
            vert = read_shader('vertex_standard.txt')


        interpolation = read_shader('fragment_bicubic.txt')
        lut = read_shader('fragment_lut.txt')
        if use_lut:
            line = 'color = texture1D_lut(lut, color.a);'
        else:
            line = ''
        Shader.__init__(self,
          vert = [interpolation] + [vert],
          frag = [interpolation] + [lut] + ['''
             uniform sampler2D texture;
             uniform sampler1D kernel;
             uniform sampler1D lut;
             uniform vec2 pixel;
             void main() {
                 vec2 uv = gl_TexCoord[0].xy;
                 vec4 color = texture2D_bicubic(texture, kernel, uv, pixel);
                 %s
                 gl_FragColor = color*gl_Color;
             }''' % line] )
        self.kernel = build_kernel()

    def bind(self, texture, lut=None):
        ''' Bind the program, i.e. use it. '''
        Shader.bind(self)
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_1D, self.kernel)
        self.uniformi('kernel', 2)
        if lut is not None:
            gl.glActiveTexture(gl.GL_TEXTURE1)
            gl.glBindTexture(lut.target, lut.id)
            self.uniformi('lut', 1)
        gl.glEnable(texture.target)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(texture.target, texture.id)
        self.uniformi('texture', 0)
        self.uniformf('pixel', 1.0/texture.width, 1.0/texture.height)
