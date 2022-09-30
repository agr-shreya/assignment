from django.contrib import admin
from services._helpers.service_handler import Service

from services.models import EmailModel, ScheduleConfig


class EmailAdmin(admin.ModelAdmin):
    model = EmailModel

    list_display = ('id', 'user', 'to', 'subject')
    readonly_fields = ('user', )
    fieldsets = ((
        None, {
            'fields': ('user', 'to')
        }), (
        'Other Receivers', {
            'fields': ('cc', 'bcc'),
            'classes': ('collapse',)
        }), (
        'Body', {
            'fields': ('subject', 'message'),
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            obj.user = request.user
            create_schedule_flag = False
            if not obj.id:
                create_schedule_flag = True

            obj.save()
            if create_schedule_flag:
                service = Service()
                service.create_schedule(obj.id, type='EMAIL')

        except EmailModel.user.RelatedObjectDoesNotExist as e:
            print(e)


class ScheduleAdmin(admin.ModelAdmin):
    model = ScheduleConfig

    readonly_fields = ('next_exec_date', 'last_exec_date', )
    fieldsets = ((
        'Service Details', {
            'fields': ('service_type', 'service_modal_id')
        }), (
        'Cadence Schedule', {
            'fields': ('cadence_time', 'frequency', 'limit', 'is_active'),
        }), (
        None, {
            'fields': ('next_exec_date', 'last_exec_date',),
        }),
    )

    def save_model(self, request, obj, form, change):
        service = Service()
        obj.next_exec_date = obj.cadence_time
        obj.last_exec_date = service.get_schedule(
            obj.cadence_time, obj.frequency, obj.limit)
        obj.save()


# Register your models here.
admin.site.register(EmailModel, EmailAdmin)
admin.site.register(ScheduleConfig, ScheduleAdmin)
