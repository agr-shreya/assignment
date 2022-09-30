from celery import shared_task
from datetime import datetime

from ._helpers.service_handler import Scheduler, Service
from .models import ScheduleConfig


@shared_task
def check_schedule():
    schedules = ScheduleConfig.objects.all()
    for schedule in schedules:
        print(schedule)
        if schedule.is_active:
            current_date = datetime.now()
            schedule_date = schedule.next_exec_date.replace(tzinfo=None)

            if current_date > schedule_date:
                scheduler = Scheduler(schedule)
                service = Service()
                next_limit = 1

                next_exec_date = service.get_schedule(
                    schedule_date,
                    schedule.frequency,
                    next_limit
                )

                if next_exec_date > schedule.last_exec_date.replace(tzinfo=None):
                    schedule.is_active = False
                    schedule.save()

                else:
                    schedule.next_exec_date = next_exec_date
                    schedule.save()
                print("done bro")
