import socket

from datetime import datetime, timedelta


class TransactionUpload(object):

    """Not used.
    """

    def compile_upload_stats(self, args, upload_file_model):
        sucess_list = args[0].split(',')
        error_list = args[1].split(',')
        files_status = None
        missing_files = self.get_missing_files()
        if missing_files == "":
            files_status = 'ALL RECEIVED'
        else:
            files_status = 'MISSING FILES'
        if ((len(error_list) == 1 and error_list[0].lower() == 'none') and (
                len(sucess_list) == 1 and sucess_list[0].lower() == 'none')):
            subject = 'NOTHING: {0}: {1}: {2}: No upload file found'.format(
                files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
            sucess_list.pop()
            error_list.pop()
        elif len(error_list) == 1 and error_list[0].lower() == 'none':
            subject = 'SUCCESS: {0}: {1}: {2}: Transaction files stats'.format(
                files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
            error_list.pop()
        else:
            subject = 'ERROR: {0}: {1}: {2}: Transaction files stats'.format(
                files_status, datetime.today().strftime('%Y%m%d%H%M'), socket.gethostname())
        recipient_list = args[2].split(',')
        body = "\nUploaded incoming transaction files:"
        body += "\n______________________________________"
        for entry in sucess_list:
            if entry.lower() == 'none':
                # This is the case that not attempted upload was successful i.e
                break
            uploaded = upload_file_model.objects.get(file_name=entry)
            body += "\nSUCCESS:\t{0}, uploaded={1}, duplicates={2}, ".format(
                entry, uploaded.consumed, uploaded.not_consumed)
        for entry in error_list:
            body += "\nERROR:\t{0}".format(entry)
        body += "\n======================================"
        body += missing_files
        print("sending email to {}".format(recipient_list))
        return (subject, body, recipient_list)

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
        return date_list
