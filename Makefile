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

.PHONY: test
test:
	export OUTPUT_DIR=`pwd` \
		&& cd \
		&& cd `python -c "import os; from iris import manage; \
			print(os.path.dirname(manage.__file__))"` \
		&& export COVERAGE_FILE=$$OUTPUT_DIR/.coverage \
		&& coverage run --source=core,packagedb manage.py test \
		&& export COVERAGE_XML=$$OUTPUT_DIR/coverage.xml \
		&& coverage xml -o $$COVERAGE_XML \
		&& coverage report -m \
		&& export JUNIT_XML=$$OUTPUT_DIR/nosetests.xml \
		&& py.test --ds=iris.core.settings --junitxml $$JUNIT_XML

.PHONY: devel
devel:
	bash bin/generate_environment.sh

.PHONY: clean
clean:
	rm -rf virtualenv build dist node_modules bower_components \
		iris.egg-info iris_packagedb.egg-info iris_submissions.egg-info
