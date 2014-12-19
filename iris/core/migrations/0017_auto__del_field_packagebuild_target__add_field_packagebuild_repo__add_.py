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
        # Deleting field 'PackageBuild.target'
        db.delete_column(u'core_packagebuild', 'target')

        # Adding field 'PackageBuild.repo'
        db.add_column(u'core_packagebuild', 'repo',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, db_index=True),
                      keep_default=False)

        # Adding field 'PackageBuild.group'
        db.add_column(u'core_packagebuild', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.BuildGroup']),
                      keep_default=False)

        # Adding field 'PackageBuild.url'
        db.add_column(u'core_packagebuild', 'url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'PackageBuild.log'
        db.add_column(u'core_packagebuild', 'log',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200),
                      keep_default=False)


        # Changing field 'PackageBuild.status'
        db.alter_column(u'core_packagebuild', 'status', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'PackageBuild.arch'
        db.alter_column(u'core_packagebuild', 'arch', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding index on 'PackageBuild', fields ['arch']
        db.create_index(u'core_packagebuild', ['arch'])

        # Adding unique constraint on 'PackageBuild', fields ['package', 'repo', 'arch', 'group']
        db.create_unique(u'core_packagebuild', ['package_id', 'repo', 'arch', 'group_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'PackageBuild', fields ['package', 'repo', 'arch', 'group']
        db.delete_unique(u'core_packagebuild', ['package_id', 'repo', 'arch', 'group_id'])

        # Removing index on 'PackageBuild', fields ['arch']
        db.delete_index(u'core_packagebuild', ['arch'])

        # Adding field 'PackageBuild.target'
        db.add_column(u'core_packagebuild', 'target',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Deleting field 'PackageBuild.repo'
        db.delete_column(u'core_packagebuild', 'repo')

        # Deleting field 'PackageBuild.group'
        db.delete_column(u'core_packagebuild', 'group_id')

        # Deleting field 'PackageBuild.url'
        db.delete_column(u'core_packagebuild', 'url')

        # Deleting field 'PackageBuild.log'
        db.delete_column(u'core_packagebuild', 'log')


        # Changing field 'PackageBuild.status'
        db.alter_column(u'core_packagebuild', 'status', self.gf('django.db.models.fields.CharField')(max_length=8))

        # Changing field 'PackageBuild.arch'
        db.alter_column(u'core_packagebuild', 'arch', self.gf('django.db.models.fields.TextField')())

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
            'Meta': {'object_name': 'ImageBuild'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Image']"}),
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
