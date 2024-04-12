from django.urls import re_path
from app_medassistant.consumers import CommentConsumer

websocket_urlpatterns = [
    re_path('ws', CommentConsumer.as_asgi()),
]
