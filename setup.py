#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from os.path import join
import os
import sys

# The following is more or less random copy/paste from numpy.distutils ...
import setuptools
from distutils.errors import DistutilsError
from numpy.distutils.core import setup
from common import *

def configuration(parent_package='',top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')
    write_info(os.path.join("glumpy", "info.py"))
    write_version(os.path.join("glumpy", "version.py"))
    # XXX: find a way to include the doc in sdist
    if os.path.exists(os.path.join("doc", "src")):
        write_version(os.path.join("doc", "src", "glumpy_version.py"))
    pkg_prefix_dir = 'glumpy'
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None,parent_package,top_path,
        namespace_packages = ['glumpy'],
        version     = build_fverstring(),
        maintainer  = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        url = URL,
        download_url = DOWNLOAD_URL,
        long_description = LONG_DESCRIPTION)
    config.set_options(
            ignore_setup_xxx_py=True,
            assume_default_configuration=True,
            delegate_options_to_subpackages=True,
            quiet=True,
            )
    config.add_subpackage(DISTNAME)
    return config

if __name__ == "__main__":
    # setuptools version of config script
    setup(configuration=configuration,
          name=DISTNAME,
          install_requires=INSTALL_REQUIRE,
          namespace_packages=['glumpy'],
          packages=['glumpy', 'glumpy.atb', 'glumpy.shader'],
          include_package_data = True,
          package_data={'glumpy': ['shader/*.txt']},
          zip_safe=False,
          classifiers=CLASSIFIERS)






# from distutils.core import setup

# setup(name='glumpy',
#       version='beta',
#       description='Fast OpenGL numpy visualization',
#       author='Nicolas P. Rougier',
#       author_email='Nicolas.Rougier@loria.fr',
#       url='http://code.google.com/p/glumpy/',
#       packages=['glumpy',
#                 'glumpy.atb',
#                 'glumpy.shader'],
#       package_data={'glumpy': ['shader/*.txt']},
#      )
