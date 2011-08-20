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
                 gridsize=(0.0,0.0,0.0), elevation = 0.0):
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
        self._gridsize = gridsize
        self._elevation = elevation
        self._texture = texture.Texture(Z)
        self._origin = origin
        self._vmin = vmin
        self._vmax = vmax
        self._data = Z
        self.cmap = cmap   # This takes care of actual build
        self._shader = None
        self.build()

    def build(self):
        ''' Build shader '''

        interpolation = self._interpolation
        gridsize = self._gridsize
        elevation = self._elevation
        lighted = self._lighted
        cmap = self._cmap
        self._shader = None

        # Source format is RGB or RGBA, no need of a colormap
        if self._texture.src_format in [gl.GL_RGB,gl.GL_RGBA]:
            if interpolation == 'bicubic':
                self._shader = shader.Bicubic(False, lighted=lighted, gridsize=gridsize, elevation=elevation)
            elif interpolation == 'bilinear':
                self._shader = shader.Bilinear(False, lighted=lighted, gridsize=gridsize, elevation=elevation)
            else:
                self._shader = None
        # Source format is not RGB or RGBA
        else:
            if cmap:
                if interpolation == 'bicubic':
                    self._shader = shader.Bicubic(True, lighted=lighted, gridsize=gridsize, elevation=elevation)
                elif interpolation == 'bilinear':
                    self._shader = shader.Bilinear(True, lighted=lighted, gridsize=gridsize, elevation=elevation)
                else:
                    self._shader = shader.Nearest(True, lighted=lighted, gridsize=gridsize, elevation=elevation)
            else:
                if interpolation == 'bicubic':
                    self._shader = shader.Bicubic(False, lighted=lighted, gridsize=gridsize, elevation=elevation)
                elif interpolation == 'bilinear':
                    self._shader = shader.Bilinear(False, lighted=lighted, gridsize=gridsize, elevation=elevation)
                else:
                    self._shader = None
        self.update()


    @property
    def shape(self):
        ''' Underlying array shape. '''
        return self._data.shape

    @property
    def data(self):
        ''' Underlying array '''
        return self._data

    @property
    def texture(self):
        ''' Underlying texture '''
        return self._texture

    @property
    def shader(self):
        ''' Currently active shader '''
        return self._shader

    @property
    def format(self):
        ''' Array representation format (string). '''
        format = self._texture.src_format
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
    cmap = property(_get_cmap, _set_cmap,
                    doc=''' Colormap to be used to represent the array. ''')

    def _get_elevation(self):
        return self._elevation
    def _set_elevation(self, elevation):
        # Do we need to re-build shader ?
        if not (elevation*self._elevation):
            self._elevation = elevation
            self.build()
        elif self._shader:
            self._elevation = elevation
            self._shader._elevation = elevation
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
        self.build()
    lighted = property(_get_lighted, _set_lighted,
                       doc=''' Indicate whether image is ligthed. ''')


    def _get_interpolation(self):
        return self._interpolation
    def _set_interpolation(self, interpolation):
        self._interpolation = interpolation
        self.build()
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


    def _get_gridsize(self):
        return self._gridsize
    def _get_gridsize_x(self):
        return self._gridsize[0]
    def _get_gridsize_y(self):
        return self._gridsize[1]
    def _get_gridsize_z(self):
        return self._gridsize[2]
    def _set_gridsize(self, gridsize):
        # Do we need to re-build shader ?
        x,y,z = gridsize
        x,y,z = max(0,x),max(0,y),max(0,z)
        _x,_y,_z = self._gridsize
        self._gridsize = x,y,z
        if not (x+y+z)*(_x+_y+_z) and (x+y+z)+(_x+_y+_z):
            self.build()
        elif self._shader:
            self._shader._gridsize = x,y,z
    def _set_gridsize_x(self, x):
        self.gridsize = (max(0,x), self._gridsize[1], self._gridsize[2])
    def _set_gridsize_y(self, y):
        self.gridsize = (self._gridsize[0], max(0,y), self._gridsize[2])
    def _set_gridsize_z(self, z):
        self.gridsize = (self._gridsize[0], self._gridsize[1], max(0,z))
    gridsize = property(_get_gridsize, _set_gridsize, 
                    doc=''' Image grid (x,y,z). ''')
        
    def update(self):
        ''' Data update. '''
        if self.vmin is None:
            vmin = self.data.min()
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax = self._data.max()
        else:
            vmax = self.vmax
        if vmin == vmax:
            vmin, vmax = 0, 1
        if self._lut:
            s = self._lut.width
            self._texture.update(bias = 1.0/(s-1)-vmin*((s-3.1)/(s-1))/(vmax-vmin),
                                 scale = ((s-3.1)/(s-1))/(vmax-vmin))
        else:
            self._texture.update(bias=-vmin/(vmax-vmin),scale=1.0/(vmax-vmin))

    def blit(self, x, y, w, h):
        ''' Blit array onto active framebuffer. '''
        if self._shader:
            self._shader.bind(self.texture,self._lut)
        if self.origin == 'lower':
            t=0,1
        else:
            t=1,0
        gl.glColor(1,1,1,1)
        self._texture.blit(x,y,w,h,t=t)
        if self._shader:
            self._shader.unbind()
