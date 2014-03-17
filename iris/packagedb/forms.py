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
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Div
from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)


def add_default_buttons(layout):
    """
    Appends "Save" and "Cancel" buttons to given layout.

    :param  layout:     Layout to append buttons to.
    :type   layout:     FormHelper layout.

    Example usage with a modelform::

        class AppendedForm(forms.ModelForm):
            def __init__(self, *args, **kwargs):
                super(AppendedForm, self).__init__(*args, **kwargs)
                self.helper = FormHelper(self)
                add_default_buttons(self.helper.layout)
    """

    layout.append(Div(
        Submit('save', 'Save'),
        Button('cancel', 'Cancel', onclick='history.back()'),
        css_class='pull-right')
    )


class BaseForm(forms.ModelForm):
    """
    A basic form with save and cancel buttons.

    Inherit your own forms from this one.

    Example usage with Django forms::

        class ExampleForm(BaseForm):
            def __init__(self, *args, **kwargs):
                super(ExampleForm, self).__init__(*args, **kwargs)
    """

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        add_default_buttons(self.helper.layout)


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
    notes = forms.CharField(required=False,
            widget=forms.Textarea(attrs={'rows': 3}))

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
    short = forms.CharField(label='Short name for the product')
    state = forms.CharField(label='Current state of the product')
    targets = forms.CharField(label='List of targets for the product')
    gittrees = forms.MultipleChoiceField(
            label='Select associated git trees',
            widget=forms.SelectMultiple(attrs={'size': '20'}))

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Product


class ImageForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Image
