# filepath: orchestrator/control_server/job_handler/forms.py
from django import forms

class SampleForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

class JobForm(forms.Form):
    name = forms.CharField(max_length=200, label='Name', required=True)
    container_image_name = forms.CharField(max_length=200, required=True, label="Container Image Name")
    container_number = forms.IntegerField(max_value=5, required=True, label="Number of containers to deploy")
    cpu_limit = forms.FloatField(label="Container CPU limit")
    computation_duration_in_seconds = forms.IntegerField(max_value=7200, required=True, label="Computation duration in seconds")


class EnviromentVariableForm(forms.Form):
    variable_name = forms.CharField(max_length=200, label="Name", required=False)
    variable_value = forms.CharField(max_length=200, label="Value", required=False)
    
