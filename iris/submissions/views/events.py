"""
View functions to handler submission events
"""
import sys
import urlparse
import urllib

from MySQLdb.constants.ER import DUP_ENTRY

from django.db import IntegrityError
from django.db.transaction import atomic
from django.contrib.auth.decorators import permission_required

from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED,
    HTTP_406_NOT_ACCEPTABLE,
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view

from iris.core.models import (
    Submission, SubmissionBuild, ImageBuild, PackageBuild,
    )
from iris.submissions.views.event_forms import (
    SubmittedForm, PreCreatedForm, PackageBuiltForm,
    ImageBuildingForm, ImageCreatedForm, RepaActionForm,
    )

# pylint: disable=C0111,E1101,W0703,W0232,E1002,R0903,C0103
# W0232: 25,0:SubmittedForm: Class has no __init__ method
# E1002: 78,4:PreCreatedForm.clean: Use of super on an old style class
# R0903: 90,0:ImageBuildingForm: Too few public methods (1/2)

PUBLISH_EVENTS_PERM = 'core.publish_events'

@atomic
@api_view(["POST"])
@permission_required(PUBLISH_EVENTS_PERM, raise_exception=True)
def events_handler(request, typ):
    """
    Common event handler for all submissions events
    """
    handlers = {
        'submitted': submitted,
        'pre_created': pre_created,
        'package_built': package_built,
        'image_building': image_building,
        'image_created': image_created,
        'repa_action': repa_action,
        }
    print >> sys.stderr, 'events|%s|%s' % (request.path, request.POST.items())
    handler = handlers.get(typ)
    if not handler:
        return Response({'detail': 'Unknown event type'},
                        status=HTTP_406_NOT_ACCEPTABLE)
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
    group.populate_status()

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
    return Response({'detail': 'Pre-release project created'},
                    status=HTTP_201_CREATED)


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
    Guess build long link like this:

    https://build.otctools.jf.intel.com/package/live_build_log/Tools/bmap-tools/CentOS_6/i586
    """
    return '%s/package/live_build_log/%s/%s/%s/%s' % (
        server.rstrip('/'),
        urllib.quote(project),
        package,
        repo,
        arch)


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
    group.populate_status()

    parts = urlparse.urlparse(form.cleaned_data['repo_server'])
    # FIXME: scheme in repo_server is http
    # but web page of build server is using https
    #server = '%s://%s' % (parts.scheme, parts.hostname)
    server = 'https://%s' % parts.hostname

    # FIXME: live repo and log urls can't be accessed anoymously
    url = guess_live_repo_url(server, group.name, data['repo'])
    log = guess_build_log_url(server,
                              group.name, data['name'].name,
                              data['repo'], data['arch'])

    pbuild, _ = PackageBuild.objects.get_or_create(
        package=data['name'],
        repo=data['repo'],
        arch=data['arch'],
        group=group)
    pbuild.status = data['status']
    pbuild.url = url
    pbuild.log = log
    pbuild.save()
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
    group.status = '20_IMGBUILDING'
    group.save()
    group.populate_status()

    ibuild = ImageBuild(name=data['name'],
                        status='BUILDING',
                        repo=data['repo'],
                        group=group)
    ibuild.save()
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
    ok = data['status'] == 'success'

    group = data['project']
    if ok:
        group.status = '30_READY'
    else:
        group.status = '25_IMGFAILED'
    group.save()
    group.populate_status()

    ibuild = data['name']
    ibuild.log = data['log']
    if ok:
        ibuild.url = data['url']
        ibuild.status = 'SUCCESS'
    else:
        ibuild.status = 'FAILURE'
    ibuild.save()
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
    group.operator = data['who']
    group.operator_on = data['when']
    group.save()
    group.populate_status()

    return Response({'detail': 'Action %s received' % data['status']},
                    status=HTTP_200_OK)
