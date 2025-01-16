from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_job/", views.create_job, name="create_job"),
    path("job_detail/<int:job_id>/", views.job_detail, name="job_detail"),
    path("delete_job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("start_job/<int:job_id>/", views.start_job, name="start_job"),
]

