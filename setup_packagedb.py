#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup file for the IRIS package.
"""

from os import path, pardir, chdir
from setuptools import setup, find_packages

# Allow setup.py to be run from any path:
chdir(path.normpath(path.join(path.abspath(__file__), pardir)))

setup(
    url='https://otctools.jf.intel.com/pm/projects/iris',
    name='iris-packagedb',
    version='0.0.2',
    namespace_packages=['iris'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points="""
        [iris.app]
        packagedb=iris.packagedb.plugin:APPINFO
    """,
    license='GPL-2.0',
    description='IRIS Package Database plugin',
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
)
