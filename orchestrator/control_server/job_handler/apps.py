from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class JobHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_handler'

    def ready(self):
        from control_server_project.celery import app as celery_app
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule

            # Erstelle IntervalSchedule für automatische Tasks
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=5,
                period=IntervalSchedule.SECONDS,
            )

            # Periodic tasks erstellen
            PeriodicTask.objects.get_or_create(
                interval=schedule,
                name='Automatic Job Stop Task',
                task='job_handler.tasks.automatic_job_stop_task',
            )

            PeriodicTask.objects.get_or_create(
                interval=schedule,
                name='Automatic Job Start Task',
                task='job_handler.tasks.automatic_job_start_task',
            )

            # Celery-Tasks senden
            celery_app.send_task('job_handler.tasks.monitor_agent_status')
            celery_app.send_task('job_handler.tasks.monitor_job_status')

        except (OperationalError, ProgrammingError):
            pass