from channels.generic.websocket import AsyncWebsocketConsumer
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
import operator
from .Scripts.inference import inference_on_link
from .Scripts.scraping import get_subpage_links


# websocket consumer which will be connected to a websocket through the frontend
# the websocket logic is simple, any user will connect to the websocket when opening the frontend and can communicate with it
# the user can make a request to get product information from websites and he will receive status updates and the results of the inference
class InferenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept() # accept the connection - no need for any checks

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data): # here the user sends a request to get information about products on a website and / or to scrape the website for more links
        data = json.loads(text_data)
        links = data.get('links')
        scrape_subpages = data.get('scrape_subpages', False)
        custom_sitemap_tags = data.get('custom_sitemap_tags', None)
        wanted_words = data.get('wanted_words', None)
        await self.processing_user_request(links, scrape_subpages=scrape_subpages, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)

    async def send_status_message(self, phase, message): # for sending status updates to the user
        await self.send(text_data=json.dumps({
            'message': f"{phase}: {message}"
        }))

    async def send_inference_result(self, product_name, product_price, product_img_urls, link): # for sending the results of the inference to the user
        await self.send(text_data=json.dumps({
            'product_name': product_name,
            'product_price': product_price,
            'product_img_urls': product_img_urls,
            'link': link
        }))

    # main loop from the notebooks made asynchronous
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

    # inference for one link with status updates
    async def inference_on_link_with_response(self, link):
        try:
            result = inference_on_link(link)
            await self.send_inference_result(result[0], result[1], result[2], link)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    # inference for multiple links with status updates using multithreading
    async def inference_on_links(self, links, max_workers=32):
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


    # code for processing the user request - scraping the website and inferring the product information
    # this will be done for each link sent by the user
    async def processing_user_request(self, links, scrape_subpages=False, custom_sitemap_tags=None, wanted_words=None):
        processed_links = 0

        if scrape_subpages is False:
            for link in links:
                await self.send_status_message("Iteration", f"{processed_links + 1} {link}")
                processed_links += 1

                await self.send_status_message("Inference", "Started inference.")
                await self.inference_on_link_with_response(link)
                await self.send_status_message("Inference", "Inference completed.")

                await asyncio.sleep(0.1) # this is done so that the websocket can send the message before the next iteration
        else:
            for link in links:
                await self.send_status_message("Iteration", f"{processed_links + 1} {link}")
                processed_links += 1

                is_sitemap = False
                if '.xml' in link or '/sitemap' in link: # there are sitemap sublinks that are not XML files - change this if needed
                    is_sitemap = True

                await self.send_status_message("Scraping", "Done 0 iterations. Found 0 links.")
                scraped_links = await self.scrape_website_links(link, is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words)
                await self.send_status_message("Scraping", "Scraping completed.")
                await self.inference_on_links(scraped_links)
                await self.send_status_message("Inference", "Inference completed.")

                await asyncio.sleep(0.1) # this is done so that the websocket can send the message before the next iteration