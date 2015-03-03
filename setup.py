#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
"""
Setup file for the IRIS package.
"""
import os
from setuptools import setup, find_packages


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    url='http://panel.tizen.org',
    name='iris',
    version='0.3.1',
    #namespace_packages=['iris'],
    packages=find_packages(),
    include_package_data=True,
    license='GPL-2.0',
    description='IRIS - Infrastructure and Release Engineering Service',
    long_description=README,
    author='see AUTHORS file',
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
        'bin/update_iris_data.sh',
        'bin/download_snapshots.py',
        'bin/scmlint.py',
    ],
    install_requires=open('requirements.txt').readlines(),
)
