from edc_base.logging import verbose_formatter, file_handler


loggers = {
    'django_collect_offline': {
        'handlers': ['file'],
        'level': 'DEBUG',
        'propagate': True,
    }
}

file_handler['filename'] = f'/tmp/django_collect_offline.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': verbose_formatter,
    },
    'handlers': {
        'file': file_handler
    },
    'loggers': loggers,
}
