#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Nicolas Rougier - INRIA - CORTEX Project
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either  version 3 of the  License, or (at your  option)
# any later version.
# 
# This program is  distributed in the hope that it will  be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR  A  PARTICULAR PURPOSE.  See  the GNU  General  Public 
# License for  more details.
# 
# You should have received a copy  of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
# 
# Contact:  CORTEX Project - INRIA
#           INRIA Lorraine, 
#           Campus Scientifique, BP 239
#           54506 VANDOEUVRE-LES-NANCY CEDEX 
#           FRANCE
''' Numerical integration of dynamic neural fields.

This script implements the numerical integration of dynamic neural fields [1]_
of the form:
                  
1 ∂U(x,t)             ⌠+∞ 
- ------- = -U(x,t) + ⎮  w(|x-y|).f(U(y,t)).dy + I(x,t) + h
α   ∂t                ⌡-∞ 

where U(x,t) is the potential of a neural population at position x and time t
      W(d) is a neighborhood function from ℝ⁺ → ℝ
      f(u) is the firing rate of a single neuron from ℝ → ℝ
      I(x,t) is the input at position x and time t
      h is the resting potential
      α is the temporal decay of the synapse

:References:
    _[1] http://www.scholarpedia.org/article/Neural_fields
'''
import glumpy
import numpy as np
import scipy.linalg


def fromdistance(fn, shape, center=None, dtype=float):
    '''Construct an array by executing a function over a normalized distance.
    
    The resulting array therefore has a value
    ``fn(sqrt((x-x0)²+(y-y0)²))`` at coordinate  ``(x,y)`` where x,y ∈ [-1,+1]²
    
    Parameters
    ----------
    fn : callable
        The function is called with one parameter representing the normalized
        distance. `fn` must be capable of operating on arrays, and should
        return a scalar value.
    shape : (N,) tuple of ints
        Shape of the output array, which also determines the shape of
        the coordinate arrays passed to `fn`.
    dtype : data-type, optional
        Data-type of the coordinate arrays passed to `fn`.  By default,
        `dtype` is float.
    '''
    def distance(*args):
        d = 0
        for i in range(len(shape)):
            d += (2*args[i]/float(shape[i]-1)-1 -center[i])**2
        return np.sqrt(d) #/np.sqrt(len(shape))
    if center == None:
        center = [0.,]*len(shape)
    return fn(np.fromfunction(distance,shape,dtype=dtype))


def convolve1d( Z, K ):
    ''' Discrete, clamped, linear convolution of two one-dimensional sequences.

        :Parameters:
            Z : (N,) array_like
                First one-dimensional input array (input).
            K : (M,) array_like
                Second one-dimensional input array (kernel).

        :Returns:
            out : array
                Discrete, clamped, linear convolution of `Z` and `K`.
    '''
    R = np.convolve(Z, K, 'same')
    i0 = 0
    if R.shape[0] > Z.shape[0]:
        i0 = (R.shape[0]-Z.shape[0])/2 + 1 - Z.shape[0]%2
    i1 = i0+ Z.shape[0]
    return R[i0:i1]


def convolve2d(Z, K, USV = None):
    ''' Discrete, clamped convolution of two two-dimensional arrays.
   
        :Parameters:
            Z : (N1,N2) array_like
                First two-dimensional input array (input)
            K : (M1,M2) array_like
                Second two-dimensional input array (kernel)

        :*Returns:
           out : ndarray
                Discrete, clamped, linear convolution of `Z` and `K`
    '''
    epsilon = 1e-9
    if USV is None:
        U,S,V = scipy.linalg.svd(K)
        U,S,V = U.astype(K.dtype), S.astype(K.dtype), V.astype(K.dtype)
    else:
        U,S,V = USV
    n = (S > epsilon).sum()
    R = np.zeros( Z.shape )
    for k in range(n):
        Zt = Z.copy() * S[k]
        for i in range(Zt.shape[0]):
            Zt[i,:] = convolve1d(Zt[i,:], V[k,::-1])
        for i in range(Zt.shape[1]):
            Zt[:,i] = convolve1d(Zt[:,i], U[::-1,k])
        R += Zt
    return R



if __name__ == '__main__':

    #  Parameters
    n       = 40
    dt      = 0.05
    alpha   = 12.0
    tau     = 0.25
    h       = 0.0
    s       = (n*n)/(40.*40.)
    noise   = 0.01
    theta   = 0
    dtheta  = 0.025
    rho     = 0.75
    n_stims = 3
    u = (dt/tau)/alpha

    def f(x):
        return np.maximum(x,0)
    def g(x, width=0.1):
        return np.exp(-(x/width)**2/2)
    def w(x):
        return 1.0*g(x,0.1)-0.5*g(x,1.0)
    def stimulus(shape,center,width):
        def g2(x) : return g(x,width)
        return fromdistance(g2,shape,center)


    #  Initialization
    I = np.zeros((n,n),dtype=np.float32)  # input
    Z = np.zeros((n,n), dtype=np.float32)  # output
    Z_ = np.zeros((n,n), dtype=np.float32) # membrane potential

    # Kernel
    K = fromdistance(w,(2*n+1,2*n+1))
    USV = scipy.linalg.svd(K)

    # Output decoding
    X,Y = np.mgrid[0:n,0:n]
    X = 2*X/float(n-1) - 1
    Y = 2*Y/float(n-1) - 1



    window = glumpy.Window(2*512, 512)
    Ii = glumpy.Image(I, interpolation='bicubic',
                      cmap=glumpy.colormap.Grey_r, vmin=0.0, vmax=2.5)
    Zi = glumpy.Image(Z, interpolation='bicubic',
                      cmap=glumpy.colormap.Grey_r, vmin=0.0, vmax=0.25)

    @window.event
    def on_draw():
        global Zi, Ii
        window.clear()
        Ii.blit(0,0,512,512)
        Zi.blit(512,0,512,512)


    @window.event
    def on_key_press(key, modifiers):
        global Z
        if key == glumpy.key.SPACE:
            Z[...] = 0
            Z_[...] = 0

    @window.event
    def on_idle(*args):
        global I, Z, Z_, Ii, Zi, dt, n, h, s, tau, alpha, theta, dtheta, rho, u

        theta += dtheta
        I[...] = np.zeros((n,n))
        for j in range(n_stims):
            t = theta+ j*2*np.pi/n_stims
            x,y = rho*np.cos(t),rho*np.sin(t)
            I += 2.5*stimulus((n,n), (x,y), 0.1)
        I += (2*np.random.random((n,n))-1)*noise

        # Compute field activity
        for i in range(1):
            L = convolve2d(Z,K,USV)/s
            Z_ *= (1-tau)
            L += I
            L *= u
            Z_ += L
            #Z_[...] = np.minimum(np.maximum(Z_,0),1)
            Z[...] = f(Z_)

        Zi.update()
        Ii.update()
        window.draw()
        
    window.mainloop()


