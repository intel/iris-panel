# pylint: disable=C0111,E1101,W0703
from iris.core.models import GitTree, Submission

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


@atomic
@api_view(["POST"])
@permission_required('submissions.publish_events', raise_exception=True)
def submitted(request):
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
        return Response({'detail': str(err)}, status=HTTP_202_ACCEPTED)

    return Response({'detail': 'Tag submitted'}, status=HTTP_201_CREATED)
