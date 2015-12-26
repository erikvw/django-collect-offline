from datetime import datetime
import socket
from optparse import make_option

from django.db.models import Count
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from ...models import IncomingTransaction


class Command(BaseCommand):
    """ Sends an email to a list of recipients if about incoming transactions status
    """
    args = ('--email <email> --body <email_body>')

    help = 'Email any sync alerts'

    option_list = BaseCommand.option_list + (
        make_option(
            '--email',
            dest='email',
            action='store_true',
            default=False,
            help=('Send an email nofication.')),
        )

    def handle(self, *args, **options):
        email_sender = 'django@bhp.org.bw'
        recipient_list = []
        tot = IncomingTransaction.objects.filter(is_consumed=False, is_ignored=False).count()
        body = "\nA summary of unconsumed incoming transactions"
        body += "\n{0} Incoming transactions\n".format(tot)
        body += "\nTotal:\t:Transaction name"
        body += "\n__________________________"
        for stat in self.stats:
            body += "\n{0}\t:{1}".format(stat['tx_count'], stat['tx_name'])
        body += "\n\t -------------------\t"

        if not args:
            CommandError('Invalid options, Try --help for a list of valid options')
        if options['email']:
            print args
            recipient_list = args[0].split(',')
            print "sending email to {0}".format(recipient_list)
            # TODO: if connection is not up the report will not be delivered
            # e.g. no retry -- what about using edc.notification
            self.send_email(email_sender, recipient_list, body)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')
        print "Successfully sent email to {0}".format(recipient_list)

    def send_email(self, email_sender, recipient_list, body):
        subject = "{}: incoming tx report for {}".format(socket.gethostname(),
                                                         datetime.today().strftime('%Y%m%d%H%M'),)
        send_mail(subject, body, email_sender, recipient_list, fail_silently=False)

    @property
    def stats(self):
        return IncomingTransaction.objects.values('tx_name').filter(
            is_consumed=False, is_ignored=False
            ).annotate(
                tx_count=Count('tx_name')
                ).order_by('tx_name')
