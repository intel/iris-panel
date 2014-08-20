# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Django settings for the iris-core project.
"""

# pylint: disable=C0103,F0401,W0611,W0703
import os
from os import path
from sys import prefix, argv
from pkg_resources import iter_entry_points
from django.conf import global_settings

# ConfigParser was renamed to configparser in Python 3
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1', 'localhost')

ADMINS = (
    ('Eduard Bartosh', 'eduard.bartosh@intel.com'),
    ('Hao Huang', 'hao.h.huang@intel.com'),
    ('Jing-Fiang Deng', 'jian-feng.ding@intel.com'),
    ('Gao XueSong', 'xuesongx.gao@intel.com'),
)

MANAGERS = ADMINS

SQLITE_DB_FILE = path.join(path.expanduser('~'), '.cache', 'iris.db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SQLITE_DB_FILE,

        # The following settings are not used with SQLite
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
        }
    }
}

ALLOWED_HOSTS = ['*']

TIME_ZONE = 'Europe/Helsinki'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Please adjust MEDIA_ROOT and STATIC_ROOT in /etc/iris/iris.conf
# They are used for collecting static files for the appropriate user
# To be served by your distributions web server
# The folder needs to be writable by the user doing the collecting
PROJECT_FOLDER = path.realpath(path.dirname(__file__))
MEDIA_ROOT = '/srv/www/iris/media'
STATIC_ROOT = '/srv/www/iris/static'

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
LOGIN_URL = '/login/'
ROOT_URLCONF = 'iris.core.urls'
WSGI_APPLICATION = 'iris.core.wsgi.application'

STATICFILES_DIRS = (
)

TEMPLATE_DIRS = (

)

for plugin in iter_entry_points(group='iris.app'):
    template_dirs = plugin.load().get('template_dirs', ())
    TEMPLATE_DIRS += template_dirs

    print('Loaded application template directories: ')
    print(template_dirs)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'south',
    'iris.core',
)

for plugin in iter_entry_points(group='iris.app'):
    installed_apps = plugin.load().get('installed_apps', ())
    INSTALLED_APPS += installed_apps

    print('Loaded applications: ')
    print(installed_apps)

SECRET_KEY = '(e0wp@h7-@_p_&u99vi9&$jju+#=b&yyv9@0uqp!8#z#fiyb1!'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
AUTH_PROFILE_MODULE = 'iris.core.models.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s|%(name)s|%(message)s',
        }
    },
    'handlers': {
        # Development handler logs only when DEBUG=True
        'development':{
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # Production handler logs only when DEBUG=False
        'production':{
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'iris': {
            # Log from lowest level in development and production
            # Filter logging mode and level on handler levels
            'handlers': ['development', 'production'],
            'level': 'DEBUG'
        },
        'django_auth_ldap': {
            'handlers': ['development', 'production'],
            'level': 'DEBUG',
        },
        'scm_update': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# UI_AVAILABLE and REST_API_AVAILABLE are flags for the IRIS specifically.
# They control whether or not to expose web components to the client.
# Unsetting REST_API_AVAILABLE removes/allows REST API components from use:
#   - REST API URLs
#   - REST Framework web views
#   - Swagger API documentation
# Unsetting UI_AVAILABLE removes/allows web UI components:
#   - Basic CRUD URL actions
#   - Application web views and forms

UI_AVAILABLE = True
REST_API_AVAILABLE = True

# Secret key should be read from an external file for security reasons.
# Please DO NOT expose this file to anybody after setting it in production.
# Consult documentation for the proper secret key format.

KEYFILE = '/etc/iris/secret.txt'

if path.isfile(KEYFILE) and os.access(KEYFILE, os.R_OK):
    with open(KEYFILE) as secret:
        SECRET_KEY = secret.read()

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'core.context_processors.version',
    )

# Attempt to load overrides to common settings.
# Settings in /etc/iris/iris.conf are pure Python code
# and will be executed in this settings file's context.
# If the file does not exist, we will simply skip this stage.
# If the file contains syntax errors, we crash early.

CONFIG_FILE = '/etc/iris/iris.conf'

try:
    execfile(CONFIG_FILE)
except IOError as e:
    print('Skipping settings loading, no file at %s' % CONFIG_FILE)
except SyntaxError as e:
    print('Invalid syntax in configuration at %s' % CONFIG_FILE)
    raise(e)

# If we have RESTful API or UI components set available, attempt to load them.

if REST_API_AVAILABLE:
    try:
        import rest_framework, rest_framework_swagger

        INSTALLED_APPS += (
            'rest_framework',
            'rest_framework_swagger'
        )

        REST_FRAMEWORK = {
            'DEFAULT_PERMISSION_CLASSES': (
                'rest_framework.permissions.IsAuthenticated',
            ),
        }

        SWAGGER_SETTINGS = {
            "api_version": '0.0.1',
            "api_path": "/",
            "enabled_methods": ['get', 'post', 'put', 'patch', 'delete'],
            "is_authenticated": True,
        }

        print('Loaded RESTful API and documentation')
    except ImportError:
        print('Could not load RESTful API')

if UI_AVAILABLE:
    try:
        import crispy_forms

        INSTALLED_APPS += (
            'crispy_forms',
        )

        CRISPY_TEMPLATE_PACK = 'bootstrap3'

        print('Loaded web UI components')
    except ImportError:
        print('Could not load web UI components')

# If running in test mode, make the database import testing faster
if 'test' in argv:
    print('Using test database, skipping migrations')
    SOUTH_TESTS_MIGRATE = False
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

    INSTALLED_APPS += ('django_nose',)

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS\
        + ("django.core.context_processors.request",)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
