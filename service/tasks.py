from celery import shared_task
from datetime import datetime
from django.utils.timezone import make_aware

from service.models import ScheduleConfigModel


@shared_task
def check_schedule():
    curr_time = make_aware(datetime.now())
    scheduled_tasks = ScheduleConfigModel.objects.filter(
        is_active=True, next_exec_date__lt=curr_time)

    for task in scheduled_tasks:
        obj_to_send = task.get_service_obj()
        send_result = obj_to_send.send_message()
        task.update_logs(send_result)
        print("Done!!!")
