from django.contrib import admin
from .models import Log


class LogsAdmin(admin.ModelAdmin):
    model = Log
    list_display = ('id', 'service_type', 'service_modal_id',
                    'service_schedule', 'sent_date', 'status', 'note')
    readonly_fields = ('service_type', 'service_modal_id',
                       'service_schedule', 'sent_date', 'status', 'note')


# Register your models here.
admin.site.register(Log, LogsAdmin)
