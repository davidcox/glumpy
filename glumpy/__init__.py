#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from proxy import Proxy
from color import Color
from image import Image
from window import Window, active_window
from layout import layout
from texture import Texture
from trackball import Trackball
import colormap

try:
    import pylab
except:
    pass
try:
    import atb
except:
    pass
