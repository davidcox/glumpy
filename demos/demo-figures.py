#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
'''
This example demonstrates subfigure usage.
'''
from glumpy import figure, show

fig   = figure(size=(600,600))
fig1  = fig.add_figure(cols=2,rows=2, position=[0,0], size=[2,1])
fig2  = fig.add_figure(cols=2,rows=2, position=[0,1], size=[1,1])
fig3  = fig.add_figure(cols=2,rows=2, position=[1,1], size=[1,1])
fig31 = fig3.add_figure(cols=2,rows=2, position=[0,0], size=[1,1])
fig32 = fig3.add_figure(cols=2,rows=2, position=[0,1], size=[1,1])
fig33 = fig3.add_figure(cols=2,rows=2, position=[1,0], size=[1,2])

@fig1.event
def on_draw(): fig1.clear(1,0,0,1)

@fig2.event
def on_draw(): fig2.clear(0,1,0,1)

@fig31.event
def on_draw(): fig31.clear(0,0,1,1)

@fig32.event
def on_draw(): fig32.clear(0,0,0,1)

@fig33.event
def on_draw(): fig33.clear(1,1,1,1)

show()
