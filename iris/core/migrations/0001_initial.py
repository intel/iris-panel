# -*- coding: utf-8 -*-
#pylint: skip-file
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Domain'
        db.create_table(u'core_domain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('core', ['Domain'])

        # Adding model 'SubDomain'
        db.create_table(u'core_subdomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Domain'])),
        ))
        db.send_create_signal('core', ['SubDomain'])

        # Adding unique constraint on 'SubDomain', fields ['name', 'domain']
        db.create_unique(u'core_subdomain', ['name', 'domain_id'])

        # Adding model 'License'
        db.create_table(u'core_license', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['License'])

        # Adding model 'GitTree'
        db.create_table(u'core_gittree', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gitpath', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('subdomain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubDomain'])),
        ))
        db.send_create_signal('core', ['GitTree'])

        # Adding M2M table for field licenses on 'GitTree'
        db.create_table(u'core_gittree_licenses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gittree', models.ForeignKey(orm['core.gittree'], null=False)),
            ('license', models.ForeignKey(orm['core.license'], null=False))
        ))
        db.create_unique(u'core_gittree_licenses', ['gittree_id', 'license_id'])

        # Adding model 'Package'
        db.create_table(u'core_package', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('gittree', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.GitTree'])),
        ))
        db.send_create_signal('core', ['Package'])

        # Adding unique constraint on 'Package', fields ['name', 'gittree']
        db.create_unique(u'core_package', ['name', 'gittree_id'])

        # Adding model 'Product'
        db.create_table(u'core_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Product'])

        # Adding M2M table for field gittrees on 'Product'
        db.create_table(u'core_product_gittrees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['core.product'], null=False)),
            ('gittree', models.ForeignKey(orm['core.gittree'], null=False))
        ))
        db.create_unique(u'core_product_gittrees', ['product_id', 'gittree_id'])

        # Adding model 'Image'
        db.create_table(u'core_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('target', self.gf('django.db.models.fields.TextField')()),
            ('arch', self.gf('django.db.models.fields.TextField')()),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'])),
        ))
        db.send_create_signal('core', ['Image'])

        # Adding model 'Log'
        db.create_table(u'core_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Log'])

        # Adding model 'PackageBuild'
        db.create_table(u'core_packagebuild', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Package'])),
            ('target', self.gf('django.db.models.fields.TextField')()),
            ('arch', self.gf('django.db.models.fields.TextField')()),
            ('log', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Log'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('core', ['PackageBuild'])

        # Adding model 'ImageBuild'
        db.create_table(u'core_imagebuild', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Image'])),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('log', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Log'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('core', ['ImageBuild'])

        # Adding model 'TestResult'
        db.create_table(u'core_testresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('log', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Log'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('core', ['TestResult'])

        # Adding model 'Submission'
        db.create_table(u'core_submission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, db_index=True)),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['Submission'])

        # Adding M2M table for field gittree on 'Submission'
        db.create_table(u'core_submission_gittree', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('gittree', models.ForeignKey(orm['core.gittree'], null=False))
        ))
        db.create_unique(u'core_submission_gittree', ['submission_id', 'gittree_id'])

        # Adding M2M table for field pbuilds on 'Submission'
        db.create_table(u'core_submission_pbuilds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('packagebuild', models.ForeignKey(orm['core.packagebuild'], null=False))
        ))
        db.create_unique(u'core_submission_pbuilds', ['submission_id', 'packagebuild_id'])

        # Adding M2M table for field ibuilds on 'Submission'
        db.create_table(u'core_submission_ibuilds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('imagebuild', models.ForeignKey(orm['core.imagebuild'], null=False))
        ))
        db.create_unique(u'core_submission_ibuilds', ['submission_id', 'imagebuild_id'])

        # Adding M2M table for field testresults on 'Submission'
        db.create_table(u'core_submission_testresults', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('testresult', models.ForeignKey(orm['core.testresult'], null=False))
        ))
        db.create_unique(u'core_submission_testresults', ['submission_id', 'testresult_id'])

        # Adding M2M table for field submitters on 'Submission'
        db.create_table(u'core_submission_submitters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(u'core_submission_submitters', ['submission_id', 'user_id'])

        # Adding model 'SubmissionGroup'
        db.create_table(u'core_submissiongroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, db_index=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('core', ['SubmissionGroup'])

        # Adding M2M table for field submissions on 'SubmissionGroup'
        db.create_table(u'core_submissiongroup_submissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissiongroup', models.ForeignKey(orm['core.submissiongroup'], null=False)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False))
        ))
        db.create_unique(u'core_submissiongroup_submissions', ['submissiongroup_id', 'submission_id'])

        # Adding model 'UserProfile'
        db.create_table(u'core_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('core', ['UserProfile'])

        # Adding model 'UserParty'
        db.create_table(u'core_userparty', (
            (u'group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('core', ['UserParty'])

        # Adding model 'ProductRole'
        db.create_table(u'core_productrole', (
            (u'group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'])),
        ))
        db.send_create_signal('core', ['ProductRole'])

        # Adding model 'DomainRole'
        db.create_table(u'core_domainrole', (
            (u'group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='role_set', to=orm['core.Domain'])),
        ))
        db.send_create_signal('core', ['DomainRole'])

        # Adding model 'SubDomainRole'
        db.create_table(u'core_subdomainrole', (
            (u'group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('subdomain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubDomain'])),
        ))
        db.send_create_signal('core', ['SubDomainRole'])

        # Adding model 'GitTreeRole'
        db.create_table(u'core_gittreerole', (
            (u'group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('gittree', self.gf('django.db.models.fields.related.ForeignKey')(related_name='role_set', to=orm['core.GitTree'])),
        ))
        db.send_create_signal('core', ['GitTreeRole'])


    def backwards(self, orm):
        # Removing unique constraint on 'Package', fields ['name', 'gittree']
        db.delete_unique(u'core_package', ['name', 'gittree_id'])

        # Removing unique constraint on 'SubDomain', fields ['name', 'domain']
        db.delete_unique(u'core_subdomain', ['name', 'domain_id'])

        # Deleting model 'Domain'
        db.delete_table(u'core_domain')

        # Deleting model 'SubDomain'
        db.delete_table(u'core_subdomain')

        # Deleting model 'License'
        db.delete_table(u'core_license')

        # Deleting model 'GitTree'
        db.delete_table(u'core_gittree')

        # Removing M2M table for field licenses on 'GitTree'
        db.delete_table('core_gittree_licenses')

        # Deleting model 'Package'
        db.delete_table(u'core_package')

        # Deleting model 'Product'
        db.delete_table(u'core_product')

        # Removing M2M table for field gittrees on 'Product'
        db.delete_table('core_product_gittrees')

        # Deleting model 'Image'
        db.delete_table(u'core_image')

        # Deleting model 'Log'
        db.delete_table(u'core_log')

        # Deleting model 'PackageBuild'
        db.delete_table(u'core_packagebuild')

        # Deleting model 'ImageBuild'
        db.delete_table(u'core_imagebuild')

        # Deleting model 'TestResult'
        db.delete_table(u'core_testresult')

        # Deleting model 'Submission'
        db.delete_table(u'core_submission')

        # Removing M2M table for field gittree on 'Submission'
        db.delete_table('core_submission_gittree')

        # Removing M2M table for field pbuilds on 'Submission'
        db.delete_table('core_submission_pbuilds')

        # Removing M2M table for field ibuilds on 'Submission'
        db.delete_table('core_submission_ibuilds')

        # Removing M2M table for field testresults on 'Submission'
        db.delete_table('core_submission_testresults')

        # Removing M2M table for field submitters on 'Submission'
        db.delete_table('core_submission_submitters')

        # Deleting model 'SubmissionGroup'
        db.delete_table(u'core_submissiongroup')

        # Removing M2M table for field submissions on 'SubmissionGroup'
        db.delete_table('core_submissiongroup_submissions')

        # Deleting model 'UserProfile'
        db.delete_table(u'core_userprofile')

        # Deleting model 'UserParty'
        db.delete_table(u'core_userparty')

        # Deleting model 'ProductRole'
        db.delete_table(u'core_productrole')

        # Deleting model 'DomainRole'
        db.delete_table(u'core_domainrole')

        # Deleting model 'SubDomainRole'
        db.delete_table(u'core_subdomainrole')

        # Deleting model 'GitTreeRole'
        db.delete_table(u'core_gittreerole')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '225'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.domain': {
            'Meta': {'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.domainrole': {
            'Meta': {'object_name': 'DomainRole', '_ormbases': [u'auth.Group']},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_set'", 'to': "orm['core.Domain']"}),
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'core.gittree': {
            'Meta': {'object_name': 'GitTree'},
            'gitpath': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.License']", 'symmetrical': 'False'}),
            'subdomain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubDomain']"})
        },
        'core.gittreerole': {
            'Meta': {'object_name': 'GitTreeRole', '_ormbases': [u'auth.Group']},
            'gittree': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_set'", 'to': "orm['core.GitTree']"}),
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'core.image': {
            'Meta': {'object_name': 'Image'},
            'arch': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']"}),
            'target': ('django.db.models.fields.TextField', [], {})
        },
        'core.imagebuild': {
            'Meta': {'object_name': 'ImageBuild'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Image']"}),
            'log': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Log']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'core.license': {
            'Meta': {'object_name': 'License'},
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'core.log': {
            'Meta': {'object_name': 'Log'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.package': {
            'Meta': {'unique_together': "(('name', 'gittree'),)", 'object_name': 'Package'},
            'gittree': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.GitTree']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'core.packagebuild': {
            'Meta': {'object_name': 'PackageBuild'},
            'arch': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Log']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Package']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'target': ('django.db.models.fields.TextField', [], {})
        },
        'core.product': {
            'Meta': {'object_name': 'Product'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'gittrees': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.GitTree']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'core.productrole': {
            'Meta': {'object_name': 'ProductRole', '_ormbases': [u'auth.Group']},
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'core.subdomain': {
            'Meta': {'unique_together': "(('name', 'domain'),)", 'object_name': 'SubDomain'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'core.subdomainrole': {
            'Meta': {'object_name': 'SubDomainRole', '_ormbases': [u'auth.Group']},
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'subdomain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubDomain']"})
        },
        'core.submission': {
            'Meta': {'object_name': 'Submission'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gittree': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.GitTree']", 'symmetrical': 'False', 'blank': 'True'}),
            'ibuilds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.ImageBuild']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'db_index': 'True'}),
            'pbuilds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.PackageBuild']", 'symmetrical': 'False', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'submitters': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'testresults': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.TestResult']", 'symmetrical': 'False', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.submissiongroup': {
            'Meta': {'object_name': 'SubmissionGroup'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'db_index': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Submission']", 'symmetrical': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.testresult': {
            'Meta': {'object_name': 'TestResult'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Log']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'core.userparty': {
            'Meta': {'object_name': 'UserParty', '_ormbases': [u'auth.Group']},
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['core']
