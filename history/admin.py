from django.contrib import admin
from .models import LogModel


class LogsAdmin(admin.ModelAdmin):
    model = LogModel
    list_display = ('id', 'service_type', 'service_model_id',
                    'service_schedule', 'sent_date', 'status', 'note')
    readonly_fields = ('service_type', 'service_model_id',
                       'service_schedule', 'sent_date', 'status', 'note')


# Register your models here.
admin.site.register(LogModel, LogsAdmin)
