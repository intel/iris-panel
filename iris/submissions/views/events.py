"""
View functions to handler submission events
"""
import datetime

from iris.core.models import (
    GitTree, Product,
    Submission, SubmissionBuild, BuildGroup,
    ImageBuild,
    )

from MySQLdb.constants.ER import DUP_ENTRY

from django import forms
from django.forms import ValidationError
from django.db import IntegrityError
from django.db.transaction import atomic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required

from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED,
    HTTP_406_NOT_ACCEPTABLE,
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view

# pylint: disable=C0111,E1101,W0703,W0232,E1002,R0903,C0103
# W0232: 25,0:SubmittedForm: Class has no __init__ method
# E1002: 78,4:PreCreatedForm.clean: Use of super on an old style class
# R0903: 90,0:ImageBuildingForm: Too few public methods (1/2)

class SubmittedForm(forms.Form):

    gitpath = forms.CharField(label="Git tree path")
    tag = forms.CharField(label="Tag name")
    commit_id = forms.CharField(label="Commit hash")
    submitter_email = forms.EmailField(label="Email of submitter")

    def clean_gitpath(self):
        gitpath = self.cleaned_data['gitpath']
        try:
            return GitTree.objects.get(gitpath=gitpath.strip('/'))
        except GitTree.DoesNotExist as err:
            raise forms.ValidationError(err)

    def clean_submitter_email(self):
        email = self.cleaned_data['submitter_email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email, email)
        return user


class PreCreatedForm(forms.Form):

    gitpath = forms.CharField(label="Git tree path")
    tag = forms.CharField(label="Tag name")
    product = forms.CharField(label="Target product name")
    project = forms.CharField(label="Pre-release project name")

    def clean_product(self):
        product = self.cleaned_data['product']
        try:
            return Product.objects.get(name=product)
        except Product.DoesNotExist as err:
            raise forms.ValidationError(str(err))

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            group = BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist:
            group = BuildGroup(
                name=project,
                status='00_NEW')
            group.save()
        return group

    def clean(self):
        data = super(PreCreatedForm, self).clean()
        try:
            sub = Submission.objects.get(
                name=data['tag'], gittree__gitpath=data['gitpath'].strip('/'))
        except Submission.DoesNotExist as err:
            raise forms.ValidationError(err)
        else:
            data['submission'] = sub
        return data


class ImageBuildingForm(forms.Form):

    name = forms.CharField(label="Image name")
    project = forms.CharField(label="Pre-release project name")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

class ImageCreatedForm(forms.Form):

    name = forms.CharField(label="Image name")
    project = forms.CharField(label="Pre-release project name")
    status = forms.ChoiceField(choices=(
            ('success', 'success'),
            ('failure', 'failure'),
            ))
    url = forms.URLField(label="Image URL")
    log = forms.URLField(label="Image building log URL")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

    def clean(self):
        data = self.cleaned_data
        if 'project' in data:
            try:
                ibuild = ImageBuild.objects.get(name=data['name'],
                                                group=data['project'])
            except ImageBuild.DoesNotExist as err:
                raise ValidationError(str(err))
            else:
                data['name'] = ibuild
        return data


class RepaActionForm(forms.Form):

    project = forms.CharField(label="Pre-release project name")
    status = forms.ChoiceField(choices=(
            ('accepted', 'accepted'),
            ('rejected', 'rejected'),
            ), label="Accepted or rejected")
    who = forms.EmailField(label="Operator's Email")
    reason = forms.CharField(label="Explanation")
    when = forms.DateTimeField(label="When this happened", required=False)

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

    def clean_status(self):
        if self.cleaned_data['status'] == 'accepted':
            return '33_ACCEPTED'
        return '36_REJECTED'

    def clean_who(self):
        email = self.cleaned_data['who']
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return User.objects.create_user(
                username=email, email=email)

    def clean_when(self):
        if self.cleaned_data['when']:
            return self.cleaned_data['when']
        return datetime.datetime.now()


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
def submitted(request):
    """
    Event that occurs when a tag submitted

    tag -- Tag name
    gittree -- Git tree path
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


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
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


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
def image_building(request):
    """
    Event that happens when a image started to build

    name -- Image name
    project -- Pre-release project name
    """
    form = ImageBuildingForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)

    data = form.cleaned_data

    group = data['project']
    group.status = '20_IMGBUILDING'
    group.save()

    ibuild = ImageBuild(name=data['name'],
                        status='BUILDING',
                        group=group)
    ibuild.save()
    return Response({'detail': 'Image started to build'},
                    status=HTTP_200_OK)


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
def image_created(request):
    """
    Event that happends when a image created

    name -- Image name
    project -- Pre-release project name
    status -- status
    url -- Image URL
    """
    form = ImageCreatedForm(request.POST)
    if not form.is_valid():
        return Response({'detail': form.errors.as_text()},
                        status=HTTP_406_NOT_ACCEPTABLE)

    data = form.cleaned_data
    print data
    ok = data['status'] == 'success'

    group = data['project']
    if ok:
        group.status = '30_READY'
    else:
        group.status = '25_IMGFAILED'
    group.save()

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


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
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
    return Response({'detail': 'Action %s received' % data['status']},
                    status=HTTP_200_OK)
