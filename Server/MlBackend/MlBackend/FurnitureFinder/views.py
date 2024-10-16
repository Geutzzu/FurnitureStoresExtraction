#
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
#
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# from .Scripts.inference import inference_on_link
# from .Scripts.scraping import get_subpage_links, write_links_to_csv
# import operator
# import asyncio
#
#
# async def send_status_message(phase, message, channel_name):
#     channel_layer = get_channel_layer()
#     await channel_layer.send(
#         channel_name,
#         {
#             'type': 'send_status_message',
#             'message': f"{phase}: {message}"
#         }
#     )
#
# # This function is now asynchronous
# async def send_inference_result(product_name, product_price, product_img_urls, link, channel_name):
#     channel_layer = get_channel_layer()
#     await channel_layer.send(
#         channel_name,
#         {
#             'type': 'send_inference_result',
#             'product_name': product_name,
#             'product_price': product_price,
#             'product_img_urls': product_img_urls,
#             'link': link
#         }
#     )
#
# # create dictionary of websites
# async def scrape_website_links(url, channel_name, is_sitemap=False, custom_sitemap_tags=None, wanted_words=None,
#                          output_file="MlBackend/FurnitureFinder/Data/scraped_links.csv"): # Method to run from other scripts
#     # Initialize the dictionary with the starting URL
#     dict_links = {url: "Not-checked"}
#     dict_href_links = {} # Dictionary to store the href links to not run in any duplicates
#
#     counter, counter2 = None, 0
#
#     while counter != 0:
#         counter2 += 1
#         # Call the function to get subpage links
#         dict_links2 = get_subpage_links(dict_links, dict_href_links, is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags,
#                                         wanted_words=wanted_words)
#
#         # Update the counter to see how many links are left unchecked
#         counter = operator.countOf(dict_links2.values(), "Not-checked")  # Number of "Not-checked" links
#
#         # Debugging statements
#         print("\nTHIS IS LOOP ITERATION NUMBER", counter2)
#         print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
#         print("NUMBER OF 'Not-checked' LINKS =", counter, "\n")
#
#         await send_status_message("Scraping", f"Done {counter2} iterations. Found {len(dict_links2)} links.", channel_name)
#
#         # Update the dictionary with the newly found links
#         dict_links = dict_links2
#
#     # Write the collected links to the specified CSV file
#     # write_links_to_csv(dict_links, output_file)
#     # print(f"Scraping completed. Total links scraped: {len(dict_links)}")
#     print(f"Links saved to {output_file}")
#
#     links = [link for link in dict_links.keys()]
#     return links
#
#
# async def inference_on_link_with_response(link, channel_name, channel_layer):
#     try:
#         result = inference_on_link(link)
#         # Push result to WebSocket
#         await send_inference_result(result[0], result[1], result[2], link, channel_name)
#     except Exception as e:
#         print(f"Error processing link {link}: {e}")
#
#
# async def inference_on_links(links, channel_name, max_workers=16):
#     channel_layer = get_channel_layer()
#     total_links = len(links)
#     processed_links = 0
#
#     # Create a custom executor if needed, or use None to use the default
#     loop = asyncio.get_event_loop()
#
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [loop.run_in_executor(executor, inference_on_link, link) for link in links]
#
#         for future in asyncio.as_completed(futures):
#             try:
#                 result = await future  # Get the result of the inference
#                 link = links[processed_links]
#
#                 # Push result to WebSocket
#                 await send_inference_result(result[0], result[1], result[2], link, channel_name)
#
#                 processed_links += 1
#                 percentage_done = (processed_links / total_links) * 100
#                 await send_status_message("Inference", f"Processed {processed_links}/{total_links} links ({percentage_done:.2f}%)", channel_name)
#
#             except Exception as e:
#                 print(f"Error processing link {links[processed_links]}: {e}")
#
#
# async def processing_user_request(link, channel_name, scrape_subpages=False, custom_sitemap_tags=None, wanted_words=None):
#     channel_layer = get_channel_layer()
#     if scrape_subpages is False:
#         await inference_on_link_with_response(link, channel_name, channel_layer)
#         await send_status_message("Inference", "Inference completed.", channel_name)
#     else:
#         is_sitemap = False
#         if '.xml' in link:
#             is_sitemap = True
#
#         links = await scrape_website_links(link, channel_name ,is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags, wanted_words=wanted_words, output_file="data/scraped_links.csv")
#         await inference_on_links(links, channel_name)
#         await send_status_message("Inference", "Inference completed.", channel_name)