from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Job

# Create your views here.

# Lists all the available jobs and is also the root page
def index(request):
    jobs = Job.objects.all()

    context = {
        'jobs': jobs,
    }
    return render(request, 'job_handler/index.html', context)

# TODO: use this in the index page later:
# <li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
# path("<int:question_id>/", views.detail, name="detail"),
# See https://docs.djangoproject.com/en/5.1/intro/tutorial03/


# Creates a new job and redirects to the index page (includes also exception handling)
def create_job(request):
    try:
        job = Job(name=request.POST['name'], latest_operation=request.POST['latest_operation'], container_image_name=request.POST['container_image_name'], container_number=request.POST['container_number'], container_cpu_limit=request.POST['container_cpu_limit'], container_memory_limit=request.POST['container_memory_limit'], computation_duration_in_seconds=request.POST['computation_duration_in_seconds'], kafka_timestamp=request.POST['kafka_timestamp'])
        job.save()
    except (KeyError, Job.DoesNotExist):
        return render(request, 'job_handler/index.html', {
            'error_message': "You didn't provide all the necessary fields.",
        })
    else:
        return HttpResponseRedirect(reverse('index'))
    
# filepath: orchestrator/control_server/job_handler/views.py
from django.shortcuts import render
from .forms import SampleForm

def show_bootstrap(request):
    form = SampleForm()
    return render(request, 'job_handler/bootstrap_try.html', {'form': form})