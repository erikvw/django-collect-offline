from datetime import datetime, timedelta
from django.db.models import get_model
import socket
from datetime import date
#from dateutil import rrule, parser

from edc.utils.models import ShortenIdentifierName


class TransactionUpload(object):

    def compile_upload_stats(self, args, upload_file_model):
        sucess_list = args[0].split(',')
        error_list = args[1].split(',')
        files_status = None
        missing_files = self.get_missing_files()
        if missing_files == "":
            files_status = 'ALL RECEIVED'
        else:
            files_status = 'MISSING FILES'
        print args
        if (len(error_list) == 1 and error_list[0].lower() == 'none') and (len(sucess_list) == 1 and sucess_list[0].lower() == 'none'):
            #python manage.py email_file_upload_stats --success None --error None--email opharatlhatlhe@bhp.org.bw
            subject = 'NOTHING: {0}: {1}: {2}: No upload file found'.format(files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
            sucess_list.pop()
            error_list.pop()
        elif len(error_list) == 1 and error_list[0].lower() == 'none':
            #python manage.py email_file_upload_stats --success bcpp_lentswe_201410081525.json --error bcpp_letlha_201410081525.json --email opharatlhatlhe@bhp.org.bw
            #len(error_list) can never be zero.
            subject = 'SUCCESS: {0}: {1}: {2}: Transaction files stats'.format(files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
            error_list.pop()
        else:
            #python manage.py email_file_upload_stats --success bcpp_lentswe_201410081525.json --error None --email opharatlhatlhe@bhp.org.bw
            subject = 'ERROR: {0}: {1}: {2}: Transaction files stats'.format(files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
        recipient_list = args[2].split(',')
        body = "\nUploaded incoming transaction files:"
        body += "\n______________________________________"
        for entry in sucess_list:
            if entry.lower() == 'none':
                #This is the case that not attempted upload was successful i.e
                #python manage.py email_file_upload_stats --success None --error bcpp_letlha_201410081525.json --email opharatlhatlhe@bhp.org.bw
                break
            uploaded = upload_file_model.objects.get(file_name=entry)
            body += "\nSUCCESS:\t{0}, uploaded={1}, duplicates={2}, ".format(entry, uploaded.consumed, uploaded.not_consumed)
        for entry in error_list:
            body += "\nERROR:\t{0}".format(entry)
        body += "\n======================================"
        body += missing_files
        print "sending email to {0}".format(recipient_list)
        return (subject, body, recipient_list)

    def get_missing_files(self):
        from ..models import Producer
        message = ""
        for producer in Producer.objects.filter(is_active=True):
            producer_identifier = producer.name.split('.')[0]
            #if ShortenIdentifierName.objects.filter(original_name=producer_identifier).exists():
            #    producer_identifier = ShortenIdentifierName.objects.get(original_name=producer_identifier).shorter_name
            UploadTransactionFile = get_model('import', 'UploadTransactionFile')
            UploadSkipDays = get_model('import', 'UploadSkipDays')
            latest_upload_file_date = UploadTransactionFile.objects.filter(identifier__iexact=producer_identifier).order_by('-file_date')
            if latest_upload_file_date.exists():
                # For any host we have synced before, i am guaranteed to always have UploadTransactionFile record(s).
                latest_upload_file_date = latest_upload_file_date[0].file_date
            else:
                # If i cannot find a UploadTransactionFile, then we must have never synced this host before.
                # We skip all remaining work.
                continue
            latest_skip_date = UploadSkipDays.objects.filter(identifier__iexact=producer_identifier).order_by('-skip_date')
            if latest_skip_date.exists() and latest_skip_date[0].skip_until_date:
                latest_skip_date = latest_skip_date[0].skip_until_date
            elif latest_skip_date.exists() and not latest_skip_date[0].skip_until_date:
                latest_skip_date = latest_skip_date[0].skip_date
            elif not latest_upload_file_date:
                continue
            if not latest_skip_date:
                # If no skip date exists for a host, then default back to latest file upload date.
                chosen = latest_upload_file_date
            else:
                # If you found a skip date for a host, then choose the latest between it and te file upload date.
                chosen = latest_upload_file_date if latest_upload_file_date > latest_skip_date else latest_skip_date
            #dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(chosen), until=parser.parse(date.today())))
            missing_dates = self.return_friendly_date(self.date_range_generator(chosen + timedelta(days=1), date.today()))
            if not missing_dates:
                continue
            message += "\nMissing Files from {} for the following date(s) {}".format(producer.name.upper(),
                                                                                     missing_dates)
        return message

    def return_friendly_date(self, date_list):
        date_string = ""
        for dt in date_list:
            date_string += '{}, '.format(str(dt.strftime("%Y%m%d")))
        return date_string

    def date_range_generator(self, start_date, end_date):
        date_list = []
        current_date = start_date
        flag = True
        while flag:
            if current_date <= end_date:
                date_list.append(current_date)
                current_date += timedelta(days=1)
            else:
                flag = False
#         print 'START={}, END={}, DATE_LIST={}'.format(start_date,end_date,len(date_list))
        return date_list