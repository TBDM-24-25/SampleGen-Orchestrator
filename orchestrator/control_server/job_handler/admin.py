from django.contrib import admin
from .models import Job, EnviromentVariable, Agent, Container, AgentCheck

# Register your models here.
admin.site.register(Job)
admin.site.register(EnviromentVariable)
admin.site.register(Agent)
admin.site.register(Container)
admin.site.register(AgentCheck)