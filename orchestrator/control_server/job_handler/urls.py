from django.urls import path

import job_handler.views as views

urlpatterns = [
    path("", views.index, name="index"),
]