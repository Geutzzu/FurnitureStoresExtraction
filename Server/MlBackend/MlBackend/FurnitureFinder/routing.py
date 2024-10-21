from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from MlBackend.FurnitureFinder import consumers
from django.urls import path

# we have exactly one route for the websocket in our application
websocket_urlpatterns = [
    path('ws/inference/', consumers.InferenceConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # django’s ASGI application for HTTP requests
    "websocket": URLRouter(websocket_urlpatterns),  # routes WebSocket connections
})
