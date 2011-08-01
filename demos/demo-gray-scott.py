#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright INRIA
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
#
# DANA is a computing framework for the simulation of distributed,
# asynchronous, numerical and adaptive models.
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
'''
Reaction Diffusion : Gray-Scott model

References:
----------
Complex Patterns in a Simple System
John E. Pearson, Science 261, 5118, 189-192, 1993.
'''
from dana import *
import glumpy

n  = 150
dt = .1*second
t  = 5000*second

# Parameters from http://www.aliensaint.com/uo/java/rd/
# -----------------------------------------------------
# Du, Dv, F, k = 0.16, 0.08, 0.035, 0.065 # Bacteria 1
# Du, Dv, F, k = 0.14, 0.06, 0.035, 0.065 # Bacteria 2
# Du, Dv, F, k = 0.16, 0.08, 0.060, 0.062 # Coral
# Du, Dv, F, k = 0.19, 0.05, 0.060, 0.062 # Fingerprint
# Du, Dv, F, k = 0.10, 0.10, 0.018, 0.050 # Spirals
# Du, Dv, F, k = 0.12, 0.08, 0.020, 0.050 # Spirals Dense
# Du, Dv, F, k = 0.10, 0.16, 0.020, 0.050 # Spirals Fast
Du, Dv, F, k = 0.16, 0.08, 0.020, 0.055 # Unstable
# Du, Dv, F, k = 0.16, 0.08, 0.050, 0.065 # Worms 1
# Du, Dv, F, k = 0.16, 0.08, 0.054, 0.063 # Worms 2
# Du, Dv, F, k = 0.16, 0.08, 0.035, 0.060 # Zebrafish


Z = Group((n,n), '''du/dt = Du*Lu - Z + F*(1-U) : float32
                    dv/dt = Dv*Lv + Z - (F+k)*V : float32
                    U = maximum(u,0) : float32
                    V = maximum(v,0) : float32
                    Z = U*V*V : float32
                    Lu; Lv; ''')
K = np.array([[np.NaN,  1., np.NaN], 
              [  1.,   -4.,   1.  ],
              [np.NaN,  1., np.NaN]])
SparseConnection(Z('U'),Z('Lu'), K, toric=True)
SparseConnection(Z('V'),Z('Lv'), K, toric=True)

Z['u'] = 1.0
Z['v'] = 0.0
r = 20
Z['u'][n/2-r:n/2+r,n/2-r:n/2+r] = 0.50
Z['v'][n/2-r:n/2+r,n/2-r:n/2+r] = 0.25
Z['u'] += 0.05*np.random.random((n,n))
Z['v'] += 0.05*np.random.random((n,n))
Z['U'] = Z['u']
Z['V'] = Z['v']

cmap = glumpy.colormap.Colormap("blue",
                                (0.00, (0.2, 0.2, 1.0)),
                                (1.00, (1.0, 1.0, 1.0)))
Zu = glumpy.Image(Z['u'], interpolation='bicubic', cmap=cmap)
window = glumpy.Window(512,512)

@window.event
def on_mouse_drag(x, y, dx, dy, button):
    global Z, n
    center =( int((1-y/float(window.width)) * (n-1)),
              int(   x/float(window.height) * (n-1)) )
    def distance(x,y):
        return np.sqrt((x-center[0])**2+(y-center[1])**2)
    D = np.fromfunction(distance,(n,n))
    M = np.where(D<=5,True,False).astype(np.float32)
    Z['U'] = Z['u'] = (1-M)*Z['u'] + M*0.50
    Z['V'] = Z['v'] = (1-M)*Z['v'] + M*0.25
    Zu.update()

@window.event
def on_draw():
   Zu.blit(0,0,window.width,window.height)

@window.event
def on_idle(*args):
    for i in range(10):
        Z.propagate()
        Z.evaluate(dt=dt)
        Z.update()
    Zu.update()
    window.draw()
window.mainloop()
