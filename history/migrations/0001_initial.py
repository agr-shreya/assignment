# Generated by Django 4.0.7 on 2022-10-06 07:32

from django.db import migrations, models
import django.db.models.deletion
import django_enum_choices.choice_builders
import django_enum_choices.fields
import service._helpers.constants


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', django_enum_choices.fields.EnumChoiceField(choice_builder=django_enum_choices.choice_builders.value_value, choices=[('Email', 'Email'), ('Message', 'Message')], enum_class=service._helpers.constants.ServiceType, max_length=7)),
                ('service_model_id', models.IntegerField()),
                ('sent_date', models.DateTimeField(auto_now_add=True)),
                ('status', django_enum_choices.fields.EnumChoiceField(choice_builder=django_enum_choices.choice_builders.value_value, choices=[('Delivered', 'Delivered'), ('Pending', 'Pending'), ('Failed', 'Failed')], enum_class=service._helpers.constants.ServiceStatus, max_length=9)),
                ('note', models.CharField(blank=True, max_length=1000, null=True)),
                ('service_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.scheduleconfigmodel')),
            ],
        ),
    ]
