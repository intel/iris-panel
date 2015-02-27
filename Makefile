# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

# This is the test runner for the IRIS project.
# Test segment should be run by Jenkins on each build,
# and this file is mainly for instructing Jenkins on how to
# test and produce test reports in the build environment.

# First we test core application itself.
# Then we test namespace subpackages, which require prefixes.

# Test output directory is CWD, where the XML output files are placed
# First we adjust paths and find out where IRIS is actually installed
# We can't import from CWD because we have overriding iris directory there
# After that we execute tests in the system library location,
# which has to be found out by getting a concrete package location
# (in this case the iris.core) and coming down to namespace package level

.PHONY: test clean

test:
	python iris/manage.py test \
		--with-xunit \
		--with-coverage

clean:
	rm -rf build dist *.egg-info
