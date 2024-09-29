from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from MlBackend.FurnitureFinder import consumers
from django.urls import path

# WebSocket URL patterns for Channels
websocket_urlpatterns = [
    path('ws/inference/', consumers.InferenceConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Django’s ASGI application for HTTP requests
    "websocket": URLRouter(websocket_urlpatterns),  # Routes WebSocket connections
})
