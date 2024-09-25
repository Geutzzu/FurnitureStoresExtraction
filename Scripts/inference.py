import csv

from Scripts.scraping import get_data

csv.field_size_limit(5000000)
import ast
import operator
import re


import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
import concurrent

import scraping # get_data will be used




def read_links_from_csv(csv_filename):
    """Writes the current state of the links dictionary to a CSV file."""
    links = {}
    with open(csv_filename, "r", newline='') as csvfile:
        csvwriter = csv.reader(csvfile)
        for row in csvwriter:
            links[row[0]] = ast.literal_eval(row[1])
    return links

def clean_text(text):
    # Replace multiple spaces and line breaks with a single space
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    return cleaned_text



def formated_link_content(link):
    html_data = get_data(link)
    if html_data is None:
        return None
    soup = BeautifulSoup(html_data, "html.parser")
    # Remove scripts, styles, and irrelevant content
    for script in soup(["script", "style", "footer", "nav", "header", "noscript", "head"]):
        script.extract()

    for tag in soup.descendants:
        if tag.name:  # Check if it's a tag (not a string)
            print(tag.name, tag.text)

    page_text = clean_text(soup.get_text(separator=' '))


    return page_text


formated_link_content("https://www.ikea.com/ro/ro/p/styrspel-scaun-de-gaming-purpuriu-negru-20522027/")


# TBD
