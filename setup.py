#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup file for the IRIS package.

This file contains multiple package setups:
iris_packagedb and iris_submissions require their plugins (eggs)
to be set up with unique names to be pluggable to the core app.
Hence they are set up with differing names and produce
iris_packagedb.egg-info and iris_submissions.egg-info folders,
respectively, to broadcast their existence to the core app.

Apart from this egg setup, they build from the same binary
as the core application does, and come plugged only when
their plugins are registered under the [iris.app] entrypoint.

This convenience is for RPM packaging purposes and to avoid
setting up multiple setup.py files doing essentially the same thing.
"""

from os import path, pardir, chdir
from setuptools import setup, find_packages


def get_version():
    """Get version from the spec file"""
    filename = path.join(path.dirname(__file__), 'packaging', 'iris.spec')
    with open(filename, 'r') as spec:
        for line in spec.readlines():
            if line.lower().startswith('version:'):
                return line.split(':', 1)[1].strip()
    raise Exception('ERROR: unable to parse version from spec file')


# Allow setup.py to be run from any path:
chdir(path.normpath(path.join(path.abspath(__file__), pardir)))
README = open(path.join(path.dirname(__file__), 'README')).read()
VERSION = get_version()

# Core package project setup
setup(
    url='https://otctools.jf.intel.com/pm/projects/iris',
    name='iris',
    version=VERSION,
    namespace_packages=['iris'],
    packages=find_packages(),
    include_package_data=True,
    license='GPL-2.0',
    description='IRIS - Infrastructure and Release Engineering Service',
    long_description=README,
    author='Aleksi Hakli',
    author_email='aleksi.hakli@intel.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Admistrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    scripts=[
        'bin/generate_django_secret_key.py',
        'bin/import_scm.py',
    ],
)

# Package Database plugin setup
setup(
    url='https://otctools.jf.intel.com/pm/projects/iris',
    name='iris_packagedb',
    version=VERSION,
    namespace_packages=['iris'],
    packages=['iris.packagedb'],
    include_package_data=True,
    entry_points="""
        [iris.app]
        packagedb=iris.packagedb.plugin:APPINFO
    """,
    license='GPL-2.0',
    description='IRIS Package Database plugin',
)

# Submissions plugin setup
setup(
    url='https://otctools.jf.intel.com/pm/projects/iris',
    name='iris_submissions',
    version=VERSION,
    namespace_packages=['iris'],
    packages=['iris.submissions'],
    include_package_data=True,
    entry_points="""
        [iris.app]
        submissions=iris.submissions.plugin:APPINFO
    """,
    license='GPL-2.0',
    description='IRIS Submissions plugin',
)
