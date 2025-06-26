# video/urls.py
from django.urls import path
from . import views
from . import api_views 

urlpatterns = [
    path('', views.index, name='index'),
    path('video/<str:room>/<str:created>/', views.video, name='video'),
    path('api/rooms/', api_views.ChatRoomListCreateAPIView.as_view(), name='api_chat_rooms'),
    path('api/rooms/<str:room_name>/', api_views.ChatRoomDetailAPIView.as_view(), name='api_chat_room_detail'),
]