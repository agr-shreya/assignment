from xmlrpc.client import Boolean
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_enum_choices.fields import EnumChoiceField
from django.utils.timezone import make_aware

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings

from ._helpers.validation import phone_validation
from ._helpers.service_handlers import Infoblip, Mailjet
from ._helpers.constants import ServiceType, ScheduleFreq, ServiceStatus

User = settings.AUTH_USER_MODEL


# Create your models here.
class ServiceModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to = ArrayField(models.CharField(unique=True))
    message = models.CharField(max_length=200)

    class Meta:
        abstract = True

    @classmethod
    def create_new_schedule(cls, service_type: ServiceType, service_model_id: int) -> None:
        is_service_not_scheduled = ServiceModel.is_service_not_scheduled(service_type,
                                                                         service_model_id)

        if is_service_not_scheduled:
            running_time = make_aware(datetime.now())

            ScheduleConfigModel.objects.create(
                service_type=service_type,
                service_model_id=service_model_id,
                running_time=running_time,
                cadence=ScheduleFreq.ONCE,
                frequency=1,
                is_active=True,
            )

    @classmethod
    def is_service_not_scheduled(cls, service_type: ServiceType, service_model_id: int) -> Boolean:
        service_configs = ScheduleConfigModel.objects.filter(
            service_type=service_type,
            service_model_id=service_model_id)

        return not service_configs

    def send_message(self, service):
        result = service.send_message()
        return result

    def __str__(self) -> str:
        return str(self.to) + ' - ' + self.message


class EmailModel(ServiceModel):
    to = ArrayField(models.EmailField(unique=True))
    cc = ArrayField(models.EmailField(), null=True, blank=True)
    bcc = ArrayField(models.EmailField(), null=True, blank=True)
    subject = models.CharField(max_length=100)

    def send_message(self):
        service = Mailjet(data=self)
        return super().send_message(service)


class MessageModel(ServiceModel):
    to = ArrayField(models.CharField(
        max_length=10, unique=True, validators=[phone_validation]))

    def send_message(self):
        service = Infoblip(data=self)
        return super().send_message(service)


class ScheduleConfigModel(models.Model):
    service_type = EnumChoiceField(ServiceType)
    service_model_id = models.IntegerField()

    running_time = models.DateTimeField()
    cadence = EnumChoiceField(ScheduleFreq, default=ScheduleFreq.ONCE)
    frequency = models.IntegerField(default=1)

    next_schedule_time = models.DateTimeField(auto_now_add=True, blank=True)
    last_schedule_time = models.DateTimeField(auto_now_add=True, blank=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_n_schedule_time(cls, running_time: datetime, cadence: ScheduleFreq, freq: int) -> datetime:
        get_interval = {
            ScheduleFreq.ONCE: 'default',
            ScheduleFreq.DAILY: 'days',
            ScheduleFreq.WEEKLY: 'weeks',
            ScheduleFreq.MONTHLY: 'months',
            ScheduleFreq.YEARLY: 'years',
        }

        interval = get_interval[cadence]
        if interval == 'default':
            return running_time
        else:
            '''
                > delta = {'days': 3}
                > relativedelta(days=3)
                > exec_date = running_time + (freq * days/weeks/months/year)
            '''
            delta = {interval: freq}
            exec_date = running_time + relativedelta(**delta)
            return exec_date

    def save(self, *args, **kwargs):
        if self.is_new():
            self.next_schedule_time = self.running_time
            self.last_schedule_time = self.get_n_schedule_time(
                running_time=self.running_time,
                cadence=self.cadence,
                freq=self.frequency
            )

        super(ScheduleConfigModel, self).save(*args, **kwargs)

    def is_new(self):
        return not self.id

    def get_service_obj_from_service_type(self) -> ServiceModel:
        if self.service_type == ServiceType.EMAIL:
            service_obj = EmailModel.objects.get(id=self.service_model_id)
        else:
            service_obj = MessageModel.objects.get(id=self.service_model_id)

        return service_obj

    def update_logs(self, send_result) -> None:
        sent_status = send_result['status']

        self.set_logs(
            sent_status=sent_status,
            result=send_result['result'],
        )

        if sent_status == ServiceStatus.DELIVERED:
            self.update_schedule_data()

    def set_logs(self, sent_status, result):
        from history.models import LogModel
        LogModel.objects.create(
            service_type=self.service_type,
            service_model_id=self.service_model_id,
            service_schedule=self,
            status=sent_status,
            note="",
        )

    def update_schedule_data(self):
        def get_datetime(iso_datetime):
            return iso_datetime.strftime("%Y-%m-%d %H:%M:%S")

        if get_datetime(self.next_schedule_time) >= get_datetime(self.last_schedule_time):
            self.set_as_inactive()
        else:
            curr_time = make_aware(datetime.now())
            next_schedule_time = self.get_n_schedule_time(
                running_time=self.next_schedule_time,
                cadence=self.cadence,
                freq=1
            )

            self.update_next_schedule_time(next_schedule_time)

        # using diff b/w curr_time & next_schedule_time
        # would be creating logs for celery errors
        # print(next_schedule_time)
        # print(curr_time - next_schedule_time)
        # print(next_schedule_time > self.last_schedule_time)

    def set_as_inactive(self):
        self.is_active = False
        self.save()

    def update_next_schedule_time(self, next_schedule_time):
        self.next_schedule_time = next_schedule_time
        self.save()

    def __str__(self) -> str:
        service_type = self.service_type
        is_active = 'active' if self.is_active else 'completed'

        return '%s - %s: %s' % (service_type, self.service_model_id, is_active)
