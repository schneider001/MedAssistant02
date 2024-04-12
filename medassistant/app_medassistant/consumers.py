import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = 'comments'
        self.room_group_name = 'comment_group_'
        print("Hello from CommentConsumer.connect")
        print(AsyncWebsocketConsumer().__dir__())
        # Присоединяемся к группе комментариев
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу комментариев
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Получаем данные комментария
        comment = json.loads(text_data)

        # Отправляем комментарий в группу комментариев
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_message',
                'text': comment['text']
            }
        )

    async def comment_message(self, event):
        # Отправляем полученный комментарий клиентам
        await self.send(text_data=json.dumps({
            'text': event['text']
        }))