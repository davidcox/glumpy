#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# glumpy - Fast OpenGL numpy visualization
# Copyright (c) 2009, 2010 - Nicolas P. Rougier
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
import numpy as np
import OpenGL.GL as gl
import texture, shader, colormap, color

class Image(object):
    ''' '''
    def __init__(self, Z, format=None, cmap=colormap.IceAndFire, vmin=None,
                 vmax=None, interpolation='nearest', origin='lower'):
        ''' Creates an image from a numpy array.

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
        self.texture = texture.Texture(Z)
        self.cmap = cmap
        self.origin = origin
        self.vmin = vmin
        self.vmax = vmax
        self.Z = Z

        # Source format is RGB or RGBA, no need of a colormap
        if self.texture.src_format in [gl.GL_RGB,gl.GL_RGBA]:
            if interpolation == 'bicubic':
                self.shader = shader.Bicubic(False)
            elif interpolation == 'bilinear':
                self.shader = shader.Bilinear(False)
            else:
                self.shader = None
        # Source format is not RGB or RGBA
        else:
            if cmap:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(True)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(True)
                else:
                    self.shader = shader.Nearest(True)
            else:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(False)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(False)
                else:
                    self.shader = None
        self.update()


    @property
    def shape(self):
        ''' Underlying array shape. '''
        return self.Z.shape

    @property
    def format(self):
        ''' Source representation format string. '''
        format = self.texture.src_format
        if format == gl.GL_ALPHA:
            return 'A'
        elif format == gl.GL_LUMINANCE_ALPHA:
            return 'LA'
        elif format == gl.GL_RGB:
            return 'RGB'
        elif format == gl.GL_RGBA:
            return 'RGBA'

    @property
    def cmap(self):
        ''' Colormap to be used to represent the array. '''
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        ''' Colormap to be used to represent the array. '''
        self._cmap = cmap
        colors = self.cmap.LUT['rgb'][1:].flatten().view((np.float32,3))
        self._lut = texture.Texture(colors)
        self.interpolation = self.interpolation # This is not a no-op line

    @property
    def origin(self):
        ''' Place the [0,0] index of the array in the upper left or lower
            left corner. '''
        return self._origin

    @origin.setter
    def origin(self, origin):
        ''' Place the [0,0] index of the array in the upper left or lower
            left corner. '''
        self._origin = origin

    @property
    def interpolation(self):
        ''' Interpolation method. '''
        return self._interpolation

    @interpolation.setter
    def interpolation(self, interpolation):
        ''' Interpolation method. '''
        self._interpolation = interpolation
        if self.texture.src_format in [gl.GL_RGB,gl.GL_RGBA]:
            if interpolation == 'bicubic':
                self.shader = shader.Bicubic(False)
            elif interpolation == 'bilinear':
                self.shader = shader.Bilinear(False)
            else:
                self.shader = None
        else:
            if self._cmap:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(True)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(True)
                else:
                    self.shader = shader.Nearest(True)
            else:
                if interpolation == 'bicubic':
                    self.shader = shader.Bicubic(False)
                elif interpolation == 'bilinear':
                    self.shader = shader.Bilinear(False)
                else:
                    self.shader = None

    @property
    def vmin(self):
        ''' Minimal representable value. '''
        return self._vmin

    @vmin.setter
    def vmin(self, vmin):
        ''' Minimal representable value. '''
        self._vmin = vmin

    @property
    def vmax(self):
        ''' Maximal representable value. '''
        return self._vmax

    @vmax.setter
    def vmax(self, vmax):
        ''' Maximal representable value. '''
        self._vmax = vmax
        
    def update(self):
        ''' Data update. '''
        if self.vmin is None:
            vmin = self.Z.min()
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax = self.Z.max()
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
