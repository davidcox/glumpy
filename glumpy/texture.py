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
''' Texture object.

    A texture is an image loaded into video memory that can be efficiently
    drawn to the framebuffer.
'''
import numpy
import OpenGL.GL as gl


class TextureException(Exception):
    ''' Texture exception object. '''
    pass


class Texture(object):
    ''' Texture object.
    
    A texture is an image loaded into video memory that can be efficiently
    drawn to the framebuffer.
    '''

    def __init__(self, Z, format=None, interpolation=None):
        ''' Create texture.

        :Parameters:
            `Z` : numpy array
                Z may be a float32 or uint8 array with following shapes:
                    * M
                    * MxN
                    * MxNx[1,2,3,4]
            `format`: [None | 'A' | 'LA' | 'RGB' | 'RGBA']
                Specify the texture format to use. Most of times it is possible
                to find it automatically but there are a few cases where it not
                possible to decide. For example an array with shape (M,3) can be
                considered as 2D alpha texture of size (M,3) or a 1D RGB texture
                of size (M,).
        '''
        self._id = 0
        self._build(Z, format)


    def __del__(self):
        if self._id and gl.glDeleteTextures:
            gl.glDeleteTextures([self._id,])


    @property
    def target(self):
        ''' GL texture target (e.g., GL_TEXTURE_2D).

        :type: int, read-only
        '''
        return self._target

    
    @property
    def width(self):
        ''' Texture width.

        :type: int, read-only
        '''
        return self._width



    @property
    def height(self):
        ''' Texture height.

        :type: int, read-only
        '''
        return self._height



    @property
    def id(self):
        ''' GL texture name.

        :type: int, read-only
        '''
        #return self._id.value
        return self._id



    def blit(self, x, y, w, h, z=0, s=(0,1), t=(0,1)):
        ''' Draw texture to active framebuffer. '''

        if self.target == gl.GL_TEXTURE_1D:
            gl.glDisable (gl.GL_TEXTURE_2D)
            gl.glEnable (gl.GL_TEXTURE_1D)
            gl.glBindTexture(self.target, self.id)
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord1f(s[0]), gl.glVertex2f(x,   y)
            gl.glTexCoord1f(s[0]), gl.glVertex2f(x,   y+h)
            gl.glTexCoord1f(s[1]), gl.glVertex2f(x+w, y+h)
            gl.glTexCoord1f(s[1]), gl.glVertex2f(x+w, y)
            gl.glEnd()
        else:
            gl.glEnable (gl.GL_TEXTURE_2D)
            gl.glDisable (gl.GL_TEXTURE_1D)
            gl.glBindTexture(self.target, self.id)
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(s[0], 1), gl.glVertex2f(x,   y)
            gl.glTexCoord2f(s[0], 0), gl.glVertex2f(x,   y+h)
            gl.glTexCoord2f(s[1], 0), gl.glVertex2f(x+w, y+h)
            gl.glTexCoord2f(s[1], 1), gl.glVertex2f(x+w, y)
            gl.glEnd()


    def _build (self, Z, format=None):
        ''' Build a new texture from Z and format. '''

        self._Z = Z

        # Check data type
        dtype = Z.dtype
        if dtype not in [numpy.float32, numpy.uint8]:
            raise TextureException('Array data type must be float32 or uint8.')
        if dtype == numpy.float32:
            self.src_type = gl.GL_FLOAT
        elif dtype == numpy.uint8:
            self.src_type = gl.GL_UNSIGNED_BYTE

        # Find shape & format
        shape = Z.shape
        if len(shape) == 1:
            self._target = gl.GL_TEXTURE_1D
            self.src_format = gl.GL_ALPHA
            self.dst_format = gl.GL_ALPHA16
        elif len(shape) == 2:
            if shape[1] == 1 and format in [None, 'A']:
                self._target = gl.GL_TEXTURE_1D
                self.src_format = gl.GL_ALPHA
                self.dst_format = gl.GL_ALPHA16
            elif shape[1] == 2 and format in [None, 'LA']:
                self._target = gl.GL_TEXTURE_1D
                self.src_format = gl.GL_LUMINANCE_ALPHA
                self.dst_format = gl.GL_LUMINANCE16_ALPHA16
            elif shape[1] == 3 and format in [None, 'RGB']:
                self._target = gl.GL_TEXTURE_1D
                self.src_format = gl.GL_RGB
                self.dst_format = gl.GL_RGB16
            elif shape[1] == 4 and format in [None, 'RGBA']:
                self._target = gl.GL_TEXTURE_1D
                self.src_format = gl.GL_RGBA
                self.dst_format = gl.GL_RGBA16
            elif format in [None, 'RGBA']:
                self._target = gl.GL_TEXTURE_2D
                self.src_format = gl.GL_ALPHA
                self.dst_format = gl.GL_ALPHA16
            else:
                raise TextureException(
                    'Array shape %s not compatible with any texture format'
                    % str(shape))
        elif len(shape) == 3:
            self._target = gl.GL_TEXTURE_2D
            if shape[2] == 1 and format in [None, 'A']:
                self.src_format = gl.GL_ALPHA
                self.dst_format = gl.GL_ALPHA16
            elif shape[2] == 2 and format in [None, 'LA']:
                self.src_format = gl.GL_LUMINANCE_ALPHA
                self.dst_format = gl.GL_LUMINANCE16_ALPHA16
            elif shape[2] == 3 and format in [None, 'RGB']:
                self.src_format = gl.GL_RGB
                self.dst_format = gl.GL_RGB16
            elif shape[2] == 4 and format in [None, 'RGBA']:
                self.src_format = gl.GL_RGBA
                self.dst_format = gl.GL_RGBA16
            else:
                raise TextureException(
                    'Array shape %s not compatible with any texture format'
                    % str(shape))

        # Build texture
        if self.target == gl.GL_TEXTURE_2D:
            width, height = shape[1], shape[0]
        else:
            width, height = shape[0], 0            
        self._width = width
        self._height = height

        if self._id:
            #gl.glDeleteTextures(1, gl.byref(self._id))
            gl.glDeleteTextures([self._id])
        #id = gl.GLuint()
        #gl.glGenTextures(1, gl.byref(id))
        self._id = gl.glGenTextures(1)
        gl.glPixelStorei (gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glPixelStorei (gl.GL_PACK_ALIGNMENT, 1)
        gl.glBindTexture (self.target, self.id)
        gl.glTexParameterf (self.target,
                            gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf (self.target,
                            gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf (self.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameterf (self.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        if self._target == gl.GL_TEXTURE_1D:
            gl.glTexImage1D (self.target, 0, self.dst_format, width, 0,
                             self.src_format, self.src_type, numpy.zeros(Z.shape,Z.dtype))
        else:
            gl.glTexImage2D (self.target, 0, self.dst_format, width, height, 0,
                             self.src_format, self.src_type, numpy.zeros(Z.shape,Z.dtype))
        self.update()


    def update(self, bias=0.0, scale=1.0):
        ''' Update texture. '''

        gl.glBindTexture(self.target, self.id)

        # Autoscale array using OpenGL pixel transfer parameters
        if self.target == gl.GL_TEXTURE_2D and self.src_type == gl.GL_FLOAT:
            gl.glPixelTransferf(gl.GL_ALPHA_SCALE, scale)
            gl.glPixelTransferf(gl.GL_ALPHA_BIAS, bias)
        if self.target == gl.GL_TEXTURE_1D:
            gl.glTexSubImage1D (self.target, 0, 0, 
                                self._Z.shape[0],
                                self.src_format,
                                self.src_type,
                                self._Z) #.ctypes.data)
        else:
            gl.glTexSubImage2D (self.target, 0, 0, 0,
                                self._Z.shape[1],
                                self._Z.shape[0],
                                self.src_format,
                                self.src_type,
                                self._Z) #.ctypes.data)
        if self.target == gl.GL_TEXTURE_2D and self.src_type == gl.GL_FLOAT:
           # Default parameters
           gl.glPixelTransferf(gl.GL_ALPHA_SCALE, 1)
           gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 0)
