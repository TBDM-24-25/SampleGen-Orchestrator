import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class JobConsumer(WebsocketConsumer):
    def connect(self):
        return super().connect()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        return super().receive(text_data, bytes_data)
    
    