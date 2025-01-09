import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Job
from . import services

class JobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, code):
        pass

    @database_sync_to_async
    def get_jobs(self):
        return list(Job.objects.values())

    async def receive(self, text_data=None, bytes_data=None):
        # Parse the incoming message
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'fetch_jobs':
            # Fetch job data from the database
            jobs = await self.get_jobs()
            # Send job data back to the client
            await self.send(text_data=json.dumps({
                'type': 'job_list',
                'jobs': jobs
            }, default=services.json_serial_date_time),)
        else:
            # Handle other message types if needed
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Unknown message type'
            }))