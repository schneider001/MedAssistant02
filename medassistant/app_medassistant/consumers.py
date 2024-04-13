import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Comment, Doctor



class CommentConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            self.user = self.scope['user']
            await self.accept()
        except:
            await self.send(text_data=json.dumps({'type': 'connect_error'}))

    async def disconnect(self, close_code):
        pass
        

    async def receive(self, text_data):
        try:
            function_data = json.loads(text_data)
            function_data['type'] = function_data.pop('action')

            await self.channel_layer.send(
                self.channel_name,
                function_data
            )
        except:
            await self.send(text_data=json.dumps({'type': 'recieve_error'}))



    async def join_room(self, event):
        try:
            room_number = event['room_id']
            self.room_group_name = 'gorup_' + str(room_number)
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        except:
            await self.send(text_data=json.dumps({'type': 'join_room_error'}))



    async def leave_room(self, event):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            await self.send(text_data=json.dumps({'type': 'leave_room_error'}))

    

    async def add_comment(self, event):
        try:
            comment = await database_sync_to_async(Comment.objects.create)(
                comment=event['comment'], 
                doctor_id=self.user.id, 
                request_id=event['request_id']
            )

            doctor = await database_sync_to_async(Doctor.objects.get)(id=self.user.id)
            comment_data = {
                'id': comment.id, 
                'doctor': doctor.name, 
                'time': comment.date.strftime("%Y-%m-%d %H:%M:%S"), 
                'comment': comment.comment
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_except_send',
                    'sender_channel_name': self.channel_name,
                    'type_self': 'self_added_comment',
                    'type_other': 'added_comment',
                    'data_name': 'comment',
                    'data': comment_data
                }
            )
        except:
            await self.send(text_data=json.dumps({'type': 'add_comment_error'}))


        
    async def group_except_send(self, event):
        try:
            if self.channel_name == event['sender_channel_name']:
                await self.send(text_data=json.dumps({
                    'type': event['type_self'],
                    event['data_name']: event['data']
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': event['type_other'],
                    event['data_name']: event['data']
                }))
        except:
            await self.send(text_data=json.dumps({'type': 'group_except_send_error'}))



    async def delete_comment(self, event):
        try:
            comment = await database_sync_to_async(Comment.set_status)(event['comment_id'], Comment.OLD)
            doctor = await database_sync_to_async(Doctor.objects.get)(id=self.user.id)
            comment_data = {
                'id': comment.id, 
                'doctor': doctor.name
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_except_send',
                    'sender_channel_name': self.channel_name,
                    'type_self': 'deleted_comment',
                    'type_other': 'deleted_comment',
                    'data_name': 'comment',
                    'data': comment_data
                }
            )
        except:
            await self.send(text_data=json.dumps({'type': 'delete_comment_error'}))


    async def edit_comment(self, event):
        try:
            new_comment = await database_sync_to_async(Comment.set_comment)(event['comment_id'], event['comment'])

            doctor = await database_sync_to_async(Doctor.objects.get)(id=self.user.id)
            comment_data = {
                'old_id': event['comment_id'],
                'id': new_comment.id, 
                'doctor': doctor.name, 
                'time': new_comment.date.strftime("%Y-%m-%d %H:%M:%S"), 
                'comment': new_comment.comment
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_except_send',
                    'sender_channel_name': self.channel_name,
                    'type_self': 'self_edited_comment',
                    'type_other': 'edited_comment',
                    'data_name': 'comment',
                    'data': comment_data
                }
            )
        except:
            await self.send(text_data=json.dumps({'type': 'edit_comment_error'}))



