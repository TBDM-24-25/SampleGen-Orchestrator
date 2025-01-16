from django import forms
from django.forms import ModelForm
from django.forms import BaseFormSet, BaseModelFormSet
from .models import Job, EnviromentVariable
from django.utils.translation import gettext_lazy as _



class JobForm(ModelForm):
    class Meta:
        # TODO: Add memory limit field
        model = Job
        fields = ["name", "description", "container_image_name", "container_number", "container_cpu_limit", "container_memory_limit_in_mb", "computation_duration_in_seconds", "iot_data_kafka_topic"]
        labels = {
            "name": _("Name"),
            "description": _("Description"),
            "container_image_name": _("Container image name"),
            "container_number": _("Container number"),
            "container_cpu_limit": _("Container CPU limit"),
            "container_memory_limit_in_mb": _("Container memory limit in Megabytes"),
            "computation_duration_in_seconds": _("Computation duration"),
            "iot_data_kafka_topic": _("Kafka topic"),
        }
        help_texts = {
            "name": _("How you would like to name your Job"),
            "description": _("Describe what the job does"),
            "container_image_name": _("Provide the container image name use in your container registry."),
            "container_number": _("the number of containers to deploy"),
            "container_cpu_limit": _("The amount of CPU the container can use. Please provide a floating point number."),
            "container_memory_limit_in_mb": _("The amount of memory the container can use in megabytes. The value must be between 512 and 2048 Megabytes."),
            "computation_duration_in_seconds": _("The duration of computation measured in seconds"),
            "iot_data_kafka_topic": _("The Kafka topic where the IoT data is published."),
        }

class EnviromentVariableForm(ModelForm):
    class Meta:
        model = EnviromentVariable
        fields = ["variable_name", "variable_value"]
        labels = {
            "variable_name": _("Name"),
            "variable_value": _("Value"),
            }
    

class BaseEnviromentVariableFormset(BaseModelFormSet):
    """Custom validation for the formset."""
    def clean(self):
        if any(self.errors):
            return
        
        for form in self.forms:
            # Check if the form is valid and has cleaned data
            if not form.cleaned_data.get('variable_name') and not form.cleaned_data.get('variable_value'):
                form.add_error('variable_value', 'Value is required if Name is set.')
                form.add_error('variable_name', 'Name is required if Value is set.')


