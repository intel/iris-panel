#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Download Tizen products snapshots
"""
# pylint: disable=E1103
#E1103: Instance of 'URL' has no 'href' member

import os
import argparse

from django.conf import settings
from pyquery import PyQuery as pq

from iris.etl.url import URL

# Add Django settings for the sake of imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'iris.core.settings'

WORKDIR = '/tmp/tizen_snapshots/'


def main():
    """download snapshots and call import_packages script
    """
    desc = "Download Tizen snapshots to %s on your file system." % WORKDIR
    parser = argparse.ArgumentParser(description=desc)
    parser.parse_args()

    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)

    def get_lastid(ppath):
        """get latest timestamp of downloading snapshots
        """
        filename = os.path.join(ppath, 'latest.timestamp')
        if os.path.exists(filename):
            with open(filename) as reader:
                return reader.read()

    def save_lastid(ppath, lastid):
        """set timesttamp of downloading snapshots
        """
        filename = os.path.join(ppath, 'latest.timestamp')
        if not os.path.exists(ppath):
            os.makedirs(ppath)
        with open(filename, 'w') as writer:
            writer.write(lastid)

    def each(data, element, name):
        """get attributes of emelent from PyQuery data
        """
        return [pq(i).attr(name) for i in data(element)]

    for pname, urlstring in settings.IRIS_PRODUCT_MAPPING:
        baseurl = URL(urlstring)
        pdir = os.path.join(WORKDIR, baseurl.href.split('//')[1])
        buildurl = baseurl.join('build.xml')

        text = pq(buildurl.fetch())
        newid = text('id').text()
        lastid = get_lastid(pdir)

        if lastid and newid <= lastid:
            print "%s has no update yet!" % pname
            print "Last download timestamp: %s" % lastid
            continue

        buildurl.download(WORKDIR)

        for target in each(text, 'buildtarget', 'name'):

            # Image
            image_path = os.path.join('builddata', 'images', target,
                'images.xml')
            imgxmlurl = baseurl.join(image_path)
            imgxmlurl.download(WORKDIR)

            # Packages
            package_path = os.path.join('repos', target, 'packages', 'repodata')
            for url in baseurl.join(package_path).glob('*-primary.xml.gz'):
                url.download(WORKDIR)

        # Manifest
        manifest_path = os.path.join('builddata', 'manifest')
        for url in baseurl.join(manifest_path).listdir():
            url.download(WORKDIR)

        os.system('import_snapshot.py %s %s' % (pname, pdir))

        save_lastid(pdir, newid)

if __name__ == '__main__':
    main()
