import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'webrtc_{self.room_name}'

        self.user_ip = self.scope.get('client', ['unknown', None])[0]
     
        if self.channel_layer is None:
            raise RuntimeError("Django Channels channel_layer is not configured. Please check your ASGI and CHANNEL_LAYERS settings.")
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user_ip} connected to room {self.room_name}")
        

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.channel_name,
                'user_ip': self.user_ip,
                'sender': self.channel_name
            }
        )

    async def disconnect(self, close_code):
        logger.info(f"User {self.user_ip} disconnected from room {self.room_name}")
        
        if self.channel_layer is None:
            raise RuntimeError("Django Channels channel_layer is not configured. Please check your ASGI and CHANNEL_LAYERS settings.")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.channel_name,
                'user_ip': self.user_ip,
                'sender': self.channel_name
            }
        )
        
    
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.info(f"Received {message_type} from {self.user_ip}")
            
            if self.channel_layer is None:
                raise RuntimeError("Django Channels channel_layer is not configured. Please check your ASGI and CHANNEL_LAYERS settings.")
            if message_type == 'offer':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'webrtc_offer',
                        'offer': data['offer'],
                        'sender': self.channel_name,
                        'sender_ip': self.user_ip,
                        'target': data.get('target')
                    }
                )
            elif message_type == 'answer':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'webrtc_answer',
                        'answer': data['answer'],
                        'sender': self.channel_name,
                        'sender_ip': self.user_ip,
                        'target': data.get('target')
                    }
                )
            elif message_type == 'ice_candidate':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'webrtc_ice_candidate',
                        'candidate': data['candidate'],
                        'sender': self.channel_name,
                        'sender_ip': self.user_ip,
                        'target': data.get('target')
                    }
                )
            elif message_type == 'get_room_users':
               
                await self.send(text_data=json.dumps({
                    'type': 'room_users',
                    'users': []  
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from {self.user_ip}")

    async def user_joined(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'user_ip': event['user_ip']
            }))

    async def user_left(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'user_ip': event['user_ip']
            }))

    async def webrtc_offer(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': event['offer'],
                'sender': event['sender'],
                'sender_ip': event['sender_ip']
            }))

    async def webrtc_answer(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'answer': event['answer'],
                'sender': event['sender'],
                'sender_ip': event['sender_ip']
            }))

    async def webrtc_ice_candidate(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'candidate': event['candidate'],
                'sender': event['sender'],
                'sender_ip': event['sender_ip']
            }))