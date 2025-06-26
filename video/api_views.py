from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Chat
from .serializers import ChatRoomSerializer

class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatRoomSerializer

    def post(self, request):
        room_name = request.data.get('room_name')
        if not room_name:
            return Response({'error': 'Room name is required'}, status=status.HTTP_400_BAD_REQUEST)

        get_room = Chat.objects.filter(room_name=room_name).first()

        if get_room:
            if int(get_room.allowed_user) < 2:
                get_room.allowed_user = str(int(get_room.allowed_user) + 1)
                get_room.save()
            return Response(
                {'message': f'Room "{room_name}" exists, join now.', 'room_id': get_room.id, 'action': 'join'},
                status=status.HTTP_200_OK
            )
        else:
            serializer = self.get_serializer(data={'room_name': room_name, 'allowed_user': 1})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {'message': f'Room "{room_name}" created successfully.', 'room_id': serializer.data['id'], 'action': 'created'},
                status=status.HTTP_201_CREATED, headers=headers
            )

class ChatRoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatRoomSerializer
    lookup_field = 'room_name'