from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("bootstrap_try/", views.show_bootstrap, name="bootstrap_try"),   
]