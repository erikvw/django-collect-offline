#!/usr/bin/env python3
import os
import sys
from unipath import Path

SOURCE_ROOT = Path(os.path.dirname(os.path.realpath(__file__))).ancestor(1)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sync.settings")
    sys.path.insert(1, SOURCE_ROOT.child('edc-base'))
    sys.path.insert(1, SOURCE_ROOT.child('django-revision'))
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
