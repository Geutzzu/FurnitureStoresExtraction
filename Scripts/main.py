from numpy.ma.core import product

import inference
import scraping

import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor

link_queue = queue.Queue()

def inference_worker():
    with ThreadPoolExecutor(max_workers=30) as executor:  # Adjust the max_workers as needed
        while True:
            try:
                link = link_queue.get(block=True, timeout=1)
                future = executor.submit(inference.inference_on_link, link)
                result = future.result()  # Get the result of the inference
                print(f"Processed link: {link}, result: {result}")
                link_queue.task_done()
            except queue.Empty:
                print("Queue is empty, waiting for more links...")
                time.sleep(1)


inference_thread = threading.Thread(target=inference_worker)
inference_thread.daemon = True  # Allows the thread to exit when the main program exits
inference_thread.start()

sitemap = "https://claytongrayhome.com/sitemap.xml"

scraping.scrape_website_links(sitemap, link_queue, is_sitemap=True, wanted_words=["product", 'collections', 'products', 'collection'])