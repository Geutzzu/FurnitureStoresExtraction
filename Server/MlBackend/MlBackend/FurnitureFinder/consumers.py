from channels.generic.websocket import AsyncWebsocketConsumer
import json

from .views import processing_user_request

class InferenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        link = data.get('link')
        scrape_subpages = data.get('scrape_subpages', False)
        custom_sitemap_tags = data.get('custom_sitemap_tags', None)
        wanted_words = data.get('wanted_words', None)

        await processing_user_request(link, self.channel_name, scrape_subpages=scrape_subpages, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)

    # Event is a dictionary containing the data to be sent to the WebSocket client
    async def send_inference_result(self, event):
        # Extract data from the event dictionary
        product_name = event['product_name']
        product_price = event['product_price']
        product_img_urls = event['product_img_urls']
        link = event['link']

        # Now you can send this data to the WebSocket client
        await self.send(text_data=json.dumps({
            'product_name': product_name,
            'product_price': product_price,
            'product_img_urls': product_img_urls,
            'link': link
        }))

    async def send_status_message(self, event):
        message = event['message']

        # Send the message to the specific WebSocket client
        await self.send(text_data=json.dumps({
            'message': message
        }))