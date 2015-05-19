from datetime import datetime, timedelta
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import OutgoingTransaction, IncomingTransaction


class Command(BaseCommand):

    args = ('num_days')
    help = 'Purge transactions already consumed. '
    option_list = BaseCommand.option_list + (
        make_option('--incoming',
            action='store_true',
            dest='incoming',
            default=False,
            help=('Purge incoming transactions.')),
         )
    option_list += (
        make_option('--outgoing',
            action='store_true',
            dest='outgoing',
            default=False,
            help=('Purge outgoing transactions.')),
        )

    def handle(self, *args, **options):
        if not args:
            args = [None]
        if options['incoming']:
            self.purge_incoming(*args)
        elif options['outgoing']:
            self.purge_outgoing(*args)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    def purge_incoming(self, *args):
        n = 0
        # in days
        age = 0
        if args[0]:
            if args[0].isdigit():
                value = float(args[0])
                if value > 0:
                    age = int(value)
        print "Deleting incoming transaction older than {0} day(s)".format(age)
        cut_off_date = datetime.now() - timedelta(days=age)
        transactions = IncomingTransaction.objects.filter(
                            tx_name="ScheduledEntryMetaData",
                        )
        tot = transactions.count()
        if tot == 0:
            print "    No transactions older than {0} were found".format(cut_off_date)
        else:
            for incoming_transaction in transactions:
                n += 1
                print '{0} / {1} {2} {3}'.format(
                    n,
                    tot,
                    incoming_transaction.producer,
                    incoming_transaction.tx_name)

                incoming_transaction.save(using='archive')
                print '    Saved on the archive db'

                incoming_transaction.delete(using='default')
                print '    Deleted from local db'
    '''
        Delete all outgoing transaction older than the specified number of days
        (default=0). If we are on a netbook delete only those that have been
        consumed.
    '''
    def purge_outgoing(self, *args):
        n = 0
        transactions = None
        is_server = True
        # in days
        age = 0

        if args:
            if args[0].isdigit():
                value = float(args[0])
                if value > 0:
                    age = int(value)
        print "Deleting outgoing transaction older than {0} day(s)".format(age)
        cutoff_date = datetime.now() - timedelta(days=age)
        if 'DEVICE_ID' in dir(settings):
            if settings.DEVICE_ID.isdigit():
                if float(settings.DEVICE_ID) >= 98:
                    # We are on a server
                    transactions = OutgoingTransaction.objects.filter(created__lte=cutoff_date)
                else:
                    raise ValueError('The command should on be ran on server! .')
                for outgoing_transaction in transactions:
                    n += 1
                    print '{0} / {1} {2}'.format(n, outgoing_transaction.producer, outgoing_transaction.tx_name)
                    if is_server == True:
                        outgoing_transaction.save(using='archive')
                        print '    Saved on the archive db'
                    outgoing_transaction.delete(using='default')
                    print '    Deleted'
            else:
                raise ValueError('DEVICE_ID global value should be a number .')
        else:
            raise ValueError('DEVICE_ID global value should be set on the settings.py file.')
