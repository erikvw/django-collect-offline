#!/usr/bin/env python
import django
import logging
import os
import sys

from django.conf import settings
from django.test.runner import DiscoverRunner
from edc_test_utils import DefaultTestSettings as Base
from os.path import abspath, dirname, join


class DefaultTestSettings(Base):
    def check_travis(self):
        if os.environ.get("TRAVIS"):
            self.settings.update(
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "edc_default",
                        "USER": "travis",
                        "PASSWORD": "",
                        "HOST": "localhost",
                        "PORT": "",
                    },
                    "server": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "edc_server",
                        "USER": "travis",
                        "PASSWORD": "",
                        "HOST": "localhost",
                        "PORT": "",
                    },
                    "client": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "edc_client",
                        "USER": "travis",
                        "PASSWORD": "",
                        "HOST": "localhost",
                        "PORT": "",
                    },
                    "test_server": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "edc_test_server",
                        "USER": "travis",
                        "PASSWORD": "",
                        "HOST": "localhost",
                        "PORT": "",
                    },
                }
            )


app_name = 'django_collect_offline'
base_dir = dirname(abspath(__file__))

DEFAULT_SETTINGS = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=os.path.join(base_dir, app_name, "tests", "etc"),
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django_crypto_fields.apps.AppConfig',
        'django_revision.apps.AppConfig',
        'rest_framework',
        'rest_framework.authtoken',
        'django_js_reverse',
        'simple_history',
        'edc_base.apps.AppConfig',
        'edc_protocol.apps.AppConfig',
        'edc_device.apps.AppConfig',
        'django_collect_offline_files.apps.AppConfig',
        'django_collect_offline.apps.AppConfig',
    ],
    DEVICE_ID='15',
    DATABASES={
        # required for tests when acting as a server that deserializes
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(base_dir, 'db.sqlite3'),
        },
        # required for tests when acting as a server but not attempting to
        # deserialize
        'server': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(base_dir, 'db.sqlite3'),
        },
        # required for tests when acting as a client
        'client': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(base_dir, 'db.sqlite3'),
        },
        'test_server': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(base_dir, 'db.sqlite3'),
        },
    },
    add_dashboard_middleware=True,
).settings


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    django.setup()
    failures = DiscoverRunner(failfast=True).run_tests(
        [f'{app_name}.tests'])
    sys.exit(failures)


if __name__ == "__main__":
    logging.basicConfig()
    main()
