# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the core deletion views file for iris-core.
"""

# pylint: disable=C0111,W0622

from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django.contrib import messages


def create(request, form, cancel_url=None):
    """
    A generic wrapper for creating given objects from a form.

    For GET renders an empty form, for POST validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with GET or POST
    :param  form:       Django form class to use for request
    :param  form:       Django form class
    :param  cancel_url: URL redirect for cancel button

    Example usage::

        def create_example(request):
            return create(request, ExampleForm)

    Which would use ExampleForm to instanciate a form and save possible object.
    """

    form = form(request.POST or None, cancel_url=cancel_url)
    url = None

    if request.method == 'POST' and form.is_valid():
        created = form.save()
        url = '%s/%s/' % (request.path.rstrip('create/'), created.id)
        messages.success(request, 'Creation successful!')

    return render(request, 'core/create.html', {
        'form': form,
        'url': url})


def update(request, pkid, model, form, cancel_url=None):
    """
    A generic wrapper for updating given objects with a form.

    For GET renders a prefilled form, for POST validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with GET or PUT
    :param  pkid:       Django model object database ID to fetch
    :type   pkid:       integer
    :param  model:      Django model class to use for request
    :type   model:      Django model class
    :param  form:       Django form class to use for request
    :type   form:       Django form class
    :param  cancel_url: URL redirect for cancel button

    Example usage::

        def example(request):
            return update(request, pkid, ExampleModel, ExampleForm)

    Which would use
    Exampleform to instanciate a form,
    Examplemodel and pkid to fetch the object to use for the update operation,
    """

    obj = get_object_or_404(model, id=pkid) if pkid else None

    form = form(request.POST or None, instance=obj, cancel_url=cancel_url)
    url = None

    if request.POST and form.is_valid():
        form.save()
        url = '%s/' % request.path.rstrip('update/')
        messages.success(request, 'Update successful!')

    return render(request, 'core/update.html', {
        'form': form,
        'url': url})


def delete(request, pkid, model, redirect_url=None):
    """
    A generic wrapper for deleting objects of type Model with id pkid.

    For GET renders an empty form, for PUT validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with DELETE
    :param  pkid:       Django model object database ID to fetch
    :type   pkid:       integer
    :param  model:      Django model class to use for request
    :type   model:      Django model class
    :param  redirect_url: URL redirect when after delete

    Example usage::

        def example(request):
            return delete(request, pkid, ExampleModel)
    """

    obj = get_object_or_404(model, id=pkid)
    deleted = model_to_dict(obj)
    try:
        obj.delete()
    except Exception as err:
        return render(request, 'core/delete.html', {'error': repr(err)})

    return render(request, 'core/delete.html', {
            'deleted': deleted,
            'redirect_url': redirect_url,
            })
