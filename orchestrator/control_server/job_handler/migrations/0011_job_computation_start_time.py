# Generated by Django 4.2.17 on 2025-01-24 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_handler', '0010_job_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='computation_start_time',
            field=models.DateTimeField(null=True),
        ),
    ]
