from django.core.management.base import BaseCommand, CommandError

from ...consumer import Consumer
from edc_sync.models import IncomingTransaction


class Command(BaseCommand):

    args = ('--consume <app_name> --model <model_name> --<producer_name>')
    help = 'Use --consume <app_name> for all transactions --consume <app_name> --model <model_name> for specific model only,\
            --consume <app_name> --model <model_name> --producer <producer_name> for specific producer only'

    def add_arguments(self, parser):
        parser.add_argument('args', metavar=self.args, nargs='+', help='Fixture labels.')
        parser.add_argument(
            '--consume',
            action='store_true',
            dest='consume',
            default=False,
            help=('Show history of data import for lock name.'))

        parser.add_argument(
            '--model',
            action='store_true',
            dest='model',
            default=False,
            help=('Specify model to consume transactions of that model only.'))

        parser.add_argument(
            '--producer',
            action='store_true',
            dest='producer',
            default=False,
            help=('Specify producer name to consume transactions of that producer only.'))

        parser.add_argument(
            '--batch',
            action='store_true',
            dest='batch',
            default=False,
            help=('Specify batch id to consume transactions.'))

    def handle(self, *args, **options):
        print(args, ">>>>>>>>>>>>>>>.", options)
        if not args:
            args = [None]
        if options.get('model', None) and not options.get('producer', None):
            model_name = args[1]
            if len(args) != 2:
                raise CommandError('if using --consume<app_name> --model <Model_name>, then only 2 arguments are expected')
            self.consume(model_name=model_name)
        elif options.get('producer', None) and not options.get('model', None):
            producer_name = args[1]
            if len(args) != 2:
                raise CommandError('if using --consume<app_name> --producer <producer_name>, then only 2 arguments are expected')
            self.consume(producer_name=producer_name)
        elif options.get('producer', None) and options.get('model', None):
            model_name = args[1]
            producer_name = args[2]
            if len(args) != 3:
                raise CommandError('if using --consume<app_name> --model <Model_name> --producer <producer_name> then only 2 arguments are expected')
            self.consume(model_name=model_name, producer_name=producer_name)
        elif options.get('consume') and not options.get('model', None) and not options.get('producer', None):
            if len(args) != 1:
                raise CommandError('if using --consume<app_name> only, then only 1 argument is expected')
            self.consume()
        elif options.get('batch', None):
            if len(args) != 2:
                raise CommandError('if using --consume<app_name> --batch <batch>, then only 2 arguments are expected')
            batch_id = args[1]
            transactions = IncomingTransaction.objects.filter(
                batch_id=batch_id)
            Consumer(transactions=transactions).consume()
            self.stdout.write(self.style.SUCCESS('Completed playing of transactions.'))
        else:
            self.stdout.write(self.style.ERROR('Unknown option, Try --help for a list of valid options.'))

    @property
    def consumer(self):
        """Returns the consumer class instances.

        Users should override to provide an app specific consumer."""
        return Consumer()

    def consume(self, transactions=None, model_name=None, producer_name=None):
        return Consumer().consume(model_name=model_name, producer_name=producer_name)
