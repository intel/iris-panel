# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the root views module for the iris-core project.
"""

import logging
from pkg_resources import iter_entry_points

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError

from iris.core.injectors import inject_user_getters

log = logging.getLogger(__name__)


def error(request):
    """
    Returns the 404 page.
    """

    return render(request, '404.html')


def index(request):
    """
    Returns page index.
    """

    apps = []

    # Get button info for accessible apps to front page:
    for plugin in iter_entry_points(group='iris.app'):
        fields = plugin.load()

        try:
            app = {
                # URL is filtered because it's in regexp format of r'^url/'
                'url': fields['urlpatterns']['baseurl'].replace('^', ''),
                'intro': fields['intro'],
                'header': fields['header']
            }

            apps.append(app)

        except KeyError as field:
            log.warn('Plugin error, entrypoint field "%s" missing!' % field)

    return render(request, 'core/index.html', {
        'apps': apps,
    })


def login_view(request):
    """
    Returns login at '/login' and logs user in from POST.
    """

    redirect_url = request.REQUEST.get('next', '') or '/'

    if request.POST:
        try:
            username = request.POST['username']
            password = request.POST['password']
        except MultiValueDictKeyError:
            messages.error(request, 'Login failed.')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            log.info('login|%s|%s', user.username, user.email)
            return redirect(redirect_url)

        else:
            messages.error(request, 'Faulty login credentials.')

    return render(request, 'core/login.html', {
        'redirecto_to': redirect_url})


def logout_view(request):
    """
    Logs user out and redirects to '/'.
    """

    logout(request)
    return redirect('/')


@login_required
def settings_view(request):
    """
    Returns settings view (unimplemented).
    """

    return render(request, 'core/settings.html', {
        'messages': messages})


@login_required
def users(request, pkid=None):
    """
    Returns IRIS user list.
    """

    if pkid:
        user = inject_user_getters(get_object_or_404(User, id=pkid))
        return render(request, 'core/user.html',
                {'User': user})
    else:
        return render(request, 'core/users.html',
                {'users': User.objects.all()})
