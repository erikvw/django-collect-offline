from django.contrib import admin

from ..models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):

    list_display = ('producer', 'request_datetime', 'status', 'comment')
