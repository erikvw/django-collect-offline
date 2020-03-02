from django.conf import settings

from .parsers import datetime_to_date_parser


def get_offline_enabled():
    return getattr(settings, "DJANGO_COLLECT_OFFLINE_ENABLED", False)
