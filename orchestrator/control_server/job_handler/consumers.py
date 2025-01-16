import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Job
from .services.common_service import json_serial_date_time

class JobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_group_name = "jobs"

        # Join room group
        await self.channel_layer.group_add(self.job_group_name, self.channel_name)

        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.job_group_name, self.channel_name)

    @database_sync_to_async
    def get_jobs(self):
        return list(Job.objects.values())

    async def receive(self, text_data=None, bytes_data=None):
        # Parse the incoming message
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'fetch_jobs':
            await self.fetch_jobs()
        else:
            # Handle other message types if needed
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Unknown message type'
            }))

    async def fetch_jobs(self, event=None):
        # Fetch job data from the database
        jobs = await self.get_jobs()
        # Send job data back to the client
        await self.send(text_data=json.dumps({
            'type': 'job_list',
            'jobs': jobs
        }, default=json_serial_date_time))