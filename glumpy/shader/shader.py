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
#
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#
''' Base shader class.

    Example:
    --------
    shader = Shader()

    shader.bind()
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(lut.target, lut.id)
    shader.uniformi('lut', 1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(texture.target, texture.id)
    shader.uniformi('texture', 0)
    shader.uniformf('pixel', 1.0/texture.width, 1.0/texture.height)

    texture.blit(x,y,w,h)
    shader.unbind()
'''
import os, sys
import pyglet.gl as gl
import ctypes

class Shader:
    ''' Base shader class. '''

    def __init__(self, vert = [], frag = [], geom = [], name=''):
        ''' vert, frag and geom take arrays of source strings
            the arrays will be concatenated into one string by OpenGL.'''

        self.uniforms = {}
        self.name = name
        # create the program handle
        self.handle = gl.glCreateProgram()
        # we are not linked yet
        self.linked = False
        # create the vertex shader
        self._build_shader(vert, gl.GL_VERTEX_SHADER)
        # create the fragment shader
        self._build_shader(frag, gl.GL_FRAGMENT_SHADER)
        # the geometry shader will be the same, once pyglet supports the extension
        # self.createShader(frag, GL_GEOMETRY_SHADER_EXT)
        # attempt to link the program
        self._link()

    def _build_shader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = gl.glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (ctypes.c_char_p * count)(*strings)
        gl.glShaderSource(shader, count,
                          ctypes.cast(ctypes.pointer(src),
                                      ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), None)

        # compile the shader
        gl.glCompileShader(shader)

        temp = ctypes.c_int(0)
        # retrieve the compile status
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(temp))

        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(temp))
            # create a buffer for the log
            buffer = ctypes.create_string_buffer(temp.value)
            # retrieve the log text
            gl.glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            print buffer.value
        else:
            # all is well, so attach the shader to the program
            gl.glAttachShader(self.handle, shader);

    def _link(self):
        ''' Link the program '''

        gl.glLinkProgram(self.handle)
        # retrieve the link status
        temp = ctypes.c_int(0)
        gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS, ctypes.byref(temp))

        # if linking failed, print the log
        if not temp:
            # retrieve the log length
            gl.glGetProgramiv(self.handle, gl.GL_INFO_LOG_LENGTH, ctypes.byref(temp))
            # create a buffer for the log
            buffer = ctypes.create_string_buffer(temp.value)
            # retrieve the log text
            gl.glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            print buffer.value
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        ''' Bind the program, i.e. use it. '''
        gl.glUseProgram(self.handle)

    def unbind(self):
        ''' Unbind whatever program is currently bound - not necessarily this program,
            so this should probably be a class method instead. '''
        gl.glUseProgram(0)

    def uniformf(self, name, *vals):
        ''' Uploads float uniform(s), program must be currently bound. '''

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc

        # Check there are 1-4 values
        if len(vals) in range(1, 5):
            # Select the correct function
            { 1 : gl.glUniform1f,
              2 : gl.glUniform2f,
              3 : gl.glUniform3f,
              4 : gl.glUniform4f
              # Retrieve uniform location, and set it
            }[len(vals)](loc, *vals)

    def uniformi(self, name, *vals):
        ''' Upload integer uniform(s), program must be currently bound. '''

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc

        # Checks there are 1-4 values
        if len(vals) in range(1, 5):
            # Selects the correct function
            { 1 : gl.glUniform1i,
              2 : gl.glUniform2i,
              3 : gl.glUniform3i,
              4 : gl.glUniform4i
              # Retrieves uniform location, and set it
            }[len(vals)](loc, *vals)

    def uniform_matrixf(self, name, mat):
        ''' Upload uniform matrix, program must be currently bound. '''

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        self.uniforms[name] = loc

        # Upload the 4x4 floating point matrix
        gl.glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))



def read_shader(filename):
    ''' Read a file from within the shader directory and return content '''
    
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname,filename)
    file = open(path)
    buffer = file.read()
    file.close()
    return buffer
