#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Module for checking git scm data before importing.
"""
import os
import sys
import argparse
os.environ['DJANGO_SETTINGS_MODULE'] = 'iris.core.settings'
from iris.etl.check import check_scm


def main():
    """
    Imports package, domain and license data and creates Tizen 3.0 products.
    return 0 means everything is ok, Non-zero means errors exist.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('domain', type=file, help='domain data file')
    parser.add_argument('gittree', type=file, help='git tree data file')
    args = parser.parse_args()

    print('Starting check git scm data...')
    res = file_import(args.domain, args.gittree)
    print('check git scm data end. %s failed.' % (res))
    return res


def file_import(domain_file, gittree_file):
    """
    read domain and git-tree file.
    """
    res = check_scm(domain_file.read(), gittree_file.read())
    return res


if __name__ == '__main__':
    sys.exit(main())
