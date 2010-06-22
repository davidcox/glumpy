#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy as np
import OpenGL.GL as gl
import texture, shader, colormap, color

class Image(object):
    ''' '''
    def __init__(self, Z, format=None, cmap=colormap.IceAndFire, vmin=None, vmax=None,
                 interpolation='nearest', origin='lower', lighted=False, 
                 grid=(0.0,0.0,0.0), elevation = 0.0):
        ''' Creates a texture from numpy array.

        Parameters:
        -----------
        Z : numpy array
            Z may be a float32 or uint8 array with following shapes:
                * M
                * MxN
                * MxNx[1,2,3,4]

        format: [None | 'A' | 'LA' | 'RGB' | 'RGBA']
            Specify the texture format to use. Most of times it is possible to
            find it automatically but there are a few cases where it not
            possible to decide. For example an array with shape (M,3) can be
            considered as 2D alpha texture of size (M,3) or a 1D RGB texture of
            size (M,).

        interpolation: 'nearest', 'bilinear' or 'bicubic'
            Interpolation method.

        vmin: scalar
            Minimal representable value.

        vmax: scalar
            Maximal representable value.

        origin: 'lower' or 'upper'
            Place the [0,0] index of the array in the upper left or lower left
            corner.
        '''

        self._lut = None
        self._interpolation = interpolation
        self._lighted = lighted
        self._grid = grid
        self._elevation = elevation
        self.texture = texture.Texture(Z)
        self.origin = origin
        self.vmin = vmin
        self.vmax = vmax
        self.data = Z

        # Source format is RGB or RGBA, no need of a colormap
        if self.texture.src_format in [gl.GL_RGB,gl.GL_RGBA]:
            if interpolation == 'bicubic':
                self.shader = shader.Bicubic(False, lighted=lighted, grid=grid, elevation=elevation)
            elif interpolation == 'bilinear':
                self.shader = shader.Bilinear(False, lighted=lighted, grid=grid, elevation=elevation)
            else:
                self.shader = None
        # Source format is not RGB or RGBA
        else:
            if cmap:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(True, lighted=lighted, grid=grid, elevation=elevation)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(True, lighted=lighted, grid=grid, elevation=elevation)
                else:
                    self.shader = shader.Nearest(True, lighted=lighted, grid=grid, elevation=elevation)
            else:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(False, lighted=lighted, grid=grid, elevation=elevation)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(False, lighted=lighted, grid=grid, elevation=elevation)
                else:
                    self.shader = None
        self.cmap = cmap
        self.update()


    @property
    def shape(self):
        ''' Underlying array shape. '''
        return self.data.shape

    @property
    def format(self):
        ''' Array representation format (string). '''
        format = self.texture.src_format
        if format == gl.GL_ALPHA:
            return 'A'
        elif format == gl.GL_LUMINANCE_ALPHA:
            return 'LA'
        elif format == gl.GL_RGB:
            return 'RGB'
        elif format == gl.GL_RGBA:
            return 'RGBA'

    def _get_cmap(self):
        return self._cmap
    def _set_cmap(self, cmap):
        self._cmap = cmap
        colors = self.cmap.LUT['rgb'][1:].flatten().view((np.float32,3))
        self._lut = texture.Texture(colors)
        self.interpolation = self.interpolation # This is not a no-op line
    cmap = property(_get_cmap, _set_cmap,
                    doc=''' Colormap to be used to represent the array. ''')


    def _get_elevation(self):
        return self._elevation
    def _set_elevation(self, elevation):
        self._elevation = elevation
        if self.shader:
            self.shader._elevation = self._elevation
    elevation = property(_get_elevation, _set_elevation,
                    doc=''' Image elevation. ''')

    def _get_origin(self):
        return self._origin
    def _set_origin(self, origin):
        self._origin = origin
    origin = property(_get_origin, _set_origin,
                      doc=''' Place the [0,0] index of the array in the upper
                              left or lower left corner. ''')

    def _get_lighted(self):
        return self._lighted
    def _set_lighted(self, lighted):
        self._lighted = lighted
        if self.shader:
            self.shader._lighted = lighted
    lighted = property(_get_lighted, _set_lighted,
                       doc=''' Indicate whether image is ligthed. ''')


    def _get_interpolation(self):
        return self._interpolation
    def _set_interpolation(self, interpolation):
        self._interpolation = interpolation
        if self.texture.src_format in [gl.GL_RGB,gl.GL_RGBA]:
            if interpolation == 'bicubic':
                self.shader = shader.Bicubic(False, lighted = self._lighted,
                                             grid=self._grid, elevation=self._elevation)
            elif interpolation == 'bilinear':
                self.shader = shader.Bilinear(False, lighted = self._lighted,
                                              grid=self._grid, elevation=self._elevation)
            else:
                self.shader = None
        else:
            if self._cmap:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(True, lighted = self._lighted,
                                                 grid=self._grid, elevation=self._elevation) 
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(True, lighted = self._lighted,
                                                  grid=self._grid, elevation=self._elevation)
                else:
                    self.shader = shader.Nearest(True, lighted = self._lighted,
                                                 grid=self._grid, elevation=self._elevation) 
            else:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(False, lighted = self._lighted,
                                                 grid=self._grid, elevation=self._elevation)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(False, lighted = self._lighted,
                                                  grid=self._grid, elevation=self._elevation)
                else:
                    self.shader = None
    interpolation = property(_get_interpolation, _set_interpolation,
                             doc=''' Interpolation method. ''')

    def _get_vmin(self):
        return self._vmin
    def _set_vmin(self, vmin):
        self._vmin = vmin
    vmin = property(_get_vmin, _set_vmin, 
                    doc=''' Minimal representable value. ''')

    def _get_vmax(self):
        return self._vmax
    def _set_vmax(self, vmax):
        self._vmax = vmax
    vmax = property(_get_vmax, _set_vmax, 
                    doc=''' Maximal representable value. ''')
        
    def update(self):
        ''' Data update. '''
        if self.vmin is None:
            vmin = self.data.min()
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax = self.data.max()
        else:
            vmax = self.vmax
        if self._lut:
            s = self._lut.width
            self.texture.update(bias = 1.0/(s-1)-vmin*((s-3.1)/(s-1))/(vmax-vmin),
                                scale = ((s-3.1)/(s-1))/(vmax-vmin))
        else:
            self.texture.update(bias=-vmin/(vmax-vmin),scale=1.0/(vmax-vmin))

    def blit(self, x, y, w, h):
        ''' Blit array onto active framebuffer. '''
        if self.shader:
            self.shader.bind(self.texture,self._lut)
        if self.origin == 'lower':
            t=0,1
        else:
            t=1,0
        self.texture.blit(x,y,w,h,t=t)
        if self.shader:
            self.shader.unbind()
