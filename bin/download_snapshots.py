#! /usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""Download Tizen products snapshots
"""

import os
import re
import argparse

from django.conf import settings
from pyquery import PyQuery as pq

from iris.etl.url import URL

# pylint: disable=E1103
# E1103: Instance of 'URL' has no 'href' member

# Add Django settings for the sake of imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'iris.core.settings'

NAME_AND_LAST_MODIFIED = re.compile(
    r'<a .*?href=(["\'])(.*?)\1.*?>\2</a>\s*'
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')


def main():
    """download snapshots and call import_packages script
    """
    desc = "Download Tizen snapshots to the given workdir on your file system."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('workdir', type=str, help='Use for saving Snapshots')
    args = parser.parse_args()
    workdir = args.workdir

    if not os.path.exists(workdir):
        os.makedirs(workdir)

    def get_lastid(filename):
        """get latest timestamp of downloading snapshots
        """
        if os.path.exists(filename):
            with open(filename) as reader:
                return reader.read()

    def save_lastid(filename, lastid):
        """set timesttamp of downloading snapshots
        """
        with open(filename, 'w') as writer:
            writer.write(lastid)

    def each(data, element, name):
        """get attributes of emelent from PyQuery data
        """
        return [pq(i).attr(name) for i in data(element)]

    def guess_latest(baseurl):
        """Guess the real path of latest from last modified info.
        """
        url = baseurl.join('..')
        page = url.asdir().fetch()
        idx = {}
        latest_mod = None
        for _quote, name, lastmod in NAME_AND_LAST_MODIFIED.findall(page):
            if name.startswith('latest'):
                latest_mod = lastmod
            else:
                idx[lastmod] = name
        if latest_mod and latest_mod in idx:
            return url.join(idx[latest_mod])
        raise Exception("Can't find latest snapshot in:%s" % url)

    for pname, urlstring in settings.IRIS_PRODUCT_MAPPING:

        baseurl = URL(urlstring)
        latesturl = guess_latest(baseurl)
        pdir = os.path.join(workdir, latesturl.href.split('//')[1])

        buildurl = latesturl.join('build.xml')
        text = pq(buildurl.fetch())

        idfile = os.path.join(workdir, '%s.latest.timestamp' % pname)
        newid = text('id').text()
        lastid = get_lastid(idfile)

        if lastid and newid <= lastid:
            print "%s has no update yet!" % pname
            print "Last download timestamp: %s" % lastid
            continue

        buildurl.download(workdir)

        for target in each(text, 'buildtarget', 'name'):

            # Image
            image_path = os.path.join('builddata', 'images', target,
                'images.xml')
            imgxmlurl = latesturl.join(image_path)
            imgxmlurl.download(workdir)

            # Packages
            pkg_path = os.path.join('repos', target, 'packages', 'repodata')
            for url in latesturl.join(pkg_path).glob('*-primary.xml.gz'):
                url.download(workdir)

        # Manifest
        manifest_path = os.path.join('builddata', 'manifest')
        for url in latesturl.join(manifest_path).listdir():
            url.download(workdir)

        os.system('import_snapshot.py %s %s' % (pname, pdir))

        save_lastid(idfile, newid)


if __name__ == '__main__':
    main()
