from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from ...utils import export_outgoing_transactions


class Command(BaseCommand):
    """ Exports currently unsynchronized outgoing transactions to json file
    """
    args = ('--path <full_qualified_path>')

    help = 'Export outgoing transactions to json file'

    option_list = BaseCommand.option_list + (
        make_option(
            '--path',
            dest='path',
            action='store_true',
            default=False,
            help=('Fully qualified path.')),
        )

    def handle(self, *args, **options):
        if len(args) == 0:
            exported, is_consumed_middleman_count = export_outgoing_transactions(None)
            print "Exported {0} outgoing transactions to /tmp".format(exported)
        elif options['path']:
            if not args or len(args) != 1:
                CommandError('Make sure you provide a single <path> argument')
            path = args[0]
            print path
            exported, is_consumed_middleman_count = export_outgoing_transactions(path)
            print "Exported {0} outgoing transactions to {1}".format(exported, path)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')
