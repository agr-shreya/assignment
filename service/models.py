from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_enum_choices.fields import EnumChoiceField
from django.utils.timezone import make_aware

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings

from ._helpers.validation import phone_validation
from ._helpers.service_handlers import Mailjet
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
        is_service_scheduled = ScheduleConfigModel.objects.filter(
            service_model_id=service_model_id)

        if not is_service_scheduled:
            running_time = make_aware(datetime.now())

            ScheduleConfigModel.objects.create(
                service_type=service_type,
                service_model_id=service_model_id,
                running_time=running_time,
                cadence=ScheduleFreq.ONCE,
                frequency=1,
                is_active=True,
            )

    @ classmethod
    def get_service_status(cls, status_code: int) -> ServiceStatus:
        success_code = [200]

        if status_code in success_code:
            return ServiceStatus.DELIVERED

        return ServiceStatus.FAILED

    def send_message(self):
        pass

    def __str__(self) -> str:
        return str(self.to) + ' - ' + self.message


class EmailModel(ServiceModel):
    to = ArrayField(models.EmailField(unique=True))
    cc = ArrayField(models.EmailField(), null=True, blank=True)
    bcc = ArrayField(models.EmailField(), null=True, blank=True)
    subject = models.CharField(max_length=100)

    def send_message(self):
        super().send_message()
        service = Mailjet()
        service.send_mail(email_data=self)
        sent_status = self.get_service_status(status_code=service.status_code)

        return {
            "sent_status": sent_status,
            "result": service.result
        }


class MessageModel(ServiceModel):
    to = ArrayField(models.CharField(
        max_length=10, unique=True, validators=[phone_validation]))


class ScheduleConfigModel(models.Model):
    service_type = EnumChoiceField(ServiceType)
    service_model_id = models.IntegerField()

    running_time = models.DateTimeField()
    cadence = EnumChoiceField(ScheduleFreq, default=ScheduleFreq.ONCE)
    frequency = models.IntegerField(default=1)

    next_exec_date = models.DateTimeField(auto_now_add=True, blank=True)
    last_exec_date = models.DateTimeField(auto_now_add=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            self.next_exec_date = self.running_time
            self.last_exec_date = self.get_n_exec_date(
                running_time=self.running_time,
                cadence=self.cadence,
                freq=self.frequency
            )

        super(ScheduleConfigModel, self).save(*args, **kwargs)

    @classmethod
    def get_n_exec_date(cls, running_time: datetime, cadence: ScheduleFreq, freq: int) -> datetime:
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
            # delta = {'days': 3} => relativedelta(days=3)
            delta = {interval: freq}
            exec_date = running_time + relativedelta(**delta)
            return exec_date

    def get_service_obj(self) -> ServiceModel:
        service_obj = None

        if self.service_type == ServiceType.EMAIL:
            service_obj = EmailModel.objects.get(id=self.service_model_id)
        else:
            service_obj = MessageModel.objects.get(id=self.service_model_id)

        return service_obj

    def update_logs(self, send_result) -> None:
        sent_status = send_result['sent_status']

        self.set_logs(
            sent_status=sent_status,
            result=send_result['result'],
        )

        if sent_status == ServiceStatus.DELIVERED:
            self.update_schedule_data()

    def set_logs(self, sent_status, result):
        from history.models import Log
        Log.objects.create(
            service_type=self.service_type,
            service_model_id=self.service_model_id,
            service_schedule=self,
            status=sent_status,
            note="",
        )

    def update_schedule_data(self):
        def get_datetime(iso_datetime):
            return iso_datetime.strftime("%Y-%m-%d %H:%M:%S")

        if get_datetime(self.next_exec_date) == get_datetime(self.last_exec_date):
            self.set_as_inactive()
        else:
            curr_time = make_aware(datetime.now())
            next_exec_date = self.get_n_exec_date(
                running_time=self.next_exec_date,
                cadence=self.cadence,
                freq=1
            )

            self.update_next_exec_date(next_exec_date)

        # using diff b/w curr_time & next_exec_date
        # would be creating logs for celery errors
        # print(next_exec_date)
        # print(curr_time - next_exec_date)
        # print(next_exec_date > self.last_exec_date)

    def set_as_inactive(self):
        self.is_active = False
        self.save()

    def update_next_exec_date(self, next_exec_date):
        self.next_exec_date = next_exec_date
        self.save()

    def __str__(self) -> str:
        service_type = self.service_type
        is_active = 'active' if self.is_active else 'completed'

        return '%s - %s: %s' % (service_type, self.service_model_id, is_active)
