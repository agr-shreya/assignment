from django.contrib import admin

from ._helpers.constants import ServiceType
from .models import EmailModel, MessageModel, ScheduleConfigModel


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
            obj.save()
            obj.create_new_schedule(
                service_type=ServiceType.EMAIL,
                service_model_id=obj.id
            )

        except EmailModel.user.RelatedObjectDoesNotExist as e:
            print(e)


class MessageAdmin(admin.ModelAdmin):
    model = MessageModel
    list_display = ('id', 'user', 'to', 'message')

    readonly_fields = ('user', )
    fieldsets = ((
        None, {
            'fields': ('user', 'to')
        }), (
        'Body', {
            'fields': ('message',),
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            obj.user = request.user
            obj.save()
            obj.create_new_schedule(
                service_type=ServiceType.MESSAGE,
                service_model_id=obj.id
            )

        except MessageModel.user.RelatedObjectDoesNotExist as e:
            print(e)


class ScheduleConfigAdmin(admin.ModelAdmin):
    model = ScheduleConfigModel

    readonly_fields = ('next_exec_date', 'last_exec_date', )
    fieldsets = ((
        'Service Details', {
            'fields': ('service_type', 'service_model_id')
        }), (
        'Cadence Schedule', {
            'fields': ('running_time', 'cadence', 'frequency', 'is_active'),
        }), (
        None, {
            'fields': ('next_exec_date', 'last_exec_date'),
        }),
    )


# Register your models here.
admin.site.register(EmailModel, EmailAdmin)
admin.site.register(ScheduleConfigModel, ScheduleConfigAdmin)
