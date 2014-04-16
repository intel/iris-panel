# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the forms file for the iris-submissions application.

Forms correspond to their respective models in the iris.core.models module
"""

# pylint: disable=E1002,C0111,R0903,W0232

from django import forms
from django.contrib.auth.models import User
from django.utils.timezone import now
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset
from iris.core.forms import BaseForm
from iris.core.models import Submission, SubmissionGroup


class SubmissionForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Submission


class SubmissionGroupForm(BaseForm):
    submissions = forms.ModelMultipleChoiceField(
        label='Select submissions for group testing',
        widget=forms.SelectMultiple(attrs={'size': '20'}),
        queryset=Submission.objects.all())

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('name'),
                Field('author', readonly=True),
                Field('product'),
                Field('submissions'),
            ),
        )

        super(SubmissionGroupForm, self).__init__(*args, **kwargs)

    def set_name(self, name=None):
        if not name:
            name = 'submit/tizen/%s' % now().strftime('%Y%m%d.%H%M%S')

        self.fields['name'] = \
                forms.CharField(initial=name)

    def set_author(self, request):
        user = User.objects.filter(id=request.user.id)
        self.fields['author'] = \
                forms.ModelChoiceField(queryset=user, empty_label=None,
                        widget=forms.Select(attrs={'disabled':'disabled'}))

    class Meta:
        model = SubmissionGroup
        fields = ('name', 'author', 'product', 'submissions',)
