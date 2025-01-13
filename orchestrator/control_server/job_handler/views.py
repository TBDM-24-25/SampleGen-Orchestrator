from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, EnviromentVariable, Container
from .forms import JobForm, EnviromentVariableForm, BaseEnviromentVariableFormset
from django.forms import modelformset_factory
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .tasks import start_job_task



def index(request):
    """The index page lists all the available jobs and their current state. It is also the root page of the application.
    The page is implemented using WebSockets with Django Channels.
    """
    return render(request, 'job_handler/index.html')


def job_detail(request, job_id):
    try:
        job = Job.objects.get(pk=job_id)
    except:
        raise Http404("Job does not exist")
    
    # Get the related objects
    enviroment_variables = EnviromentVariable.objects.filter(job=job)
    agent = job.agent
    containers = Container.objects.filter(job=job)
    
    context = {
        "job": job,
        "enviroment_variables": enviroment_variables,
        "agent": agent,
        "containers": containers,
    }
    return render(request, "job_handler/job_detail.html", context)


def create_job(request):
    """This view is responsible for creating a new job and the corresponding enviroment variables. It handles both GET and POST requests."""

    current_extra_forms = 1

    # Everithing else than a POST request
    if request.method != 'POST':
        # GET request
        EnviromentVariableFormSet = modelformset_factory(model=EnviromentVariable, form=EnviromentVariableForm, formset=BaseEnviromentVariableFormset, extra=1)
        enviroment_variable_formset = EnviromentVariableFormSet(prefix='env', queryset=EnviromentVariable.objects.none())
        job_form = JobForm()
        context = {
            'job_form': job_form,
            'env_formset': enviroment_variable_formset,
            'extra_forms': current_extra_forms,
        }
        return render(request, 'job_handler/create_job.html', context=context)
    
    # Only POST requests
    current_extra_forms = int(request.POST.get('extra_forms'))
    job_form = JobForm(request.POST)
    EnviromentVariableFormSet = modelformset_factory(model=EnviromentVariable, form=EnviromentVariableForm, formset=BaseEnviromentVariableFormset, extra=current_extra_forms)
    enviroment_variable_formset = EnviromentVariableFormSet(request.POST, prefix='env', queryset=EnviromentVariable.objects.none())

    # If the data in the existing form set is valid, the existing data stays in the formset and a new form is added
    if "add_env" in request.POST:
        if enviroment_variable_formset.is_valid():
            current_extra_forms += 1
            EnviromentVariableFormSet = modelformset_factory(model=EnviromentVariable, form=EnviromentVariableForm, formset=BaseEnviromentVariableFormset, extra=current_extra_forms)
            enviroment_variable_formset = EnviromentVariableFormSet(initial=[form.cleaned_data for form in enviroment_variable_formset], prefix='env', queryset=EnviromentVariable.objects.none())
        
        context = {
            'job_form': job_form,
            'env_formset': enviroment_variable_formset,
            'extra_forms': current_extra_forms,
        }
        return render(request, 'job_handler/create_job.html', context=context)


    # Save form data in the database
    if job_form.is_valid() and enviroment_variable_formset.is_valid():
        # Save job instance in memory without committing to the database
        job = job_form.save(commit=False)

        # Add the initial operationi after the creation of the job entry
        job.latest_operation = "create"  # Example: Add a value for `latest_operation`
        # Commit changes to the database
        job.save()

        # Save the related environment variables
        enviroment_variables = enviroment_variable_formset.save(commit=False)
        for enviroment_variable in enviroment_variables:
            enviroment_variable.job = job
            enviroment_variable.save()
        
        # Redirect to the index page, reverse() is used to avoid hardcoding the URL
        return redirect("index")
    
    context = {
        'job_form': job_form,
        'env_formset': enviroment_variable_formset,
        'extra_forms': current_extra_forms,
    }

    return render(request, 'job_handler/create_job.html', context=context)


@require_http_methods(["DELETE"])
def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job.delete()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "jobs", # Group name
        {
            "type": "fetch.jobs", # Method to invoke
        }
    )
    return JsonResponse({'status': 'Job deleted'})


@require_http_methods(["POST"])
def start_job(request, job_id):
    # Call service that is asynchronly starting jobs
    job = Job.objects.get(pk=job_id)
    start_job_task(job)
    return JsonResponse({'status': 'job started', "data": "job started"})