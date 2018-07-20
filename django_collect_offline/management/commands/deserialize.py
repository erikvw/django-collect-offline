import logging

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from ...transaction import CustomTransactionDeserializer


app_config = django_apps.get_app_config('django_collect_offline')
logger = logging.getLogger('django_collect_offline')


class Command(BaseCommand):
    """Usage:
        python manage.py deserialize --batch=9835201711152020
            --model=label_lower --order_by=created,producer
    """

    help = ('Deserialises transactions manually using '
            'different filter options.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            dest='model',
            default=None,
            help=('Specify the model name/tx name.'),
        )

        parser.add_argument(
            '--batch',
            dest='batch',
            default=None,
            help=('Specify batch.'),
        )

        parser.add_argument(
            '--order_by',
            dest='order_by',
            default='created',
            help=('Specify a field to order by e.g timestamp or created.'),
        )

        parser.add_argument(
            '--producer',
            dest='producer',
            default=None,
            help=('Specify a producer/client machine. e.g bcpp010'),
        )

    def handle(self, *args, **options):
        CustomTransactionDeserializer(**options)
