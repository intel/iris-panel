# pylint: disable=C0111,E1101,W0703
from iris.core.models import (
    GitTree, Product,
    Submission, SubmissionBuild, BuildGroup,
    )

from MySQLdb.constants.ER import DUP_ENTRY

from django import forms
from django.db import IntegrityError
from django.db.transaction import atomic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required

from rest_framework.status import (
    HTTP_201_CREATED, HTTP_202_ACCEPTED,
    HTTP_406_NOT_ACCEPTABLE,
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
