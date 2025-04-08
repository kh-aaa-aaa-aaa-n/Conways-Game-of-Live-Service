import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        await self.channel_layer.group_add("game_room", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("game_room", self.channel_name)

    async def receive(self, text_data):
        ### TODO: Maybe implement something here for the move timeout
        self.can_move = True
        if not self.can_move:
            await self.send(text_data = json.dumps({
                "type": "error",
                "message": "You must wait before making another move."
            }))
            return
        ############################################################

        await self.channel_layer.group_send(
            "game_room",
            {
                "type": "send_move",
                "message": text_data
            }
        )

    async def send_move(self, event):
        await self.send(text_data=event["message"])
