# Generated by Django 4.0.7 on 2022-10-06 07:32

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_enum_choices.choice_builders
import django_enum_choices.fields
import service._helpers.constants
import service._helpers.validation


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleConfigModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', django_enum_choices.fields.EnumChoiceField(choice_builder=django_enum_choices.choice_builders.value_value, choices=[('Email', 'Email'), ('Message', 'Message')], enum_class=service._helpers.constants.ServiceType, max_length=7)),
                ('service_model_id', models.IntegerField()),
                ('running_time', models.DateTimeField()),
                ('cadence', django_enum_choices.fields.EnumChoiceField(choice_builder=django_enum_choices.choice_builders.value_value, choices=[('Once', 'Once'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default=service._helpers.constants.ScheduleFreq['ONCE'], enum_class=service._helpers.constants.ScheduleFreq, max_length=7)),
                ('frequency', models.IntegerField(default=1)),
                ('next_schedule_time', models.DateTimeField(auto_now_add=True)),
                ('last_schedule_time', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('to', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10, unique=True, validators=[service._helpers.validation.phone_validation]), size=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('to', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254, unique=True), size=None)),
                ('cc', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None)),
                ('bcc', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None)),
                ('subject', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
