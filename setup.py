#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009,2010,2011  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import os
from distutils.core import setup

from common import *

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')
    write_info(os.path.join("glumpy", "info.py"))
    write_version(os.path.join("glumpy", "version.py"))
    if os.path.exists(os.path.join("doc", "src")):
        write_version(os.path.join("doc", "src", "glumpy_version.py"))

    setup(name=DISTNAME,
          version=build_fverstring(),
          description=DESCRIPTION,
          long_description = LONG_DESCRIPTION,
          maintainer= MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          url=URL,
          download_url=DOWNLOAD_URL,
          license = LICENSE,
          packages=['glumpy', 'glumpy.atb', 'glumpy.shader'],
          package_data={'glumpy': ['shader/*.txt']},
          classifiers=CLASSIFIERS)
