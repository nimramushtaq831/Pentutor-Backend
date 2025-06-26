
from rest_framework import serializers
from .models import Chat

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'room_name', 'allowed_user']