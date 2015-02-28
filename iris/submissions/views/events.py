# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
"""
View functions to handler submission events
"""
import sys
import urllib
import logging

from MySQLdb.constants.ER import DUP_ENTRY, LOCK_DEADLOCK

from django.utils import timezone
from django.db import IntegrityError, OperationalError, transaction
from django.contrib.auth.decorators import permission_required

from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED,
    HTTP_406_NOT_ACCEPTABLE,
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view

from iris.core.models import (
    Submission, SubmissionBuild, ImageBuild, PackageBuild, Snapshot,
    BuildGroup
    )
from iris.submissions.views.event_forms import (
    SubmittedForm, PreCreatedForm, PackageBuiltForm,
    ImageBuildingForm, ImageCreatedForm, RepaActionForm,
    SnapshotStartForm, SnapshotFinishedForm, SnapshotReleaseForm)

# pylint: disable=C0111,E1101,W0703,W0232,E1002,R0903,C0103
# W0232: 25,0:SubmittedForm: Class has no __init__ method
# E1002: 78,4:PreCreatedForm.clean: Use of super on an old style class
# R0903: 90,0:ImageBuildingForm: Too few public methods (1/2)

logger = logging.getLogger(__name__)

PUBLISH_EVENTS_PERM = 'core.publish_events'

@api_view(["POST"])
@permission_required(PUBLISH_EVENTS_PERM, raise_exception=True)
def events_handler(request, typ):
    """
    Common event handler for all submissions events
    """
    handlers = {
        'submitted': submitted,
        'pre_created': pre_created,
        'pre_created_failed': pre_created_failed,
        'package_built': package_built,
        'image_building': image_building,
        'image_created': image_created,
        'repa_action': repa_action,
        'snapshot_start': snapshot_start,
        'snapshot_finish': snapshot_finish,
        'snapshot_release': snapshot_release,
        }
    print >> sys.stderr, 'events|%s|%s' % (request.path, request.POST.items())
    handler = handlers.get(typ)
    if not handler:
        return Response({'detail': 'Unknown event type'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    try:
        with transaction.atomic():
            return handler(request)
    except OperationalError as err:
        if err.args[0] != LOCK_DEADLOCK:
            raise
        # refs: http://dev.mysql.com/doc/refman/5.5/en/innodb-deadlocks.html
        # Always be prepared to re-issue a transaction if it fails due to
        # deadlock. Deadlocks are not dangerous. Just try again.
        logger.warn("Deadlock found, try again: %s" % str(err))
        with transaction.atomic():
            return handler(request)


def submitted(request):
    """
    Event that occurs when a tag submitted

    tag -- Tag name
    gitpath -- Git tree path
    commit_id -- Commit hash
    submitter_email -- Email of submitter
    """
    form = SubmittedForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data

    sub = Submission(
        name=data['tag'],
        gittree=data['gitpath'],
        commit=data['commit_id'],
        owner=data['submitter_email'],
        status='SUBMITTED',
        )
    try:
        sub.save()
    except IntegrityError as err:
        if err.args[0] == DUP_ENTRY:
            return Response({'detail': str(err)}, status=HTTP_202_ACCEPTED)
        raise

    return Response({'detail': 'Tag submitted'}, status=HTTP_201_CREATED)


def pre_created(request):
    """
    Event that happens when a pre-release project had been created

    gitpath -- Git tree path
    tag -- Tag name
    product -- Target product name
    project -- Pre-release project name
    """
    form = PreCreatedForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data

    group = data['project']

    build = SubmissionBuild(
        submission=data['submission'],
        product=data['product'],
        group=data['project'])
    try:
        build.save()
    except IntegrityError as err:
        if err.args[0] == DUP_ENTRY:
            return Response({'detail': str(err)}, status=HTTP_202_ACCEPTED)
        raise

    group.populate_status()
    return Response({'detail': 'Pre-release project created'},
                    status=HTTP_201_CREATED)


def pre_created_failed(request):
    """
    Event that happens when a pre-release project failed to create
    tag -- Tag name
    gitpath -- Git tree path
    reason -- Why pre-release project creat fail
    """
    try:
        sub = Submission.objects.get(
            name=request.POST['tag'],
            gittree__gitpath=request.POST['gitpath'].strip('/')
            )
    except Submission.DoesNotExist as err:
        return Response({'detail': 'wrong tag name or gitpath'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    else:
        sub.status = 'ERROR'
        sub.reason = request.POST['reason']
        sub.save()
        return Response(
            {'detail': 'submission status updated'},
            status=HTTP_200_OK)


def guess_live_repo_url(server, project, repo):
    """
    Guess live repo url like this:

    https://build.otctools.jf.intel.com/project/repository_state/Tools/CentOS_6
    """
    return '%s/project/repository_state/%s/%s' % (
        server.rstrip('/'),
        urllib.quote(project),
        repo)


def guess_build_log_url(server, project, package, repo, arch):
    """
    Guess build log link like this:

    https://build.tizen.org/package/live_build_log?arch=x86_64&package=automake&project=home%3Aprerelease%3ATizen%3AIVI%3Asubmit%3Atizen_ivi%3A20141007.444444&repository=atom64
    """
    return '%s/package/live_build_log?arch=%s&package=%s&project=%s&repository=%s' % (
        server.rstrip('/'),
        arch,
        package,
        urllib.quote(project),
        repo)


def package_built(request):
    """
    Event that happens when a package was built

    name -- Package name
    repo -- Building repository name
    arch -- Building architecture
    project -- Pre-release project name
    status -- Status
    repo_server -- Repository URL
    """
    form = PackageBuiltForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data
    group = data['project']
    # Have to save group.status before creating a new record in PackageBuild,
    # otherwise deadlock may be raised. Since PackageBuild.group_id is a
    # foreign key to BuildGroup.id, when insert a new record to PackageBuild,
    # MSYQL trys to add a shared lock on BuildGroup's corresponding row.
    # refs: http://dev.mysql.com/doc/refman/5.5/en/innodb-foreign-key-constraints.html
    group.check_packages_status(
        PackageBuild(
            package=data['name'],
            repo=data['repo'],
            arch=data['arch'],
            group=group,
            status=data['status']))

    url = guess_live_repo_url(data['repo_server'], group.name, data['repo'])
    log = guess_build_log_url(data['repo_server'],
                              group.name, data['name'].name,
                              data['repo'], data['arch'])
    pbuild, created = PackageBuild.objects.get_or_create(
        package=data['name'],
        repo=data['repo'],
        arch=data['arch'],
        group=group,
        defaults={
            'status': data['status'],
            'url': url,
            'log': log,
            })
    if not created:
        pbuild.status = data['status']
        pbuild.url = url
        pbuild.log = log
        pbuild.save()

    group.populate_status()
    msg = {'detail': '%s bulit %s' % (data['name'], data['status'])}
    return Response(msg, status=HTTP_200_OK)


def image_building(request):
    """
    Event that happens when a image started to build

    name -- Image name
    project -- Pre-release project name
    repo -- Building repository
    #arch -- Building architecture
    """
    form = ImageBuildingForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)

    data = form.cleaned_data
    group = data['project']

    group.check_images_status(
        ImageBuild(
            name=data['name'],
            group=group,
            status='BUILDING'))

    ImageBuild.objects.get_or_create(
        name=data['name'],
        group=data['project'],
        defaults={
            'status': 'BUILDING',
            'repo': data['repo'],
            })

    group.populate_status()
    return Response({'detail': 'Image started to build'},
                    status=HTTP_200_OK)


def image_created(request):
    """
    Event that happends when a image created

    name -- Image name
    project -- Pre-release project name
    status -- status
    url -- Image URL
    #log -- Build log
    """
    form = ImageCreatedForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)

    data = form.cleaned_data
    ibuild, group = data['name'], data['project']

    # Now the image and log all can be downloaded from the same url
    ibuild.url = data['url']
    ibuild.log = data['url']

    group.check_images_status(ibuild)
    ibuild.save()
    group.populate_status()
    return Response({'detail': 'Image created %s' % data['status']},
                    status=HTTP_200_OK)


def repa_action(request):
    """
    Event that happens when `repa` operates on some pre-release project

    project - Pre-release project
    status - Accepted or rejected
    who - Operator's Email
    reason - Explanation
    when - When this happened
    """
    form = RepaActionForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data

    group = data['project']
    group.status = data['status']
    group.operator = data['who'].strip()
    # since enabled timezone support, here it should get aware datetime
    group.operated_on = timezone.now()
    group.operate_reason = data['reason'].strip()
    group.save()
    group.populate_status()

    return Response({'detail': 'Action %s received' % data['status']},
                    status=HTTP_200_OK)


def snapshot_start(request):
    form = SnapshotStartForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data
    Snapshot.objects.create(buildid=data['buildid'],
                            started_time=data['started_time'],
                            product=data['project'])

    return Response({'detail': 'Action snapshot start received'},
                    status=HTTP_200_OK)


def snapshot_finish(request):

    def manage_submissions():
        buildgroups = BuildGroup.objects.filter(
            status="33_ACCEPTED",
            operated_on__lt=snapshot.started_time,
            submissionbuild__product=snapshot.product,
            snapshot=None)

        for buildgroup in buildgroups:
            buildgroup.snapshot = snapshot
            buildgroup.save()

    form = SnapshotFinishedForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)

    data = form.cleaned_data
    snapshot = Snapshot.objects.get(buildid=data['buildid'],
                                    product=data['project'])
    snapshot.finished_time = data['finished_time']
    snapshot.url = data['url']
    snapshot.save()
    manage_submissions()

    return Response({'detail': 'Action snapshot finish received'},
                    status=HTTP_200_OK)


def snapshot_release(request):
    form = SnapshotReleaseForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)
    data = form.cleaned_data
    snapshot = Snapshot.objects.get(buildid=data['buildid'],
                                    product=data['project'])
    if data['release_type'] == 'daily':
        snapshot.daily_url = data['url']
    elif data['release_type'] == 'weekly':
        snapshot.weekly_url = data['url']
    snapshot.save()

    return Response({'detail': 'Action snapshot release received'},
                    status=HTTP_200_OK)
