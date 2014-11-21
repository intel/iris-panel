"""
All forms for events views
"""
from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from iris.core.models import (
    GitTree, Product, Package,
    Submission, BuildGroup, ImageBuild, SubmissionBuild,
    Snapshot
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
        user, _created = User.objects.get_or_create(email=email, defaults={
                'username': email,
                })
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
        group, _created = BuildGroup.objects.get_or_create(
            name=project, defaults={'status': '10_PKGBUILDING'})
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
            # make sure only one product related with one pre-release project
            if 'product' in data and 'project' in data:
                product = data['product']
                project = data['project']
                smbs = SubmissionBuild.objects.filter(submission__name=sub.name,
                                                    group=project)
                if len(smbs) > 0 and smbs[0].product != product:
                    raise forms.ValidationError(
                        "product must be the same in one pre-release project"
                    )

            return data


class PackageBuiltForm(forms.Form):

    name = forms.CharField(label="Package name")
    repo = forms.CharField(label="Building repository name")
    arch = forms.CharField(label="Building architecture")
    project = forms.CharField(label="Pre-release project name")
    status = forms.ChoiceField(choices=(
            ('OBS_BUILD_SUCCESS', 'SUCCESS'),
            ('OBS_BUILD_FAIL', 'FAILURE')
            ), label="Status")
    repo_server = forms.CharField(label="Repository URL")

    def clean_name(self):
        name = self.cleaned_data['name']
        pack, _created = Package.objects.get_or_create(name=name)
        return pack

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

    def clean_status(self):
        if 'success' in self.cleaned_data['status'].lower():
            return 'SUCCESS'
        return 'FAILURE'


class ImageBuildingForm(forms.Form):

    name = forms.CharField(label="Image name")
    project = forms.CharField(label="Pre-release project name")
    repo = forms.CharField(label="Building repository")
    #arch = forms.CharField(label="Building architecture")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))


class ImageCreatedForm(forms.Form):

    name = forms.CharField(label="Image name")
    project = forms.CharField(label="Pre-release project name")
    status = forms.CharField(label="Build status")
    url = forms.URLField(label="Image URL")
    #log = forms.URLField(label="Image building log URL")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return BuildGroup.objects.get(name=project)
        except BuildGroup.DoesNotExist as err:
            raise ValidationError(str(err))

    def clean_status(self):
        if 'success' in self.cleaned_data['status'].lower():
            return 'SUCCESS'
        return 'FAILURE'

    def clean(self):
        if 'project' not in self.cleaned_data:
            return self.cleaned_data

        try:
            ibuild = ImageBuild.objects.get(
                name=self.cleaned_data['name'],
                group=self.cleaned_data['project'])
        except ImageBuild.DoesNotExist as err:
            raise ValidationError(str(err))

        #ibuild.log = data['log']
        if self.cleaned_data['status'] == 'SUCCESS':
            ibuild.url = self.cleaned_data['url']
            ibuild.status = 'SUCCESS'
        else:
            ibuild.status = 'FAILURE'

        self.cleaned_data['name'] = ibuild
        return self.cleaned_data


class RepaActionForm(forms.Form):

    project = forms.CharField(label="Pre-release project name")
    status = forms.ChoiceField(choices=(
            ('accepted', 'accepted'),
            ('declined', 'rejected'),
            ), label="Accepted or rejected")
    who = forms.CharField(label="Operator's Email")
    reason = forms.CharField(label="Explanation")

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


class SnapshotStartForm(forms.Form):
    buildid = forms.CharField(label="build id")
    started_time = forms.DateTimeField()
    project= forms.CharField(label="Target project name")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return Product.objects.get(name=project)
        except Product.DoesNotExist as err:
            raise forms.ValidationError(str(err))


class SnapshotFinishedForm(forms.Form):
    buildid = forms.CharField(label="build id")
    finished_time = forms.DateTimeField()
    project= forms.CharField(label="Target project name")
    url = forms.URLField(label="Snapshot URL")

    def clean_project(self):
        project = self.cleaned_data['project']
        try:
            return Product.objects.get(name=project)
        except Product.DoesNotExist as err:
            raise forms.ValidationError(str(err))

    def clean(self):
        if 'buildid' in self.cleaned_data and 'project' in self.cleaned_data:
            buildid = self.cleaned_data['buildid']
            product = self.cleaned_data['project']
            try:
                Snapshot.objects.get(product=product, buildid=buildid)
            except Snapshot.DoesNotExist as err:
                raise forms.ValidationError(
                "No matched snapshot start for snpshot finish with buildid:\
 %s, project: %s" % (buildid, product.name)
            )
        return self.cleaned_data
