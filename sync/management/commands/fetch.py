from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
# from edc.device.sync.classes import SyncLock, ImportHistory, Consumer
from edc.device.sync.classes import Consumer


class Command(BaseCommand):

#     args = ('--producer <producer_name> --list-locked <lock_name> --unlock <lock_name>')
    args = ('--producer <producer_name>')
    help = 'Fetch transactions from a producer and flag as consumed on the producer. '
    option_list = BaseCommand.option_list + (
        make_option('--producer',
            action='store_true',
            dest='producer',
            default=False,
            help=('Consume transactions from producer.')),
         )
#     option_list += (
#         make_option('--list-locked',
#             action='store_true',
#             dest='list-locked',
#             default=False,
#             help=('List all locks.')),
#          )
#     option_list += (
#         make_option('--unlock',
#             action='store_true',
#             dest='unlock',
#             default=False,
#             help=('Unlock for given lock name.')),
#         )
#     option_list += (
#         make_option('--show-history',
#             action='store_true',
#             dest='show_history',
#             default=False,
#             help=('Show history of data import for lock name.')),
#         )

    def handle(self, *args, **options):
#         db = 'default'
        if not args:
            args = [None]
#         sync_lock = SyncLock(db)
        if options['producer']:
            for producer_hostname in args:
                self.fetch(producer_hostname)
#         elif options['list-locked']:
#             for lock_name in args:
#                 self.list_locked(sync_lock, lock_name)
#         elif options['unlock']:
#             for lock_name in args:
#                 self.unlock(sync_lock, lock_name)
#         elif options['show_history']:
#             for lock_name in args:
#                 self.show_history(db, sync_lock, lock_name)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    def fetch(self, producer_hostname):
        consumer = Consumer()
        consumer.fetch_from_producer(producer_hostname)

#     def unlock(self, sync_lock, lock_name):
#         if lock_name:
#             sync_lock.release(lock_name)
#         else:
#             print 'Unable to released lock {0}. Try --list-locked for a list of valid locks.'.format(lock_name)
#
#     def list_locked(self, sync_lock, lock_name):
#         qs = sync_lock.list(lock_name)
#         if qs:
#             print 'Existing Locks:'
#             for q in qs:
#                 print '  {0} {1}'.format(q.lock_name, q.created)
#         else:
#             print 'No locks exist for lock name \'{0}\'.'.format(lock_name)
#
#     def show_history(self, db, lis_lock, lock_name):
#         history = ImportHistory(db, lock_name).history()
#         if not history:
#             print 'No import history for lock name \'{0}\''.format(lock_name)
#         else:
#             print 'Import History:'
#             print '  (lock name -- start -- finish)'
#             for h in history:
#                 print '  {0} {1} {2}'.format(h.lock_name, h.start_datetime, h.end_datetime or 'Open')
#         self.list_locked(lis_lock, lock_name)
