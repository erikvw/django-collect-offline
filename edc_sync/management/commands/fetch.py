from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from edc_sync.classes import Consumer


class Command(BaseCommand):

    args = ('--producer <producer_name>')
    help = 'Fetch transactions from a producer and flag as consumed on the producer. '
    option_list = BaseCommand.option_list + (
        make_option(
            '--producer',
            action='store_true',
            dest='producer',
            default=False,
            help=('Consume transactions from producer.')))

    def handle(self, *args, **options):
        if not args:
            args = [None]
        if options['producer']:
            for producer_hostname in args:
                self.fetch(producer_hostname)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    def fetch(self, producer_hostname):
        consumer = Consumer()
        consumer.fetch_from_producer(producer_hostname)
