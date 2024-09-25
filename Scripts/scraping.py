import csv
import operator
import re
import threading

import sys

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
import concurrent

from urllib.parse import urlparse
from urllib.parse import urljoin

import spacy  # we use this for word similarity

from collections import defaultdict
import random
import time


dict_href_links = {}  # Dictionary to store all the links found
wanted_words = None  # Words that should be in the URL
is_sitemap = True
custom_sitemap_tags = None

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
]

def get_base_url(url):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        # print(f"Error parsing URL {url}: {e}")
        return None


def get_data(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}  # Rotate user-agent

    try:
        response = requests.get(url, headers=headers, timeout=5)

        # Handle rate-limiting (HTTP 429) by pausing and retrying
        if response.status_code == 429:
            tqdm.write(f"FROM GET_DATA: Rate limit reached. Sleeping before retrying {url}")
            # print(f"FROM GET_DATA: Rate limit reached. Sleeping before retrying {url}")
            time.sleep(random.uniform(4, 8))  # Random delay to avoid detection
            return get_data(url)

        if response.status_code == 200:
            return response.content  # Return HTML content if successful

        tqdm.write(f"FROM GET_DATA: Failed to retrieve {url}, Status Code: {response.status_code}")

        # print(f"FROM GET_DATA: Failed to retrieve {url}, Status Code: {response.status_code}")
        return None

    except requests.RequestException as e:
        tqdm.write(f"FROM GET_DATA: Error fetching {url}: {e}")
        # print(f"FROM GET_DATA: Error fetching {url}: {e}")
        return None




def is_valid_link(url,
                  wanted_words=None):  # I used these parameters in case I separate the two app features, but I dont see the need right now (they are basically global variables I know but its python)
    # Exclude common unwanted patterns
    unwanted_patterns = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.ico', 'tel:', 'mailto:', '#',
                         'twitter', 'instagram', 'facebook', 'youtube', 'pinterest', 'linkedin', 'whatsapp']
    for pattern in unwanted_patterns:
        if pattern in url:
            return False
    if wanted_words is None:
        return True
    # Only accept URLs that contain "collections" or "products"
    for word in wanted_words:
        if word in url:
            return True
    return False


def get_links_from_sitemap(website_link, custom_sitemap_tags=None,
                           wanted_words=None):  # modified version from the one in the other notebook
    # Set the base of the URL depending on whether "collections" or "products" is in the link
    website_origin = get_base_url(website_link)

    html_data = get_data(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    list_links = []

    tags = ["loc"]
    if custom_sitemap_tags is not None:
        tags = custom_sitemap_tags

    for link in soup.find_all(tags):  # this contains the links inside xml files
        link = link.text
        # Filter out invalid links (non-product/collection pages)

        if not is_valid_link(link, wanted_words):
            continue

        link_to_append = None

        # Handle absolute URLs that start with the origin
        if link.startswith(str(website_origin)):
            link_to_append = link

        # Handle relative URLs that start with "/"
        elif link.startswith("/"):
            # print(href)
            link_with_www = website_origin + link[1:]
            # print("adjusted link =", link_with_www)
            link_to_append = link_with_www

        # If link_to_append is not None, check if it's already in dict_href_links and if it's accessible
        if link_to_append is not None:
            if link_to_append not in dict_href_links:  # and check_website(link_to_append) - I will not check the links here, I will check them after I get all the links
                dict_href_links[link_to_append] = None  # Mark it as seen

                list_links.append(link_to_append)

    # Convert list of links to a dictionary with "Not-checked" as the default value for each
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links


def get_links(website_link, wanted_words=None):
    # Set the base of the URL depending on whether "collections" or "products" is in the link
    website_origin = get_base_url(website_link)

    html_data = get_data(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    list_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # Filter out invalid links (non-product/collection pages)
        if not is_valid_link(href, wanted_words):
            continue

        link_to_append = None

        # Handle absolute URLs that start with the origin
        if href.startswith(str(website_origin)):
            link_to_append = href

        # Handle relative URLs that start with "/"
        elif href.startswith("/"):
            # print(href)
            link_with_www = website_origin + href[1:]
            # print("adjusted link =", link_with_www)
            link_to_append = link_with_www

        # If link_to_append is not None, check if it's already in dict_href_links and if it's accessible
        if link_to_append is not None:
            if link_to_append not in dict_href_links:  # and check_website(link_to_append) - I will not check the links here, I will check them after I get all the links
                dict_href_links[link_to_append] = None  # Mark it as seen
                list_links.append(link_to_append)

    # Convert list of links to a dictionary with "Not-checked" as the default value for each
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links


def get_subpage_links(l, is_sitemap=False, custom_sitemap_tags=None, wanted_words=None, max_depth=3, current_depth=0,
                      write_frequency=20, csv_filename="app_feature_test.csv"):
    processed_links_count = 0

    if current_depth >= max_depth:
        return l

    with ThreadPoolExecutor(max_workers=32) as executor:

        if is_sitemap:
            futures = {executor.submit(get_links_from_sitemap, link, custom_sitemap_tags, wanted_words): link for link
                       in l if l[link] == "Not-checked"}
        else:
            futures = {executor.submit(get_links, link, wanted_words): link for link in l if l[link] == "Not-checked"}

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                           desc="Processing subpage links"):
            link = futures[future]
            try:
                dict_links_subpages = future.result()
                # print(f"Processed {link} with {len(dict_links_subpages)} subpages.")
            except Exception as e:
                print(f"Error fetching {link}: {e}")
                continue
            l[link] = "Checked"
            l.update(dict_links_subpages)

            processed_links_count += 1

            # Write to file every 'write_frequency' processed links
            if processed_links_count >= write_frequency:  # this actually writes all the links to the csv file - even the not checked ones but in my case it is sufficient
                write_links_to_csv(l, csv_filename)
                processed_links_count = 0  # Reset the counter

    # Recursively call the function for the next depth level
    return get_subpage_links(l, is_sitemap, custom_sitemap_tags, wanted_words, max_depth, current_depth + 1,
                             write_frequency, csv_filename)


def write_links_to_csv(links_dict, csv_filename):
    """Writes the current state of the links dictionary to a CSV file."""
    with open(csv_filename, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for link in links_dict.keys():
            csvwriter.writerow([link])

    print(f"Links saved to {csv_filename}.")


# create dictionary of websites
def scrape_website_links(url, is_sitemap=False, custom_sitemap_tags=None, wanted_words=None,
                         output_file="app_feature_test.csv"): # Method to run from other scripts
    # Initialize the dictionary with the starting URL
    dict_links = {url: "Not-checked"}

    counter, counter2 = None, 0

    while counter != 0:
        counter2 += 1
        # Call the function to get subpage links
        dict_links2 = get_subpage_links(dict_links, is_sitemap=is_sitemap, custom_sitemap_tags=custom_sitemap_tags,
                                        wanted_words=wanted_words)

        # Update the counter to see how many links are left unchecked
        counter = operator.countOf(dict_links2.values(), "Not-checked")  # Number of "Not-checked" links

        # Debugging statements
        print("\nTHIS IS LOOP ITERATION NUMBER", counter2)
        print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
        print("NUMBER OF 'Not-checked' LINKS =", counter, "\n")

        # Update the dictionary with the newly found links
        dict_links = dict_links2

    # Write the collected links to the specified CSV file
    write_links_to_csv(dict_links, output_file)

    print(f"Scraping completed. Total links scraped: {len(dict_links)}")
    print(f"Links saved to {output_file}")