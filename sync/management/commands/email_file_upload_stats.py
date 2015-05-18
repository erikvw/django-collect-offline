from optparse import make_option

from django.db.models import get_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from ...classes.transaction_upload import TransactionUpload


class Command(BaseCommand):
    """ Sends an email to a list of recipients about the status of uploading transaction files
    """
    args = ('--success <comma_separated> --error <comma_separated> --email <comma_separated>')

    help = 'Email transaction file upload stats'

    option_list = BaseCommand.option_list + (
        make_option(
            '--success',
            dest='success',
            action='store_true',
            default=False,
            help=('Comma separated list of successfully uploaded files names.')),
        make_option(
            '--error',
            action='store_true',
            dest='error',
            default=False,
            help=('Comma separated list of files that failed to upload')),
         make_option(
            '--email',
            action='store_true',
            dest='email',
            default=False,
            help=('Comma separated list of reciepant\'s emails')),
        )

    def handle(self, *args, **options):
        email_sender = 'django@bhp.org.bw'
        UploadTransactionFile = get_model('import', 'UploadTransactionFile')
        missing_files = []
        if not len(args) == 3:
            raise CommandError('Please input arguments in this form--success <[]> --error <[]> --email <comma_separated>')
        if options['email'] and options['success'] and options['error']:
            subject, body, recipient_list = TransactionUpload().compile_upload_stats(args, UploadTransactionFile)
            #for producer in Producer.objects.filter(is_active=True):
            self.send_email(email_sender, subject, body, recipient_list)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')
        print "Successfully sent email to {0}".format(recipient_list)

    def send_email(self, email_sender, subject, body, recipient_list):
        send_mail(subject, body, email_sender, recipient_list, fail_silently=False)
