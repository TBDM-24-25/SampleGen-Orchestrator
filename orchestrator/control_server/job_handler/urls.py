from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_job/", views.create_job, name="new_job"),
    path("job_detail/<int:job_id>/", views.job_detail, name="job_detail"),
]