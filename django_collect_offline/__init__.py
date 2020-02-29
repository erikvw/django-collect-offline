from django.conf import settings

from .parsers import datetime_to_date_parser

DJANGO_COLLECT_OFFLINE_ENABLED = getattr(
    settings, "DJANGO_COLLECT_OFFLINE_ENABLED", False
)
