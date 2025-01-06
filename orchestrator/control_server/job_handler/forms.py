from django import forms
from django.forms import ModelForm
from django.forms import BaseFormSet, BaseModelFormSet
from .models import Job, EnviromentVariable
from django.utils.translation import gettext_lazy as _

class SampleForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()


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



# class JobForm(forms.Form):
#     name = forms.CharField(max_length=200, label='Name', required=True)
#     container_image_name = forms.CharField(max_length=200, required=True, label="Container Image Name")
#     container_number = forms.IntegerField(max_value=5, required=True, label="Number of containers to deploy")
#     cpu_limit = forms.FloatField(label="Container CPU limit")
#     computation_duration_in_seconds = forms.IntegerField(max_value=7200, required=True, label="Computation duration in seconds")


# class EnviromentVariableForm(forms.Form):
#     variable_name = forms.CharField(max_length=200, label="Name", required=True)
#     variable_value = forms.CharField(max_length=200, label="Value", required=True)

    
# class BaseEnviromentVariableFormSet(BaseFormSet):
#     def clean(self):
#         if any(self.errors):
#             return

#         for form in self.forms:
#             variable_name = form.cleaned_data.get('variable_name')
#             variable_value = form.cleaned_data.get('variable_value')

#             if not (variable_name and variable_value):
#                 form.add_error('variable_value', 'Value is required if Name is set.')
#                 form.add_error('variable_name', 'Name is required if Value is set.')