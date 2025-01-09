from django import forms
from django.forms import ModelForm
from django.forms import BaseFormSet, BaseModelFormSet
from .models import Job, EnviromentVariable
from django.utils.translation import gettext_lazy as _



class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ["name", "container_image_name", "container_number", "container_cpu_limit", "computation_duration_in_seconds"]
        labels = {
            "name": _("Name"),
            "container_image_name": _("Container image name"),
            "container_number": _("Container number"),
            "container_cpu_limit": _("Container CPU limit"),
            "computation_duration_in_seconds": _("Computation duration"),
        }
        help_texts = {
            "name": _("How you would like to name your Job"),
            "container_image_name": _("Provide the container image name use in your container registry."),
            "container_number": _("the number of containers to deploy"),
            "container_cpu_limit": _("The amount of CPU the container can use. Please provide a floating point number."),
            "computation_duration_in_seconds": _("The duration of computation measured in seconds"),
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


