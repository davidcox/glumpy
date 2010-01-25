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
'''

  Let A be an array of size (11,11) and B an array of size (5,5):

  [A,B] : +---------+
          |         |
          |         |
          |         | +---+
          |         | |   |
          +---------+ +---+

  [A,(B,11/5.)] : +---------+ +---------+
                  |         | |         |
                  |         | |         |
                  |         | |         |
                  |         | |         |
                  +---------+ +---------+

  [[ A,  B] : +---------+ +---+
   ['|', B]]  |         | |   |
              |         | +---+
              |         | +---+
              |         | |   |
              +---------+ +---+

  [[A,'-'], : +---------+
   [B, B ]]   |         |
              |         |
              |         |
              |         |
              +---------+
              +---+ +---+
              |   | |   |
              +---+ +---+
'''
import numpy


def layout(obj, padding=1, border=(1,1,1,1), origin = 'lower'):
    '''

    Parameters
    ----------
    obj : array | [array, ...] | [[array, ...]]
        Arrays to be layouted
    padding : int
        Space between arrays
    border : int | (int,int) | (int,int,int,int)
        Borders around arrays (vertical,horizontal) or (top,right,bottom,left)
    origin : 'lower' | 'upper'
       Determine layout vertical orientation


    Returns
    -------
    overall shape as a tuple of float and a list of arrays with
    their associated layout
    '''
    
    shape, items = (0,0), []
    if type(border) is int:
        border = (border,border,border,border)
    elif type(border) is tuple and len(border) == 2:
        h,v = border
        border = (v,h,v,h)

    # Is obj a single array or tuple ?
    #if isinstance(obj,numpy.ndarray) or isinstance(obj,tuple):
    if hasattr(obj,'shape') or isinstance(obj,tuple):
        shape = (1,1)
        items.append ([obj, (0,0)])

    # Is obj a list ?
    elif isinstance(obj, list):
        s = [item for item in obj if isinstance(item,list)]

        # Is obj a list of list ? No
        if not s:
            shape = (1,len(obj))
            for i in range (len(obj)):
                items.append([obj[i],(0,i)])
        # Is obj a list of list ? Yes
        else:
            shape = (len(obj), max(len(item) for item in s))
            for i in range (len(obj)):
                if isinstance(obj[i],list):
                    for j in range(len(obj[i])):
                        items.append([obj[i][j],(i,j)])
                else:
                    items.append([obj[i],(i,0)])

    # Create a 'meta' array with items at the right place
    Z = numpy.ndarray(shape=shape,dtype=object)
    Z[...] = None

    for z, index in items:
        if isinstance(z, tuple):
            #if isinstance (z[0], numpy.ndarray):
            #    Z[index] = (numpy.atleast_2d(z[0]),z[1])
            #else:
            Z[index] = (z[0],z[1])
        else:
            #if isinstance (z, numpy.ndarray):
            #    Z[index] = (numpy.atleast_2d(z),1)
            #else:
            Z[index] = (z,1)


    # Computes rows and columns size
    # First pass: we do not take into account array that span several rows
    #             or columns and we do not take care of array with negative zoom
    sizes = [[0]*shape[0], [0]*shape[1]]
    for i in range(shape[0]):
        for j in range(shape[1]):
            if Z[i,j] is None: continue
            z,zoom = Z[i,j]
            #if isinstance (z, numpy.ndarray):
            if hasattr(z, 'shape'):
                # Lines height
                if ((i==(shape[0]-1)) or (Z[i+1,j] is not None and Z[i+1,j][0] != '|')):
                    if (z.shape[0]*zoom+padding) > sizes[0][i]:
                        sizes[0][i] = z.shape[0]*zoom+padding
                # Columns width
                if ((j==(shape[1]-1)) or (Z[i,j+1] is not None and Z[i,j+1][0] != '-')):
                    if (z.shape[1]*zoom+padding) > sizes[1][j]:
                        sizes[1][j] = z.shape[1]*zoom+padding

    # Computes rows and columns 
    # Second pass: we only take into account array that span several rows
    # or columns
    for i in range(shape[0]):
        for j in range(shape[1]):
            if Z[i,j] is None:
                continue
            z,zoom = Z[i,j]
            #if isinstance (z, numpy.ndarray):
            if hasattr(z, 'shape'):                       
                # Lines height
                if (i < (shape[0]-1)) and Z[i+1,j] is not None and Z[i+1,j][0] == '|':
                    n = 1
                    for k in range(i+1,Z.shape[0]):
                        if Z[k,j][0] == '|':
                            n += 1
                        else:
                            break
                    s = z.shape[0]*zoom
                    for kk in range(i,k):
                        s = s - sizes[0][kk]
                    sizes[0][k] = max(s+padding, sizes[0][k])
                # Columns width
                if (j < (shape[1]-1)) and Z[i,j+1] is not None and Z[i,j+1][0] == '-':
                    n = 1
                    for k in range(j+1,shape[1]):
                        if Z[i,k][0] == '-':
                            n += 1
                        else:
                            break
                    s = z.shape[1]*zoom
                    for kk in range(j,k):
                        s = s - sizes[1][kk]
                    sizes[1][k] = max(s+padding, sizes[1][k])

    # Compute final position and size
    s0 = float(sum(sizes[1])-padding)
    s1 = float(sum(sizes[0])-padding)
    shape = (s0+border[1]+border[3],s1+border[0]+border[2])
    objects = []
    for i in range(Z.shape[0]):
       for j in range(Z.shape[1]):
            if Z[i,j] is None:
                continue
            z,zoom = Z[i,j]
            #if isinstance (z, numpy.ndarray):
            if hasattr(z, 'shape'):                       
                y = (border[0]+sum(sizes[0][0:i],0) )/shape[1]
                x = (border[1]+sum(sizes[1][0:j],0) )/shape[0]
                h = ( z.shape[0]*zoom )/shape[1]
                w = ( z.shape[1]*zoom )/shape[0]
                if origin == 'lower':
                    y = 1.0 - y - h
                objects.append( (z,x,y,w,h) )

    w,h = shape[0], shape[1]
    if w > h:
        shape = 1,h/w
    else:
        shape = w/h,1
    return shape, objects




