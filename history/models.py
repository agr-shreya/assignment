from django.db import models
from django_enum_choices.fields import EnumChoiceField

from services.models import ScheduleConfig
from services._helpers.constants import ServiceType, ServiceStatus
# Create your models here.


class Log(models.Model):
    service_type = EnumChoiceField(ServiceType, default=ServiceType.EMAIL)
    service_modal_id = models.IntegerField()
    service_schedule = models.ForeignKey(
        ScheduleConfig, on_delete=models.CASCADE)
    sent_date = models.DateTimeField(auto_now_add=True)
    status = EnumChoiceField(ServiceStatus)
    note = models.CharField(max_length=200, blank=True, null=True)
