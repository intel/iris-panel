"""
All forms for events views
"""
import datetime

from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from iris.core.models import (
    GitTree, Product,
    Submission, BuildGroup, ImageBuild,
    )

# pylint: disable=C0111,E1101,W0232,E1002,R0903
# E1101: Instance of 'xx' has no 'cleaned_data' member
# W0232: Class has no __init__ method
# E1002: PreCreatedForm.clean: Use of super on an old style class
# R0903: PackageBuiltForm: Too few public methods (1/2)


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
                status='10_PKGBUILDING')
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


class PackageBuiltForm(forms.Form):

    name = forms.CharField(label="Package name")
    repo = forms.CharField(label="Building repository")
    arch = forms.CharField(label="Building architecture")
    project = forms.CharField(label="Pre-release project name")
    status = forms.ChoiceField(choices=(
            ('success', 'Success'),
            ('failure', 'Failure'),
            ))
    url = forms.URLField(label="Live repo URL")
    log = forms.URLField(label="Package building log URL")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

    def clean_status(self):
        return self.cleaned_data['status'].upper()

    def clean(self):
        group = self.cleaned_data['project']
        name = self.cleaned_data['name']
        sbuild = None
        for build in group.submissionbuild_set.all():
            if build.submission.gittree.gitpath.endswith(name):
                sbuild = build
                break

        if sbuild is None:
            raise ValidationError("Can't find corresponding submission build")
        self.cleaned_data['submission_build'] = sbuild
        return self.cleaned_data


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
            ('success', 'Success'),
            ('failure', 'Failure'),
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
