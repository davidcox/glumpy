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
    def __init__(self, use_lut=False, lighted=False,
                 gridsize=(0.0, 0.0, 0.0), elevation=0.0):
        self._lighted = lighted
        self._gridsize = gridsize
        self._gridwidth = (1.0,1.0,1.0)
        self._elevation = elevation
        interpolation = read_shader('nearest.txt')
        light         = read_shader('phong.txt')
        lut           = read_shader('lut.txt')
        vertex        = read_shader('vertex.txt')
        fragment      = read_shader('fragment.txt')
        lut_code = light_code = grid_code = height_code = ''
        if use_lut:
            lut_code = 'color = texture1D_lut(lut, color.a);'
        if lighted:
            light_code = read_shader('light.txt')
        if self._gridsize[0] or self._gridsize[1] or self._gridsize[2]:
            grid_code = read_shader('grid.txt')
        if self._elevation:
            height_code = read_shader('height.txt')
        fragment  = fragment % (lut_code,grid_code,light_code)
        vertex    = vertex % (height_code)
        Shader.__init__(self,
          vert = [interpolation] + [vertex],
          frag = [interpolation] + [light] + [lut] + [fragment])

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
        self.uniformf('elevation', self._elevation)
        self.uniformf('pixel', 1.0/texture.width, 1.0/texture.height)
        self.uniformf('gridsize', *self._gridsize)
        self.uniformf('gridwidth', *self._gridwidth)
        self.uniformi('lighted', self._lighted)
