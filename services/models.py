from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_enum_choices.fields import EnumChoiceField

from user.models import User
# from ._helpers.validation import phone_validation
from ._helpers.constants import ServiceType, ScheduleFrequency


# Service models here.
class EmailModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to = ArrayField(models.EmailField(unique=True))
    cc = ArrayField(models.EmailField(), null=True, blank=True)
    bcc = ArrayField(models.EmailField(), null=True, blank=True)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=200)

    def __str__(self) -> str:
        return str(self.to) + ' - ' + self.subject


# class MessageModel(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     to = ArrayField(models.CharField(
#         max_length=10, unique=True, validators=[phone_validation]))
#     message = models.CharField(max_length=200)

#     def __str__(self) -> str:
#         return str(self.to) + ' - ' + self.subject


# Schedule Model which takes the service id, and type to get
# the data from the above services and accordingly handles api call
class ScheduleConfig(models.Model):
    service_type = EnumChoiceField(ServiceType, default=ServiceType.EMAIL)
    service_modal_id = models.IntegerField()
    cadence_time = models.DateTimeField()
    frequency = EnumChoiceField(
        ScheduleFrequency, default=ScheduleFrequency.ONCE)
    limit = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    next_exec_date = models.DateTimeField(auto_now_add=True, blank=True)
    last_exec_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        service_type = self.service_type.value
        is_active = 'active' if self.is_active else 'completed'

        return '%s - %s: %s' % (service_type, self.service_modal_id, is_active)
