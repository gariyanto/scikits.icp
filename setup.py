#!/usr/bin/env python

descr = '''Iterative Closest Point (ICP) Algorithm SciKit

Provide the ICP algorithm of point sets and 3D meshes to SciPy
'''

DISTNAME            = 'scikits.icp'
DESCRIPTION         = 'ICP for SciPy'
LONG_DESCRIPTION    = descr
MAINTAINER          = 'Guofu Xiang'
MAINTAINER_EMAIL    = 'gfxiang@gmail.com'
URL                 = 'http://github.com/gx/scikits.icp.git'
LICENSE             = 'GNU GPL'
DOWNLOAD_URL        = URL
VERSION             = '0.1'


import os

import setuptools
from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


def configuration(parent_package='', top_path=None):
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage(DISTNAME)
    return config


if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          version=VERSION,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          download_url=DOWNLOAD_URL,
          long_description=LONG_DESCRIPTION,
          #install_requires='numpy',
          namespace_packages=['scikits'],
          packages=setuptools.find_packages(),
          include_package_data=True,
          zip_safe=False, # some tests need data files
          #zip_safe=True, # the package can run out of an .egg file
          classifiers=[
              'Development Status :: 1 - Planning',
              'Environment :: Console',
              'Intended Audience :: Developers',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GPL License',
              'Topic :: Scientific/Engineering'],
          configuration=configuration)
