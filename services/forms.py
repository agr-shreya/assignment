from django.forms import ModelForm

from .models import EmailModel, ScheduleConfig
# from user.models import User


class EmailForm(ModelForm):
    class Meta:
        model = EmailModel
        fields = ['user', 'to', 'cc', 'bcc', 'subject',  'message']

    # def clean_last_modified_by(self):
    #     if not self.cleaned_data['last_modified_by']:
    #         return User()
    #     return self.cleaned_data['last_modified_by']


class ScheduleForm(ModelForm):
    class Meta:
        model = ScheduleConfig
        fields = ['service_type', 'service_modal_id', 'cadence_time',
                  'frequency', 'limit',  'is_active', 'last_exec_date']