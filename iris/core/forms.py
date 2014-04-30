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
from django.forms.models import ModelChoiceIterator, ModelChoiceField
from itertools import groupby
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Div


def add_default_buttons(layout, cancel_url):
    """
    Appends "Save" and "Cancel" buttons to given layout.

    :param  layout:     Layout to append buttons to.
    :type   layout:     FormHelper layout.
    :param  cancel_url: URL redirect to for cancel button

    Example usage with a modelform::

        class AppendedForm(forms.ModelForm):
            def __init__(self, *args, **kwargs):
                super(AppendedForm, self).__init__(*args, **kwargs)
                self.helper = FormHelper(self)
                add_default_buttons(self.helper.layout)
    """
    if not cancel_url:
        cancel_onclick = 'history.back()'
    else:
        cancel_onclick = 'window.location.href="%s"' % cancel_url

    layout.append(Div(
        Submit('save', 'Save'),
        Button('cancel', 'Cancel', onclick=cancel_onclick),
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
        if 'cancel_url' in kwargs:
            cancel_url = kwargs.pop('cancel_url')
        else:
            cancel_url = None
        super(BaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        add_default_buttons(self.helper.layout, cancel_url)


class GroupedModelChoiceField(ModelChoiceField):
    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        group_by_field is the name of a field on the model
        group_label is a function to return a label for each choice group
        """
        super(GroupedModelChoiceField, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        """
        Exactly as per ModelChoiceField except returns new iterator class
        """
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, ModelChoiceField._set_choices)


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        """
        Generate choices in select widget
        """
        if self.field.empty_label is not None:
            yield (u"", self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    (self.field.group_label(group),
                     [self.choice(ch) for ch in choices])
                    for group, choices in groupby(self.queryset.all(),
                      key=lambda row: getattr(row, self.field.group_by_field))
                    ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for group, choices in groupby(self.queryset.all(),
                    key=lambda row: getattr(row, self.field.group_by_field)):
                yield (self.field.group_label(group),
                       [self.choice(ch) for ch in choices])
