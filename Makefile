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

HERE=$(shell pwd)
MANAGEPY=$(shell python -c 'from iris import manage; print(manage.__file__)')
MPATH=$(shell dirname $(MANAGEPY))

.PHONY: test devel clean

test:
	cd $(MPATH) && \
	ls && \
	COVERAGE_FILE=$(HERE)/.coverage python manage.py test \
		--with-xunit \
		--xunit-file=$(HERE)/nosetests.xml \
		--with-coverage \
		--cover-xml \
		--cover-xml-file=$(HERE)/coverage.xml \
		--cover-erase \
		--cover-branches \
		--cover-package=. \
		--verbosity=2

devel:		
	bash bin/generate_environment.sh

clean:
	rm -rf virtualenv build dist node_modules bower_components \
		iris.egg-info iris_packagedb.egg-info iris_submissions.egg-info
