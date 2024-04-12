import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Comment, Doctor



class CommentConsumer(AsyncWebsocketConsumer):
    broadcast_functions = ['add_comment']


    async def connect(self):
        print('connect')
        self.user = self.scope['user']
        await self.accept()

    async def disconnect(self, close_code):
        print('disconnect')
        

    async def receive(self, text_data):
        print('receive')
        # Получаем данные комментария
        function_data = json.loads(text_data)
        function_data['type'] = function_data.pop('action')

        if function_data['type'] in self.broadcast_functions:
            await self.channel_layer.group_send(
                self.room_group_name,
                function_data
            )
        else:
            await self.channel_layer.send(
                self.channel_name,
                function_data
            )

    async def join_room(self, event):
        print('join_room')
        room_number = event['room_id']
        self.room_group_name = 'gorup_' + str(room_number)
        print('room_group_name =', self.room_group_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def leave_room(self, event):
        print('leave_room')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    

    async def add_comment(self, event):
        print('add_comment')
        print('event =', event)
        print('user_id =', self.user.id)
        comment = await database_sync_to_async(Comment.objects.create)(
            comment=event['comment'], 
            doctor_id=self.user.id, 
            request_id=event['request_id']
        )

        # Подготовка данных комментария для отправки
        doctor = await database_sync_to_async(Doctor.objects.get)(id=self.user.id)
        comment_data = {
            'id': comment.id, 
            'doctor': doctor.name, 
            'time': comment.date.strftime("%Y-%m-%d %H:%M:%S"), 
            'comment': comment.comment
        }

        # Отправка сообщения об добавленном комментарии
        await self.send(text_data=json.dumps({
            'type': 'self_added_comment',
            'comment': comment_data
        }))

    async def delete_comment(self, event):
        print('delete_comment')
        pass

    async def edit_comment(self, event):
        print('edit_comment')
        pass

