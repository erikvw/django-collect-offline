from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...classes import Consumer


class Command(BaseCommand):

    args = ('--consume <app_name> --model <model_name> --<producer_name>')
    help = 'Use --consume <app_name> for all transactions --consume <app_name> --model <model_name> for specific model only,\
            --consume <app_name> --model <model_name> --producer <producer_name> for specific producer only'
    option_list = BaseCommand.option_list + (
        make_option(
            '--consume',
            action='store_true',
            dest='consume',
            default=False,
            help=('Show history of data import for lock name.')),
        make_option(
            '--model',
            action='store_true',
            dest='model',
            default=False,
            help=('Specify model to consume transactions of that model only.')),
        make_option(
            '--producer',
            action='store_true',
            dest='producer',
            default=False,
            help=('Specify producer name to consume transactions of that producer only.')),
        )

    def handle(self, *args, **options):
        lock_name = 'consume-{0}'.format(settings.APP_NAME)
        if not args:
            args = [None]
        if options.get('model', None) and not options.get('producer', None):
            model_name = args[1]
            if len(args) != 2:
                raise CommandError('if using --consume<app_name> --model <Model_name>, then only 2 arguments are expected')
            self.consume(lock_name, model_name=model_name)
        elif options.get('producer', None) and not options.get('model', None):
            producer_name = args[1]
            if len(args) != 2:
                raise CommandError('if using --consume<app_name> --producer <producer_name>, then only 2 arguments are expected')
            self.consume(lock_name, producer_name=producer_name)
        elif options.get('producer', None) and options.get('model', None):
            model_name = args[1]
            producer_name = args[2]
            if len(args) != 3:
                raise CommandError('if using --consume<app_name> --model <Model_name> --producer <producer_name> then only 2 arguments are expected')
            self.consume(lock_name, model_name=model_name, producer_name=producer_name)
        elif options['consume'] and not options.get('model', None) and not options.get('producer', None):
            if len(args) != 1:
                raise CommandError('if using --consume<app_name> only, then only 1 argument is expected')
            self.consume(lock_name)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    @property
    def consumer(self):
        """Returns the consumer class instances.

        Users should override to provide an app specific consumer."""
        return Consumer()

    def consume(self, lock_name, model_name=None, producer_name=None):
        return Consumer().consume(lock_name=lock_name, model_name=model_name, producer_name=producer_name)
