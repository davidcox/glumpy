#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from PIL import Image
import numpy, glumpy
import OpenGL.GL as gl
import OpenGL.GLUT as glut

def cartesian(rho, theta):
    ''' Polar to cartesian coordinates. '''
    x = rho*numpy.cos(theta)
    y = rho*numpy.sin(theta)
    return x,y

def logpolar(rho, theta):
    ''' Polar to logpolar coordinates. '''
    A = 3.0  # Shift in the SC mapping function in deg 
    Bx = 1.4 # Collicular magnification along u axe in mm/rad 
    By = 1.8 # Collicular magnification along v axe in mm/rad 
    xmin, xmax = 0.0, 4.80743279742
    ymin, ymax = -2.76745559565, 2.76745559565
    rho = rho*90.0
    x = Bx*numpy.log(numpy.sqrt(rho*rho+2*A*rho*numpy.cos(theta)+A*A)/A)
    y = By*numpy.arctan(rho*numpy.sin(theta)/(rho*numpy.cos(theta)+A))
    x = (x-xmin)/(xmax-xmin)
    y = (y-ymin)/(ymax-ymin)
    return x,y


def retinotopy(Rs,Ps):
    ''' '''
    s = 4
    rho = ((numpy.logspace(start=0, stop=1, num=s*Rs[1],base=10)-1)/9.)
    theta = numpy.linspace(start=-numpy.pi/2,stop=numpy.pi/2, num=s*Rs[0])
    rho = rho.reshape((s*Rs[1],1))
    rho = numpy.repeat(rho,s*Rs[0], axis=1)
    theta = theta.reshape((1,s*Rs[0]))
    theta = numpy.repeat(theta,s*Rs[1], axis=0)
    y,x = cartesian(rho,theta)
    a,b = x.min(), x.max()
    x = (x-a)/(b-a)
    a,b = y.min(), y.max()
    y = (y-a)/(b-a)

    Px = numpy.ones(Ps, dtype=int)*0
    Py = numpy.ones(Ps, dtype=int)*0

    xi = (x*(Rs[0]-1)).astype(int)
    yi = ((0.5+0.5*y)*(Rs[1]-1)).astype(int)
    yc,xc = logpolar(rho,theta)
    a,b = xc.min(), xc.max()
    xc = (xc-a)/(b-a)
    a,b = yc.min(), yc.max()
    yc = (yc-a)/(b-a)
    xc = (xc*(Ps[0]-1)).astype(int)
    yc = ((.5+yc*0.5)*(Ps[1]-1)).astype(int)
    Px[xc,yc] = xi
    Py[xc,yc] = yi

    xi = (x*(Rs[0]-1)).astype(int)
    yi = ((0.5-0.5*y)*(Rs[1]-1)).astype(int)
    yc,xc = logpolar(rho,theta)
    a,b = xc.min(), xc.max()
    xc = (xc-a)/(b-a)
    a,b = yc.min(), yc.max()
    yc = (yc-a)/(b-a)
    xc = (xc*(Ps[0]-1)).astype(int)
    yc = (((1-yc)*0.5)*(Ps[1]-1)).astype(int)
    Px[xc,yc] = xi
    Py[xc,yc] = yi

    return Px, Py

def square(x,y,width,height):
    gl.glColor4f(1,1,1,.5)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2i(x,y)
    gl.glVertex2i(x+width,y)
    gl.glVertex2i(x+width,y+height)
    gl.glVertex2i(x,y+height)
    gl.glEnd()
    gl.glColor4f(1,1,1,1)
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex2i(x,y)
    gl.glVertex2i(x+width,y)
    gl.glVertex2i(x+width,y+height)
    gl.glVertex2i(x,y+height)
    gl.glEnd()


# -----------------------------------------------------------------------------
if __name__ == '__main__':

    image = Image.open('lena.png')
    S = numpy.asarray(image, dtype=numpy.float32)/256. # Visual scene
    R = numpy.zeros((256,256,3),dtype=numpy.float32)
    V = numpy.zeros((256,256,3),dtype=numpy.float32)
    Px,Py = retinotopy(R.shape[:2],V.shape[:2])
    X,Y = 0,0

    window = glumpy.Window(S.shape[1]+2*V.shape[1],
                           max(S.shape[0],2*V.shape[0]))
    Si = glumpy.Image(S, cmap=glumpy.colormap.Grey)
    Vi = glumpy.Image(V, cmap=glumpy.colormap.Grey)
    gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_BLEND)

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        global X,Y
        X = min(max(x-V.shape[1]//2,1), S.shape[1]-V.shape[1])
        Y = min(max((window.height-y)-V.shape[0]//2,1), S.shape[0]-V.shape[0])

        r,g,b = S[Y,X]
        S[Y,X] = 0
        V[...] = S[Y+Px,X+Py]
        S[Y,X] = r,g,b
        window.draw()

    @window.event
    def on_draw():
        window.clear()
        gl.glColor4f(1,1,1,1)
        Si.update()
        Vi.update()
        Si.blit(0,0,S.shape[1],S.shape[0])
        Vi.blit(S.shape[1],0,2*V.shape[1], 2*V.shape[0])
        gl.glDisable(gl.GL_TEXTURE_2D)
        square(X,window.height-Y,256,-256)

    window.mainloop()
