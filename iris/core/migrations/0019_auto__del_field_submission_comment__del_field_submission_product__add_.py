# -*- coding: utf-8 -*-
# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
#pylint: skip-file
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Submission.comment'
        db.delete_column(u'core_submission', 'comment')

        # Deleting field 'Submission.product'
        db.delete_column(u'core_submission', 'product_id')

        # Adding field 'Submission.owner'
        db.add_column(u'core_submission', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Submission.gittree'
        db.add_column(u'core_submission', 'gittree',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.GitTree']),
                      keep_default=False)

        # Removing M2M table for field gittree on 'Submission'
        db.delete_table(db.shorten_name(u'core_submission_gittree'))

        # Removing M2M table for field pbuilds on 'Submission'
        db.delete_table(db.shorten_name(u'core_submission_pbuilds'))

        # Removing M2M table for field ibuilds on 'Submission'
        db.delete_table(db.shorten_name(u'core_submission_ibuilds'))

        # Removing M2M table for field submitters on 'Submission'
        db.delete_table(db.shorten_name(u'core_submission_submitters'))


        # Changing field 'Submission.status'
        db.alter_column(u'core_submission', 'status', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'Submission.name'
        db.alter_column(u'core_submission', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Submission.commit'
        db.alter_column(u'core_submission', 'commit', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding index on 'Submission', fields ['commit']
        db.create_index(u'core_submission', ['commit'])

        # Adding unique constraint on 'Submission', fields ['name', 'gittree']
        db.create_unique(u'core_submission', ['name', 'gittree_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Submission', fields ['name', 'gittree']
        db.delete_unique(u'core_submission', ['name', 'gittree_id'])

        # Removing index on 'Submission', fields ['commit']
        db.delete_index(u'core_submission', ['commit'])

        # Adding field 'Submission.comment'
        db.add_column(u'core_submission', 'comment',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Submission.product'
        db.add_column(u'core_submission', 'product',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'], null=True, on_delete=models.SET_NULL, blank=True),
                      keep_default=False)

        # Deleting field 'Submission.owner'
        db.delete_column(u'core_submission', 'owner_id')

        # Deleting field 'Submission.gittree'
        db.delete_column(u'core_submission', 'gittree_id')

        # Adding M2M table for field gittree on 'Submission'
        m2m_table_name = db.shorten_name(u'core_submission_gittree')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('gittree', models.ForeignKey(orm['core.gittree'], null=False))
        ))
        db.create_unique(m2m_table_name, ['submission_id', 'gittree_id'])

        # Adding M2M table for field pbuilds on 'Submission'
        m2m_table_name = db.shorten_name(u'core_submission_pbuilds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('packagebuild', models.ForeignKey(orm['core.packagebuild'], null=False))
        ))
        db.create_unique(m2m_table_name, ['submission_id', 'packagebuild_id'])

        # Adding M2M table for field ibuilds on 'Submission'
        m2m_table_name = db.shorten_name(u'core_submission_ibuilds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('imagebuild', models.ForeignKey(orm['core.imagebuild'], null=False))
        ))
        db.create_unique(m2m_table_name, ['submission_id', 'imagebuild_id'])

        # Adding M2M table for field submitters on 'Submission'
        m2m_table_name = db.shorten_name(u'core_submission_submitters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['submission_id', 'user_id'])


        # Changing field 'Submission.status'
        db.alter_column(u'core_submission', 'status', self.gf('django.db.models.fields.CharField')(max_length=16))

        # Changing field 'Submission.name'
        db.alter_column(u'core_submission', 'name', self.gf('django.db.models.fields.CharField')(max_length=80))

        # Changing field 'Submission.commit'
        db.alter_column(u'core_submission', 'commit', self.gf('django.db.models.fields.CharField')(max_length=40))

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
        'core.buildgroup': {
            'Meta': {'object_name': 'BuildGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'operate_reason': ('django.db.models.fields.TextField', [], {}),
            'operated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'operator': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'snapshot': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.domain': {
            'Meta': {'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.domainrole': {
            'Meta': {'unique_together': "(('role', 'domain'),)", 'object_name': 'DomainRole', '_ormbases': [u'auth.Group']},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_set'", 'to': "orm['core.Domain']"}),
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'core.gittree': {
            'Meta': {'object_name': 'GitTree'},
            'gitpath': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.License']", 'symmetrical': 'False'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Package']", 'symmetrical': 'False'}),
            'subdomain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubDomain']"})
        },
        'core.gittreerole': {
            'Meta': {'unique_together': "(('role', 'gittree'),)", 'object_name': 'GitTreeRole', '_ormbases': [u'auth.Group']},
            'gittree': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_set'", 'to': "orm['core.GitTree']"}),
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'core.image': {
            'Meta': {'unique_together': "(('name', 'target', 'product'),)", 'object_name': 'Image'},
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']"}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.imagebuild': {
            'Meta': {'unique_together': "(('name', 'group'),)", 'object_name': 'ImageBuild'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BuildGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'repo': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.license': {
            'Meta': {'object_name': 'License'},
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'core.package': {
            'Meta': {'object_name': 'Package'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.packagebuild': {
            'Meta': {'unique_together': "(('package', 'repo', 'arch', 'group'),)", 'object_name': 'PackageBuild'},
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BuildGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Package']"}),
            'repo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.product': {
            'Meta': {'object_name': 'Product'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'gittrees': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.GitTree']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.subdomain': {
            'Meta': {'unique_together': "(('name', 'domain'),)", 'object_name': 'SubDomain'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'core.subdomainrole': {
            'Meta': {'unique_together': "(('role', 'subdomain'),)", 'object_name': 'SubDomainRole', '_ormbases': [u'auth.Group']},
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'subdomain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubDomain']"})
        },
        'core.submission': {
            'Meta': {'unique_together': "(('name', 'gittree'),)", 'object_name': 'Submission'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gittree': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.GitTree']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.userparty': {
            'Meta': {'object_name': 'UserParty', '_ormbases': [u'auth.Group']},
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['core']
