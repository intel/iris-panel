# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Admin site registrations for the IRIS Core application models.
"""

# Disabling __init__ and public method amount checks
# pylint: disable=W0232, E0102, R0903, R0904

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from iris.core.models import (
    Domain, SubDomain, License, GitTree, Package, Product, Image,
    PackageBuild, ImageBuild, Submission,
    UserProfile, UserParty, DomainRole, SubDomainRole, GitTreeRole)


class UserProfileInline(admin.StackedInline):
    """
    Inline admin view to user profile.
    """

    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    """
    User administrator which allows user profile manipulation in user view.
    """

    inlines = (UserProfileInline, )


# Registering user under the user admin view requires deregistering
# the default view to avoid duplication in the admin site controls
admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(UserParty)
admin.site.register(DomainRole)
admin.site.register(SubDomainRole)
admin.site.register(GitTreeRole)
admin.site.register(Domain)
admin.site.register(SubDomain)
admin.site.register(License)
admin.site.register(GitTree)
admin.site.register(Package)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(PackageBuild)
admin.site.register(ImageBuild)
admin.site.register(Submission)
