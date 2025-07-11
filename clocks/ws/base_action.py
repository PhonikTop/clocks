from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
import json

class BaseAction:
    queryset = None

    def __init__(self):
        self.consumer = None
        self.data = None

    @classmethod
    async def execute(cls, consumer, data):
        action = cls()
        action.consumer = consumer
        action.data = data
        return await action.perform_action()

    async def perform_action(self):
        raise NotImplementedError("You must implement 'perform_action' in your action")

    async def get_param(self, key, default=None):
        return self.data.get(key, default)

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        raise NotImplementedError(
            "You must specify either 'queryset' in your action class"
        )

    async def get_object(self, **filters):
        queryset = self.get_queryset()
        return await database_sync_to_async(get_object_or_404)(queryset, **filters)

    async def send_message(self, event):
        await self.consumer.send(text_data=json.dumps(event))
