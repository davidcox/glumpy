#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
descr = '''
glumpy is  a small python library  for the rapid vizualization  of numpy arrays
(mainly two dimensional) that has  been designed with efficiency in mind, using
OpenGL. If you want to draw nice figures for inclusion in a scientific article,
you'd better use matplotlib. If you want  to have a sense of what's going on in
your simulation while it is running, then maybe glumpy can help you.
'''

DISTNAME            = 'glumpy'
DESCRIPTION         = 'A python module for fast visualization of numpy arrays using OpenGL'
LONG_DESCRIPTION    = descr
MAINTAINER          = 'Nicolas P. Rougier'
MAINTAINER_EMAIL    = 'Nicolas.Rougier@loria.fr'
URL                 = 'http://code.google.com/p/glumpy/'
LICENSE             = 'BSD'
DOWNLOAD_URL        = 'http://pypi.python.org/pypi/glumpy'

MAJOR = 0
MINOR = 1
MICRO = 3
DEV = False

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Environment :: MacOS X',
               'Environment :: X11 Applications',
               'Intended Audience :: Developers',
               'Intended Audience :: Science/Research',
               'License :: OSI Approved :: BSD License',
               'Topic :: Multimedia :: Sound/Audio',
               'Topic :: Scientific/Engineering']

def build_verstring():
    return '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def build_fverstring():
    if DEV:
        return build_verstring() + '.dev'
    else:
        return build_verstring()

def write_version(fname):
    f = open(fname, "w")
    f.writelines("short_version = '%s'\n" % build_verstring())
    f.writelines("dev = %s\n" % DEV)
    f.writelines("version = '%s'\n" % build_fverstring())
    f.close()

def write_info(fname):
    f = open(fname, "w")
    f.writelines("# THIS FILE IS GENERATED FROM THE SETUP.PY. DO NOT EDIT.\n")
    f.writelines('"""%s"""' % descr)
    f.close()

VERSION = build_fverstring()
INSTALL_REQUIRE = ['numpy','PyOpenGL']
