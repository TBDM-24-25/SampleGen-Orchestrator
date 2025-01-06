from django.db import models


# Create your models here.
class Job(models.Model):
    name = models.CharField(max_length=200)
    latest_operation = models.CharField(max_length=200)
    container_image_name = models.CharField(max_length=200)
    container_number = models.IntegerField(default=1)
    container_cpu_limit = models.FloatField(null=False)
    container_memory_limit = models.CharField(max_length=200)
    computation_duration_in_seconds = models.IntegerField()
    kafka_timestamp = models.DateTimeField(null=True)
    # user ID foreign key, will be added later when authentication is implemented
    # TODO: implement authentication
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO: enviroment variables must be mandatory when creating a job
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 

class EnviromentVariable(models.Model):
    variable_name = models.CharField(max_length=200, null=False)
    variable_value = models.CharField(max_length=200, null=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Agent(models.Model):
    status = models.CharField(max_length=200)
    kafka_timestamp = models.DateTimeField()
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