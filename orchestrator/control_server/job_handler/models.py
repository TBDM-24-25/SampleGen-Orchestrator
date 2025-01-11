from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.
class Agent(models.Model):
    status = models.CharField(max_length=200)
    kafka_timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Job(models.Model):
    name = models.CharField(max_length=200)
    latest_operation = models.CharField(max_length=200)
    container_image_name = models.CharField(max_length=200)
    container_number = models.IntegerField(default=1)
    container_cpu_limit = models.FloatField(null=False, default=0.3)
    container_memory_limit_in_mb = models.IntegerField(default=512)
    computation_duration_in_seconds = models.IntegerField(default=300)
    iot_data_kafka_topic = models.CharField(max_length=200)
    kafka_timestamp = models.DateTimeField(null=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def clean(self):
        """Validate the model fields."""
        super().clean()
        validation_errors = {}

        if self.container_cpu_limit < 0.1:
            validation_errors['container_cpu_limit'] = "Container CPU limit must be greater than 0.1"
        if self.container_cpu_limit > 2.0:
            validation_errors['container_cpu_limit'] = "Container CPU limit must be less than 2.0"

        if self.container_number < 1:
            validation_errors['container_number'] = "Container number must be at least 1"
        if self.container_number > 10:
            validation_errors['container_number'] = "Container number must be at most 10"

        if self.container_memory_limit_in_mb < 512:
            validation_errors['container_memory_limit_in_mb'] = "Container memory limit must be at least 512 MB"
        if self.container_memory_limit_in_mb > 2048:
            validation_errors['container_memory_limit_in_mb'] = "Container memory limit must be at most 2048 MB"

        if self.computation_duration_in_seconds < 60:
            validation_errors['computation_duration_in_seconds'] = "Computation duration must be at least 60 seconds"
        if self.computation_duration_in_seconds > 600:
            validation_errors['computation_duration_in_seconds'] = "Computation duration must be at most 600 seconds"

        if validation_errors:
            raise ValidationError(validation_errors)


class EnviromentVariable(models.Model):
    variable_name = models.CharField(max_length=200, null=False)
    variable_value = models.CharField(max_length=200, null=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Container(models.Model):
    status = models.CharField(max_length=200)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AgentCheck(models.Model):
    content = models.CharField(max_length=200)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)