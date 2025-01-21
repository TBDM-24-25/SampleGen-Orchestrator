from django.apps import AppConfig


class JobHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_handler'

    def ready(self):
            from control_server_project.celery import app as celery_app
            # celery_app.send_task('job_handler.tasks.permanent_background_task')
            celery_app.send_task('job_handler.tasks.monitor_agent_status')
            celery_app.send_task('job_handler.tasks.monitor_job_status')
            # celery_app.send_task('job_handler.tasks.job_stop_scheduler_task')
