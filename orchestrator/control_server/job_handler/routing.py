from django.urls import re_path
from .import consumers

# This list defines the websocket URL patterns required for the django channels consumers
websocket_urlpatterns = [
    re_path(r"ws/job/$", consumers.JobConsumer.as_asgi()),
]