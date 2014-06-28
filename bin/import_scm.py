#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Module for importing git scm data into IRIS.

Data is available from:
    https://review.tizen.org/gerrit/gitweb?p=scm/meta/git.git
"""

import os
import sys
import argparse

from django.db import transaction

from iris import manage

PROJECT = os.path.dirname(manage.__file__)

if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)

# Add Django settings for the sake of imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'iris.core.settings'

from iris.etl import scm

def main():
    """
    Imports package, domain and license data and creates Tizen 3.0 products.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('domain', type=file, help='domain data file')
    parser.add_argument('gittree', type=file, help='git tree data file')
    args = parser.parse_args()

    print('Starting package data update...')
    transaction.set_autocommit(False)
    scm.from_file(args.domain, args.gittree)
    transaction.commit()

if __name__ == '__main__':
    main()
