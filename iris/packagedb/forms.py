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
# E1101(%s %r has no %r member) Django model objects
# C1001(old-style-class) Django raised on every Meta class
# pylint: disable=E1002,C0111,R0903,W0232,E1101,C1001

from django import forms

from iris.core.forms import BaseForm, GroupedModelChoiceField
from iris.core.models import (Domain, SubDomain,
        License, GitTree, Package, Product, Image)

MULTI_SELECT_HELP_TEXT = "Click items from left into right to select"


class DomainForm(BaseForm):
    name = forms.CharField(label='Name for the domain')

    class Meta:
        model = Domain


class SubDomainForm(BaseForm):
    name = forms.CharField(label='Name for the subdomain')

    class Meta:
        model = SubDomain


class LicenseForm(BaseForm):
    shortname = forms.CharField(label='Short name for the license')
    fullname = forms.CharField(label='Full name for the license')

    class Meta:
        model = License


class GitTreeForm(BaseForm):
    gitpath = forms.CharField(label='Git path for the tree')
    subdomain = GroupedModelChoiceField(queryset=SubDomain.objects.all(),
                                        group_by_field='domain')
    licenses = forms.ModelMultipleChoiceField(
        queryset=License.objects.all())
    licenses.help_text = MULTI_SELECT_HELP_TEXT

    class Meta:
        model = GitTree


class PackageForm(BaseForm):
    name = forms.CharField(label='Name for the package')

    class Meta:
        model = Package


class ProductForm(BaseForm):
    name = forms.CharField(label='Full name for the product')
    gittrees = forms.ModelMultipleChoiceField(
        label='Select associated git trees',
        widget=forms.SelectMultiple(attrs={'size': '20'}),
        queryset=GitTree.objects.all())
    # In order to remove builtin help text as follows, we have
    # to set it to empty after this filed has been created
    # "Hold down "Ctrol", or "Command" on a Mac, to select more than one."
    gittrees.help_text = MULTI_SELECT_HELP_TEXT

    class Meta:
        model = Product


class ImageForm(BaseForm):
    class Meta:
        model = Image
