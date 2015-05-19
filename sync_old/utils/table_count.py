from django.conf import settings
from django.db import connections


def table_count(app_label):
    db = settings.DATABASES['default']['NAME']
    cursor = connections['default'].cursor()
    sql = ('SHOW TABLES WHERE Tables_in_%s like \'%s%s%s\' and '
           'Tables_in_%s not like \'%saudit%s\';') % (db, '%', app_label, '%', db, '%', '%')
    cursor.execute(str(sql))
    for row in cursor.fetchall():
        print row
