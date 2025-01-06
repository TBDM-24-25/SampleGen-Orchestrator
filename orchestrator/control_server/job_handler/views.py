from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Job
from .forms import JobForm, EnviromentVariableForm, SampleForm, BaseEnviromentVariableFormset
from django.forms import modelformset_factory


# TODO: use this in the index page later:
# <li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
# path("<int:question_id>/", views.detail, name="detail"),
# See https://docs.djangoproject.com/en/5.1/intro/tutorial03/
# Lists all the available jobs and is also the root page
def index(request):
    """The index page lists all the available jobs and their current state. It is also the root page of the application."""
    jobs = Job.objects.all()

    context = {
        'jobs': jobs,
    }
    return render(request, 'job_handler/index.html', context)


def create_job(request):
    """This view is responsible for creating a new job and the corresponding enviroment variables. It handles both GET and POST requests."""

    current_extra_forms = 1
    extra_form_number = 1
    EnviromentVariableFormSet = modelformset_factory(EnviromentVariableForm, formset=BaseEnviromentVariableFormset, extra=extra_form_number)

    # Everithing else than a POST request
    if request.method != 'POST':
        # GET request
        enviroment_variable_formset = EnviromentVariableFormSet(prefix='env')
        job_form = JobForm()
        context = {
            'job_form': job_form,
            'env_formset': enviroment_variable_formset,
            'extra_forms': current_extra_forms,
        }
        return render(request, 'job_handler/new_job.html', context=context)
    
    # Only POST requests
    job_form = JobForm(request.POST)
    enviroment_variable_formset = EnviromentVariableFormSet(request.POST, prefix='env')

    # If the data in the existing form set is valid, the existing data stays in the formset and a new form is added
    if "add_env" in request.POST:
        if enviroment_variable_formset.is_valid():
            EnviromentVariableFormSet = modelformset_factory(EnviromentVariableForm, formset=BaseEnviromentVariableFormset, extra=extra_form_number)
            updated_enviroment_variable_formset = EnviromentVariableFormSet(initial=[form.cleaned_data for form in enviroment_variable_formset], prefix='env')
            current_extra_forms += 1
        return render(request, 'job_handler/new_job.html', {
            'job_form': job_form,
            'env_formset': updated_enviroment_variable_formset,
            'extra_forms': current_extra_forms,
        })

    # If the form data is valid, it is saved in the database
    if job_form.is_valid() and enviroment_variable_formset.is_valid():
        # The job form data is only saved as a job instance, not in the database
        job = job_form.save(commit=False)


        # Save enviroment variables in database

        

def show_bootstrap(request):
    form = SampleForm()
    return render(request, 'job_handler/bootstrap_try.html', {'form': form})