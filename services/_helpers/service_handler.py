import os
from dotenv import load_dotenv
from mailjet_rest import Client
from datetime import datetime
from dateutil.relativedelta import relativedelta

from services._helpers.constants import ScheduleFrequency, ServiceStatus, ServiceType
from services.models import EmailModel, ScheduleConfig
from history.models import Log

load_dotenv()


class Service:
    def create_schedule(self, service_modal_id: int, type: ServiceType):
        # default values (if schedule is directly created from service model)
        cadence_time, frequency, limit, is_active, last_exec_date = (
            datetime.now(), ScheduleFrequency.ONCE, 1, True, datetime.now())

        schedule = ScheduleConfig(
            service_type=ServiceType[type],
            service_modal_id=service_modal_id,
            cadence_time=cadence_time,
            frequency=frequency,
            limit=limit,
            is_active=is_active,
            last_exec_date=last_exec_date,
        )

        schedule.save()

    def get_schedule(self, cadence_time, freq: ScheduleFrequency, limit: int):
        current_time = cadence_time

        if freq == ScheduleFrequency.DAILY:
            return current_time + relativedelta(days=limit)
        elif freq == ScheduleFrequency.WEEKLY:
            return current_time + relativedelta(weeks=limit)
        elif freq == ScheduleFrequency.MONTHLY:
            return current_time + relativedelta(months=limit)
        elif freq == ScheduleFrequency.YEARLY:
            return current_time + relativedelta(years=limit)
        else:
            return datetime.now()


class Scheduler:
    success_status = [200]

    def __init__(self, obj: ScheduleConfig) -> None:
        self.obj = obj

        if obj.service_type == ServiceType.EMAIL:
            self.schedule_email()
        else:
            self.schedule_message()

    def schedule_email(self) -> None:
        _id = self.obj.service_modal_id

        try:
            _data = EmailModel.objects.get(pk=_id)
            mail = Mailjet()
            mail.send_mail(_data)

            self.set_logs(mail)

        except EmailModel.DoesNotExist as e:
            print(e)

    def schedule_message(self) -> None:
        pass

    def set_status(self, status_code) -> ServiceStatus:
        if status_code in self.success_status:
            return ServiceStatus.DELIVERED

        return ServiceStatus.FAILED

    def set_logs(self, mail) -> None:
        log = Log(
            service_type=self.obj.service_type,
            service_modal_id=self.obj.service_modal_id,
            service_schedule=self.obj,
            status=self.set_status(mail.status_code),
            note="",
        )
        log.save()


class Mailjet:
    API_KEY = os.getenv("MAILJET__API_KEY")
    API_SECRET = os.getenv("MAILJET__API_SECRET")
    mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

    def generate_data(self, obj) -> dict:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": obj.user.email,
                        "Name": obj.user.get_full_name()
                    },
                    "To": self.set_receiver_details(obj.to),
                    "CC": self.set_receiver_details(obj.cc),
                    "BCC": self.set_receiver_details(obj.bcc),
                    "Subject": obj.subject,
                    "TextPart": obj.message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        return data

    def set_receiver_details(self, emails) -> list:
        receivers = []

        for receiver in emails:
            details = {
                "Email": receiver,
                "Name": "Receiver"
            }
            receivers.append(details)

        return receivers

    def send_mail(self, obj: EmailModel) -> None:
        data = self.generate_data(obj)
        result = self.mailjet.send.create(data=data)

        self.status_code = result.status_code
        self.result = result.json()
