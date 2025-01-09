from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("bootstrap_try/", views.show_bootstrap, name="bootstrap_try"),
    path("new_job/", views.create_job, name="new_job"),
    path("index_websocket/", views.index_websocket, name="index_websocket"),
    path("job_detail/<int:job_id>/", views.job_detail, name="job_detail"),
]