#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright INRIA
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
#
# GLUMPY is an OpenGL framework for the vizualization of numpy arrays.
#
# This software is governed by the CeCILL license under French law and abiding
# by the rules of distribution of free software. You can use, modify and/ or
# redistribute the software under the terms of the CeCILL license as circulated
# by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info/index.en.html.
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean that
# it is complicated to manipulate, and that also therefore means that it is
# reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# -----------------------------------------------------------------------------
''' Font class '''
import os
import sys
import math
import numpy as np
import OpenGL.GL as gl
from freetype import *


cached_fonts = {}



class Atlas:
    '''
    Group multiple small data regions into a larger texture.

    The algorithm is based on the article by Jukka Jylänki : "A Thousand Ways
    to Pack the Bin - A Practical Approach to Two-Dimensional Rectangle Bin
    Packing", February 27, 2010. More precisely, this is an implementation of
    the Skyline Bottom-Left algorithm based on C++ sources provided by Jukka
    Jylänki at: http://clb.demon.fi/files/RectangleBinPack/

    Example usage:
    --------------

    atlas = Atlas(512,512,3)
    region = atlas.get_region(20,20)
    ...
    atlas.set_region(region, data)
    '''

    def __init__(self, width=1024, height=1024, depth=1):
        '''
        Initialize a new atlas of given size.

        Parameters
        ----------

        width : int
            Width of the underlying texture

        height : int
            Height of the underlying texture

        depth : 1 or 3
            Depth of the underlying texture
        '''
        self.width  = int(math.pow(2, int(math.log(width, 2) + 0.5)))
        self.height = int(math.pow(2, int(math.log(height, 2) + 0.5)))
        self.depth  = depth
        self.nodes  = [ (0,0,self.width), ]
        self.data   = np.zeros((self.height, self.width, self.depth),
                               dtype=np.ubyte)
        self.texid  = 0
        self.used   = 0



    def upload(self):
        '''
        Upload atlas data into video memory.
        '''

        if not self.texid:
            self.texid = gl.glGenTextures(1)

        gl.glBindTexture( gl.GL_TEXTURE_2D, self.texid )
        gl.glTexParameteri( gl.GL_TEXTURE_2D,
                            gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP )
        gl.glTexParameteri( gl.GL_TEXTURE_2D,
                            gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP )
        gl.glTexParameteri( gl.GL_TEXTURE_2D,
                            gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR )
        gl.glTexParameteri( gl.GL_TEXTURE_2D,
                            gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR )
        if self.depth == 1:
            gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_ALPHA,
                             self.width, self.height, 0,
                             gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, self.data )
        else:
            gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGB,
                             self.width, self.height, 0,
                             gl.GL_RGB, gl.GL_UNSIGNED_BYTE, self.data )



    def set_region(self, region, data):
        '''
        Set a given region width provided data.

        Parameters
        ----------

        region : (int,int,int,int)
            an allocated region (x,y,width,height)

        data : numpy array
            data to be copied into given region
        '''

        x, y, width, height = region
        self.data[y:y+height,x:x+width, :] = data



    def get_region(self, width, height):
        '''
        Get a free region of given size and allocate it

        Parameters
        ----------

        width : int
            Width of region to allocate

        height : int
            Height of region to allocate

        Return
        ------
            A newly allocated region as (x,y,width,height) or (-1,-1,0,0)
        '''

        best_height = sys.maxint
        best_index = -1
        best_width = sys.maxint
        region = 0, 0, width, height

        for i in range(len(self.nodes)):
            y = self.fit(i, width, height)
            if y >= 0:
                node = self.nodes[i]
                if (y+height < best_height or
                    (y+height == best_height and node[2] < best_width)):
                    best_height = y+height
                    best_index = i
                    best_width = node[2]
                    region = node[0], y, width, height

        if best_index == -1:
            return -1,-1,0,0

        node = region[0], region[1]+height, width
        self.nodes.insert(best_index, node)

        i = best_index+1
        while i < len(self.nodes):
            node = self.nodes[i]
            prev_node = self.nodes[i-1]
            if node[0] < prev_node[0]+prev_node[2]:
                shrink = prev_node[0]+prev_node[2] - node[0]
                x,y,w = self.nodes[i]
                self.nodes[i] = x+shrink, y, w-shrink
                if self.nodes[i][2] <= 0:
                    del self.nodes[i]
                    i -= 1
                else:
                    break
            else:
                break
            i += 1

        self.merge()
        self.used += width*height
        return region



    def fit(self, index, width, height):
        '''
        Test if region (width,height) fit into self.nodes[index]

        Parameters
        ----------

        index : int
            Index of the internal node to be tested

        width : int
            Width or the region to be tested

        height : int
            Height or the region to be tested

        '''

        node = self.nodes[index]
        x,y = node[0], node[1]
        width_left = width        
        
        if x+width > self.width:
            return -1

        i = index
        while width_left > 0:
            node = self.nodes[i]
            y = max(y, node[1])
            if y+height > self.height:
                return -1
            width_left -= node[2]
            i += 1
        return y



    def merge(self):
        '''
        Merge nodes
        '''

        i = 0
        while i < len(self.nodes)-1:
            node = self.nodes[i]
            next_node = self.nodes[i+1]
            if node[1] == next_node[1]:
                self.nodes[i] = node[0], node[1], node[2]+next_node[2]
                del self.nodes[i+1]
            else:
                i += 1


class Font:
    '''
    A Font gathers a set of glyph relatively to a given font filename
    and size.
    '''

    atlas = None
    fonts = {}

    def __init__(self, filename, size):
        '''
        Initialize font

        Parameters:
        -----------

        atlas: Atlas
            Atlas where glyph will be stored

        filename: str
            Font filename
        
        size : float
            Font size
        '''

        if Font.atlas == None:
            Font.atlas = Atlas(512, 512, 1)

        self.filename = filename
        self.size = size
        self.glyphs = {}
        face = Face( self.filename )
        face.set_char_size( int(self.size*64))
        self._dirty = True
        metrics = face.size
        self.ascender  = metrics.ascender/64.0
        self.descender = metrics.descender/64.0
        self.height    = metrics.height/64.0
        self.linegap   = self.height - self.ascender + self.descender
        self.depth     = Font.atlas.depth
        set_lcd_filter(FT_LCD_FILTER_LIGHT)


    def __getitem__(self, charcode):
        '''
        x.__getitem__(y) <==> x[y]
        '''
        if charcode not in self.glyphs.keys():
            self.load('%c' % charcode)
        return self.glyphs[charcode]



    def _get_texid(self):
        ''' Get underlying texture identity. '''
        if self._dirty:
            Font.atlas.upload()
        self._dirty = False
        return Font.atlas.texid
    texid = property(_get_texid,
                     doc='''Underlying texture identity.''')


 
    def load(self, charcodes = ''):
        '''
        Build glyphs corresponding to individual characters in charcodes.

        Parameters:
        -----------
        
        charcodes: [str | unicode]
            Set of characters to be represented
        '''
        face = Face( self.filename )
        pen = Vector(0,0)
        hres = 16*72
        hscale = 1.0/16
        face.set_char_size( int(self.size * 64), 0, hres, 72 )
        matrix = Matrix( int((hscale) * 0x10000L), int((0.0) * 0x10000L),
                         int((0.0)    * 0x10000L), int((1.0) * 0x10000L) )

        for charcode in charcodes:
            face.set_transform( matrix, pen )
            if charcode in self.glyphs.keys():
                continue
            self._dirty = True
            flags = FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT
            if self.depth == 3:
                flags |= FT_LOAD_TARGET_LCD

            face.load_char( charcode, flags )
            bitmap = face.glyph.bitmap
            left   = face.glyph.bitmap_left
            top    = face.glyph.bitmap_top
            width  = face.glyph.bitmap.width
            rows   = face.glyph.bitmap.rows
            pitch  = face.glyph.bitmap.pitch

            atlas = Font.atlas
            x,y,w,h = atlas.get_region(width/self.depth+2, rows+2)
            if x < 0:
                print 'Missed !'
                continue
            x,y = x+1, y+1
            w,h = w-2, h-2
            data = []
            for i in range(rows):
                data.extend(bitmap.buffer[i*pitch:i*pitch+width])
            data = np.array(data,dtype=np.ubyte).reshape(h,w,self.depth)
            gamma = 1.25
            Z = ((data/255.0)**(gamma))
            data = (Z*255).astype(np.ubyte)
            atlas.set_region((x,y,w,h), data)

            # Build glyph
            size   = w,h
            offset = left, top
            advance= face.glyph.advance.x, face.glyph.advance.y

            u0     = (x +     0.0)/float(atlas.width)
            v0     = (y +     0.0)/float(atlas.height)
            u1     = (x + w - 0.0)/float(atlas.width)
            v1     = (y + h - 0.0)/float(atlas.height)
            texcoords = (u0,v0,u1,v1)
            glyph = Glyph(charcode, size, offset, advance, texcoords)
            self.glyphs[charcode] = glyph

            # Generate kerning
            for g in self.glyphs.values():
                kerning = face.get_kerning(g.charcode, charcode, mode=FT_KERNING_UNSCALED)
                if kerning.x != 0:
                    glyph.kerning[g.charcode] = kerning.x
                kerning = face.get_kerning(charcode, g.charcode, mode=FT_KERNING_UNSCALED)
                if kerning.x != 0:
                    g.kerning[charcode] = kerning.x



class Glyph:
    '''
    A glyph gathers information relative to the size/offset/advance and texture
    coordinates of a single character. It is generally built automatically by a
    Font.
    '''

    def __init__(self, charcode, size, offset, advance, texcoords):
        '''
        Build a new texture glyph

        Parameter:
        ----------

        charcode : char
            Represented character

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance

        texcoords: tuple of 4 floats
            Texture coordinates of bottom-left and top-right corner
        '''
        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance
        self.texcoords = texcoords
        self.kerning = {}


    def get_kerning(self, charcode):
        ''' Get kerning information

        Parameters:
        -----------

        charcode: char
            Character preceding this glyph
        '''
        if charcode in self.kerning.keys():
            return self.kerning[charcode]
        else:
            return 0



def get_font(filename, size):
    ''' Get a font described by filename and size'''
    key = '%s-%d' % (os.path.basename(filename), size)
    if key in cached_fonts.keys():
            return cached_fonts[key]
    font = Font(filename, size)
    cached_fonts[key] = font
    return font

