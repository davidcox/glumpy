#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from distutils.core import setup

setup(name='glumpy',
      version='beta',
      description='Fast OpenGL numpy visualization',
      author='Nicolas P. Rougier',
      author_email='Nicolas.Rougier@loria.fr',
      url='http://code.google.com/p/glumpy/',
      packages=['glumpy',
                'glumpy.atb',
                'glumpy.shader'],
      package_data={'glumpy': ['shader/*.txt']},
     )
