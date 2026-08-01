from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core.constants import ROLE_ADMIN, ROLE_CHEF, ROLE_MANAGER

GROUP_NAME = 'kitchen_queue'
ALLOWED_ROLES = {ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN}


class KitchenConsumer(AsyncJsonWebsocketConsumer):
    """Broadcasts new orders and status changes to every connected
    kitchen-staff client. Nothing is pushed on connect -- the client
    already has the page's server-rendered initial state; this only
    streams what changes after that."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not await self._has_kitchen_role(user):
            await self.close()
            return
        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    @database_sync_to_async
    def _has_kitchen_role(self, user):
        profile = getattr(user, 'profile', None)
        return getattr(profile, 'role', None) in ALLOWED_ROLES

    # Called by channel_layer.group_send(..., {'type': 'kitchen.update', 'payload': {...}})
    async def kitchen_update(self, event):
        await self.send_json(event['payload'])
