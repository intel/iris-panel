# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the importing view file for the iris-packagedb application.

Views for importing data from scm/meta/git.
"""

# pylint: disable=C0111,W0622

import os
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.db.transaction import atomic
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from iris.etl import scm
from iris.etl.check import check_scm

log = logging.getLogger(__name__)


@api_view(['POST'])
@permission_required('core.scm_update', raise_exception=True)
@atomic
def update(request):
    """
    Importing scm data
    """
    domains = request.FILES.get('domains')
    gittrees = request.FILES.get('gittrees')

    if domains and gittrees:
        domains_str, gittrees_str = domains.read(), gittrees.read()
        detail = check_scm(domains_str, gittrees_str)
        if not detail:
            log.info('Importing scm data...')
            scm_str = ''.join([domains_str, os.linesep, os.linesep,
                               gittrees_str])
            scm.from_string(scm_str)
            cache.clear()
            detail = 'Successful!'
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_406_NOT_ACCEPTABLE
            detail = ','.join(detail)
            log.error(detail)
    else:
        detail = 'Can not find data files!'
        code = status.HTTP_406_NOT_ACCEPTABLE
        log.error(detail)
    content = {'detail': detail}
    return Response(content, status=code)


@api_view(['POST'])
@permission_required('core.scm_check', raise_exception=True)
def check(request):
    """
    Checking scm data
    """
    domains = request.FILES.get('domains')
    gittrees = request.FILES.get('gittrees')
    if domains and gittrees:
        log.info('Checking scm data...')
        detail = check_scm(domains.read(), gittrees.read())
        if not detail:
            detail = 'Successful!'
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_406_NOT_ACCEPTABLE
            detail = ','.join(detail)
            log.error(detail)
    else:
        detail = 'Can not find data files!'
        code = status.HTTP_406_NOT_ACCEPTABLE
        log.error(detail)
    content = {'detail': detail}
    return Response(content, status=code)
