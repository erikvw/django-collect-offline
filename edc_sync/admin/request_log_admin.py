from django.contrib import admin

from ..models import RequestLog


class RequestLogAdmin(admin.ModelAdmin):

    list_display = ('producer', 'request_datetime', 'status', 'comment')

admin.site.register(RequestLog, RequestLogAdmin)
