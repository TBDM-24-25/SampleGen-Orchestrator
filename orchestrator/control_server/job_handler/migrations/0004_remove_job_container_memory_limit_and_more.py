# Generated by Django 4.2.17 on 2025-01-11 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_handler', '0003_job_agent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='container_memory_limit',
        ),
        migrations.AddField(
            model_name='job',
            name='container_memory_limit_in_mb',
            field=models.IntegerField(default=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='computation_duration_in_seconds',
            field=models.IntegerField(default=300),
        ),
    ]
