#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
import math
import ctypes
import OpenGL.GL as gl
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
    def __init__(self, use_lut=False, lighted=False, grid=(0.0,0.0,0.0), height=0.0):
        self._lighted = lighted
        self._gridsize = grid
        self._gridwidth = (1.0,1.0,1.0)
        self._height = height
        interpolation = read_shader('bicubic.txt')
        light         = read_shader('phong.txt')
        lut           = read_shader('lut.txt')
        vertex        = read_shader('vertex.txt')
        fragment      = read_shader('fragment.txt')
        lut_code = light_code = grid_code = ''
        if use_lut:
            lut_code = 'color = texture1D_lut(lut, color.a);'
        if lighted:
            light_code = read_shader('light.txt')
        if self._gridsize[0] or self._gridsize[1] or self._gridsize[2]:
            grid_code = read_shader('grid.txt')
        fragment  = fragment % (lut_code,grid_code,light_code)
        Shader.__init__(self,
          vert = [interpolation] + [vertex],
          frag = [interpolation] + [light] + [lut] + [fragment])
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
        self.uniformf('height', self._height)
        self.uniformf('pixel', 1.0/texture.width, 1.0/texture.height)
        self.uniformf('gridsize', *self._gridsize)
        self.uniformf('gridwidth', *self._gridwidth)
