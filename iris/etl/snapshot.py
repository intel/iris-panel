# -*- encoding: utf-8 -*-
"""
Module for importing Product, Package, Image data into IRIS.
"""
import os
import logging

from iris.core.models import GitTree, Product, Package, Image
from iris.etl.loader import get_default_loader
from iris.etl.parser import (
    parse_buildxml, parse_trees_of_prod, parse_packages, parse_images
    )

# pylint: disable=E0611,E1101,F0401,R0914,C0103
#E0611: No name 'manage' in module 'iris'
#E1101: Class 'Domain' has no 'objects' member
#F0401: Unable to import 'iris.core.models'
#C0321: More than one statement on a single line
#C0103: Invalid name "logger"

logger = logging.getLogger(__name__)


def transform(prod, prod_path):
    """transform data
    """
    trees, pkgs, imgs = get_prod_data(prod, prod_path)

    product_trees = [({'name': prod}, {'gitpath': gitpath})
                     for gitpath in trees]

    packages = [{'name': name} for name in
                {pkgname for pkgname, _ in pkgs}]

    trees_packages = [({'gitpath': gitpath}, {'name': pkgname})
                      for pkgname, gitpath in pkgs]

    images = [{'name': name,
               'target': target,
               'arch': arch,
               'product__name': prod,
               } for target, arch, name in imgs]

    return product_trees, packages, trees_packages, images


def get_prod_data(prod, prod_path):
    """get all prod data, include trees, images, packages
    """
    packages = []
    images = []
    build_file = os.path.join(prod_path, 'build.xml')
    repo_file = os.path.join(prod_path, 'repos/%s/packages/repodata/')
    image_file = os.path.join(prod_path, 'builddata/images/%s/images.xml')
    tree_dir = os.path.join(prod_path, 'builddata/manifest')

    targets = parse_buildxml(build_file)
    trees = parse_trees_of_prod(tree_dir)

    for target in targets:
        packages.extend(parse_packages(repo_file % target))
        images.extend(parse_images(image_file % target, target))

    return trees, packages, images


def from_dir(prod, prod_path):
    """
    Load snapshot related data into database, which includes project-trees
    relationship, trees-packages relationship and images.
    """
    # 1.transform
    (products_trees,
     packages, trees_packages,
     images) = transform(prod, prod_path)

    # 2.load
    loader = get_default_loader()
    loader.sync_entity(packages, Package)
    loader.sync_entity(images, Image)

    loader.sync_nnr(products_trees, Product, GitTree, remove=False)
    loader.sync_nnr(trees_packages, GitTree, Package, remove=False)
