from channels.generic.websocket import AsyncWebsocketConsumer
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
import operator
from .Scripts.inference import inference_on_link
from .Scripts.scraping import get_subpage_links


class InferenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        links = data.get('links')
        scrape_subpages = data.get('scrape_subpages', False)
        custom_sitemap_tags = data.get('custom_sitemap_tags', None)
        wanted_words = data.get('wanted_words', None)
        await self.processing_user_request(links, scrape_subpages=scrape_subpages, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)

    async def send_status_message(self, phase, message):
        await self.send(text_data=json.dumps({
            'message': f"{phase}: {message}"
        }))

    async def send_inference_result(self, product_name, product_price, product_img_urls, link):
        await self.send(text_data=json.dumps({
            'product_name': product_name,
            'product_price': product_price,
            'product_img_urls': product_img_urls,
            'link': link
        }))

    async def scrape_website_links(self, url, is_sitemap=False, custom_sitemap_tags=None, wanted_words=None, output_file="data/scraped_links.csv"):
        dict_links = {url: "Not-checked"}
        dict_href_links = {}
        counter, counter2 = None, 0

        while counter != 0:
            counter2 += 1
            dict_links2 = get_subpage_links(dict_links, dict_href_links, is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)

            await asyncio.sleep(0.1)
            counter = operator.countOf(dict_links2.values(), "Not-checked")
            await self.send_status_message("Scraping", f"Done {counter2} iterations. Found {len(dict_links2)} links.")
            dict_links = dict_links2

        links = [link for link in dict_links.keys()]
        return links

    # Refactor inference_on_link_with_response inside the consumer
    async def inference_on_link_with_response(self, link):
        try:
            result = inference_on_link(link)
            await self.send_inference_result(result[0], result[1], result[2], link)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    # Refactor inference_on_links inside the consumer
    async def inference_on_links(self, links, max_workers=16):
        total_links = len(links)
        processed_links = 0

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [loop.run_in_executor(executor, inference_on_link, link) for link in links]

            for future in asyncio.as_completed(futures):
                try:
                    result = await future
                    link = links[processed_links]

                    await self.send_inference_result(result[0], result[1], result[2], result[3])

                    processed_links += 1
                    percentage_done = (processed_links / total_links) * 100
                    await self.send_status_message("Inference", f"Processed {processed_links}/{total_links} links ({percentage_done:.2f}%)")

                except Exception as e:
                    print(f"Error processing link {links[processed_links]}: {e}")

    # Refactor processing_user_request inside the consumer
    async def processing_user_request(self, links, scrape_subpages=False, custom_sitemap_tags=None, wanted_words=None):
        processed_links = 0

        if scrape_subpages is False:
            for link in links:
                await self.send_status_message("Iteration", f"{processed_links + 1} {link}")
                processed_links += 1

                await self.inference_on_link_with_response(link)
                await self.send_status_message("Inference", "Inference completed.")
        else:
            for link in links:
                await self.send_status_message("Iteration", f"{processed_links + 1} {link}")
                processed_links += 1

                is_sitemap = False
                if '.xml' in link:
                    is_sitemap = True

                await self.send_status_message("Scraping", "Done 0 iterations. Found 0 links.")
                scraped_links = await self.scrape_website_links(link, is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)
                await self.send_status_message("Scraping", "Scraping completed.")
                await self.inference_on_links(scraped_links)
                await self.send_status_message("Inference", "Inference completed.")
