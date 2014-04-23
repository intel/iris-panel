# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the forms file for the iris-packagedb application.

Forms correspond to their respective models in the iris.core.models module
"""

# pylint: disable=E1002,C0111,R0903,W0232

from django import forms
from iris.core.forms import BaseForm
from iris.core.models import (Domain, SubDomain,
        License, GitTree, Package, Product, Image)


class DomainForm(BaseForm):
    name = forms.CharField(label='Name for the domain')

    def __init__(self, *args, **kwargs):
        super(DomainForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Domain


class SubDomainForm(BaseForm):
    name = forms.CharField(label='Name for the subdomain')

    def __init__(self, *args, **kwargs):
        super(SubDomainForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SubDomain


class LicenseForm(BaseForm):
    shortname = forms.CharField(label='Short name for the license')
    fullname = forms.CharField(label='Full name for the license')

    def __init__(self, *args, **kwargs):
        super(LicenseForm, self).__init__(*args, **kwargs)

    class Meta:
        model = License


class GitTreeForm(BaseForm):
    gitpath = forms.CharField(label='Git path for the tree')

    def __init__(self, *args, **kwargs):
        super(GitTreeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = GitTree


class PackageForm(BaseForm):
    name = forms.CharField(label='Name for the package')

    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Package


class ProductForm(BaseForm):
    name = forms.CharField(label='Full name for the product')
    gittrees = forms.ModelMultipleChoiceField(
        label='Select associated git trees',
        widget=forms.SelectMultiple(attrs={'size': '20'}),
        queryset=GitTree.objects.all())

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Product


class ImageForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Image
