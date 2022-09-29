from django.contrib import admin
from services._helpers.send_mail import Schedule

from services.forms import EmailForm, ScheduleForm
from services.models import EmailModel, ScheduleConfig


class EmailAdmin(admin.ModelAdmin):
    form = EmailForm

    list_display = ('id', 'user', 'to', 'subject')
    readonly_fields = ('user', )
    fieldsets = ((
        None, {
            'fields': ('user', 'to',)
        }), (
        'Other Receivers', {
            'fields': ('cc', 'bcc'),
            'classes': ('collapse',)
        }), (
        'Body', {
            'fields': ('subject',  'message'),
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            obj.user = request.user
            obj.save()
        except EmailModel.sender.RelatedObjectDoesNotExist as e:
            print(e)


class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleForm

    def save_model(self, request, obj, form, change):
        Schedule(obj)
        obj.save()


# Register your models here.
admin.site.register(EmailModel, EmailAdmin)
admin.site.register(ScheduleConfig, ScheduleAdmin)
