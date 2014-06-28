#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Module for importing Product, Package, Image, License data into IRIS.
"""
import os
import sys
from iris import manage
PROJECT = os.path.dirname(manage.__file__)
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)
# Add Django settings for the sake of imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'iris.core.settings'

import argparse

from django.db import transaction

from iris.etl import snapshot

# pylint: disable=E0611,E1101,F0401,R0914
#E0611: No name 'manage' in module 'iris'
#E1101: Class 'Domain' has no 'objects' member
#F0401: Unable to import 'iris.core.models'
#C0321: More than one statement on a single line


def main():
    """
    Imports package, domain and license data and creates Tizen 3.0 products.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('product', type=str, help="Product name")
    parser.add_argument('snapshot_path', type=str,
        help="Product snapshot path on IRIS server which saves products data.")
    args = parser.parse_args()

    print('Starting snapshot data update...')

    transaction.set_autocommit(False)
    snapshot.from_dir(args.product, args.snapshot_path)
    transaction.commit()


if __name__ == '__main__':
    main()
