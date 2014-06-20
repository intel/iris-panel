#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Module for importing Product, Package, Image data into IRIS.
"""


# pylint: disable=E0611,E1101,F0401,R0914,C0103
#E0611: No name 'manage' in module 'iris'
#E1101: Class 'Domain' has no 'objects' member
#F0401: Unable to import 'iris.core.models'
#C0321: More than one statement on a single line
#C0103: Invalid name "logger"


import os
import logging

from django.core.exceptions import ObjectDoesNotExist
from iris.core.models import GitTree, Product, Package, Image
from iris.etl import scm
from iris.etl import parser


logger = logging.getLogger(__name__)


def transform(prod, prod_path):
    """transform data
    """
    prod_tree = []
    package_data = []
    pkg_tree = []
    image_data = []

    product = Product.objects.get(name=prod)
    # get data from Tizen path by product name
    trees, packages, images = get_prod_data(product, prod_path)

    for tree in trees:
        try:
            gittree = GitTree.objects.get(gitpath=tree)
        except ObjectDoesNotExist:
            logger.warning("%s GitTree object is not existing in DB!", tree)
            continue
        prod_tree.append(gittree)

    for pkg, tree in packages:
        try:
            gittree = GitTree.objects.get(gitpath=tree)
        except ObjectDoesNotExist:
            logger.warning("%s releated %s is not existing in DB!", pkg, tree)
            continue
        package = Package(name=pkg)
        package_data.append(package)
        pkg_tree.append((gittree, package))

    for prod, target, arch, name in images:
        image = Image(product=product, target=target, arch=arch, name=name)
        image_data.append(image)

    return product, package_data, image_data, pkg_tree, prod_tree


def incremental_import(prod, prod_path):
    """import data
    """
    product, packages, images, pkg_tree, prod_tree = transform(prod, prod_path)

    scm.load_entity(packages, Package.objects.all(),
        lambda i: i.name, delete=False)

    scm.load_entity(images, Image.objects.select_related('product').all(),
        lambda i: '%s: %s-%s' % (i.product.name, i.target, i.name),
        delete=False)

    db_prod_tree = [t for t in product.gittrees.all()]
    load_prod_tree(product, prod_tree, db_prod_tree, lambda t: t.gitpath)

    db_pkg_tree = [(t, p) for t in product.gittrees.all()
        for p in t.packages.all()]
    load_pkg_tree(pkg_tree, db_pkg_tree, lambda (t, p): '%s: %s' % (t.gitpath,
        p.name))


def load_pkg_tree(new, old, key):
    """load relations of packages and gittrees into database
    """
    assert new
    added, thesame, deleted = scm.diff(new, old, key)
    print '{:>15} added={:<5} thesame={:<5} deleted={:<5}'.format(
        'GitTree of Package', len(added), len(thesame), len(deleted))
    for tree, obj in added:
        tree.packages.add(obj.__class__.objects.get(name=obj.name))


def load_prod_tree(product, new, old, key):
    """load relations products and trees into database
    """
    assert new
    added, thesame, deleted = scm.diff(new, old, key)
    print '{:>15} added={:<5} thesame={:<5} deleted={:<5}'.format(
        'GitTree of Product', len(added), len(thesame), len(deleted))
    for obj in added:
        product.gittrees.add(obj)
    for obj in deleted:
        product.gittrees.remove(obj)


def get_prod_data(prod, prod_path):
    """get all prod data, include trees, images, packages
    """
    packages = []
    images = []
    build_file = os.path.join(prod_path, 'build.xml')
    repo_file = os.path.join(prod_path,
        'repos/%s/packages/repodata/')
    image_file = os.path.join(prod_path, 'builddata/images/%s/images.xml')
    tree_dir = os.path.join(prod_path, 'builddata/manifest')

    targets = parser.parse_buildxml(build_file)
    trees = parser.parse_trees_of_prod(tree_dir)

    for target in targets:
        packages.extend(parser.parse_packages(repo_file % target))
        images.extend(parser.parse_images(image_file % target,
            prod.name, target))

    return trees, packages, images
