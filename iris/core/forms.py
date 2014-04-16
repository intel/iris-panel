# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the common forms and utilities file for the iris project.
"""

# pylint: disable=E1002,C0111,R0903,W0232

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Div


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


