import csv

from MlBackend.FurnitureFinder.Scripts.scraping import get_data

csv.field_size_limit(5000000)
import ast
import re

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import random
import time

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

model_name = model_checkpoint = "MlBackend/FurnitureFinder/Models/0.80_F1_64_BATCH_NOT_SL"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
label_list = ['O', 'B-PRODUCT', 'I-PRODUCT']
links_file = 'scraped_links.txt'
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
]

# Function to get page content
def get_data(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}  # Rotate user-agent
    try:
        response = requests.get(url, headers=headers, timeout=3)
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


def read_links_from_csv(csv_filename):
    links = {}
    with open(csv_filename, "r", newline='') as csvfile:
        csvwriter = csv.reader(csvfile)
        for row in csvwriter:
            links[row[0]] = ast.literal_eval(row[1])
    return links


def clean_text(s):
    # Define the pattern to allow only "normal" characters and keep relevant punctuation
    allowed_pattern = r"[^a-zA-Z0-9\s,.:;\'\"!?()\-&+]"

    # Replace irrelevant characters with empty string (i.e., remove them)
    return re.sub(allowed_pattern, '', s)



def has_letters(input_string):
    return any(char.isalpha() for char in input_string)


def soup_mapper(soup, max_tokens=128):
    word_tag_tuples = []
    token_count = 0
    for tag in soup.descendants:
        if token_count >= max_tokens:
            break
        if tag.name and not tag.find_all():
            for word in tag.text.split():
                token_count += 1
                word_tag_tuples.append((word, tag))

    if len(word_tag_tuples) == 0:
        return None
    return word_tag_tuples


def link_content(link):
    html_data = get_data(link)
    if html_data is None:
        return None, None, None, None

    soup = BeautifulSoup(html_data, "html.parser")

    # Finding the title in the meta tags
    title = soup.find('title')
    if title:
        title = title.get_text()
    else:
        title = None

    # Remove scripts, styles, and irrelevant content
    for script in soup(["script", "style", "footer", "nav", "header", "noscript", "head"]):
        script.extract()

    word_tag_tuples = soup_mapper(soup, max_tokens=128)  # by joining word_tag_tuples[0] you get the full text

    url_index = link.rfind('/')
    url_last_path = link[url_index + 1:].replace('-', ' ').replace('_', ' ')

    if not has_letters(url_last_path):
        url_last_path = None

    return word_tag_tuples, title, url_last_path, soup


def formated_link_content(word_tag_tuples, title, url_last_path):
    cleaned_word_tag_tuples = []

    for word, tag in word_tag_tuples:
        clean_word = clean_text(word)
        if clean_word:  # Only append if the word is not an empty string
            cleaned_word_tag_tuples.append((clean_word, tag))

    url_last_path_tokens = clean_text(url_last_path).split() if url_last_path else []
    title_tokens = clean_text(title).split() if title else []

    # Gather text tokens from the cleaned word-tag tuples
    text_tokens = [word_tag_tuple[0] for word_tag_tuple in cleaned_word_tag_tuples]

    # Format the input for the model
    formated_model_input = ['[URL]'] + url_last_path_tokens + ['[URL]', '[TITLE]'] + title_tokens + ['[TITLE]',
                                                                                                     '[TEXT]'] + text_tokens + [
                               '[TEXT]']

    return formated_model_input, cleaned_word_tag_tuples


def predict_labels(text, model, tokenizer, label_list, max_length=512):
    inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True, is_split_into_words=True)
    word_ids = inputs.word_ids()

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)

    predictions = [label_list[prediction] for prediction in predictions[0]]
    tokenized_tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    labels = ['O'] * len(text)

    for idx, (token, prediction) in enumerate(zip(tokenized_tokens, predictions)):
        original_token_index = word_ids[idx]
        if original_token_index is not None:
            labels[original_token_index] = prediction

    return labels


def contains_currency(tag):
    currency_symbols = ['$', '€', '£', '¥', '₹', '₽', '₩', '₪']
    if tag and tag.string:
        text = tag.string
        for symbol in currency_symbols:
            if symbol in text:
                return True
    return False


def find_currency_tag(start_tag):
    if contains_currency(start_tag):
        return start_tag
    while start_tag:
        if contains_currency(start_tag):
            return start_tag
        start_tag = start_tag.find_next()
    return None


def find_img_tag(start_tag):
    previous_img = start_tag.find_previous('img')
    next_img = start_tag.find_next('img')

    previous_img_class = previous_img.get('class') if previous_img else None
    next_img_class = next_img.get('class') if next_img else None

    print(previous_img_class, next_img_class)

    img_srcs = []

    if previous_img:
        while (previous_img.get('class') == previous_img_class) or previous_img_class is None:
            # Check if 'src' attribute exists before appending
            img_src = previous_img.get('src')
            if img_src:
                img_srcs.append(img_src)
            previous_img = previous_img.find_previous('img')
            if not previous_img:
                break
        return img_srcs
    elif next_img:
        while (next_img.get('class') == next_img_class) or next_img_class is None:
            # Check if 'src' attribute exists before appending
            img_src = next_img.get('src')
            if img_src:
                img_srcs.append(img_src)
            next_img = next_img.find_next('img')
            if not next_img:
                break
        return img_srcs
    return None


def find_product_indices(tokens, labels):
    if len(tokens) != len(labels):
        raise ValueError("The length of tokens and labels must be the same.")

    start_index = None

    for i, label in enumerate(labels):
        if label == "B-PRODUCT":
            start_index = i
        elif label != "I-PRODUCT" and start_index is not None:
            return start_index, i - 1

    if start_index is not None:
        return start_index, len(labels) - 1

    return None, None

def inference_on_link(link):
    # print(f"Running inference on: {link}")
    word_tag_tuples, title, url_last_path, soup = link_content(link)
    if word_tag_tuples is None:
        return None, None, None, link

    input, word_tag_tuples = formated_link_content(word_tag_tuples, title,
                                                   url_last_path)  # This contains the [TEXT] tokens as touples

    labels = predict_labels(input, model, tokenizer, label_list)

    url_tokens, url_labels = input[1:input.index('[URL]')], labels[1:input.index('[URL]')]
    title_tokens, title_labels = input[input.index('[TITLE]') + 1:input.index('[TEXT]')], labels[input.index(
        '[TITLE]') + 1:input.index('[TEXT]')]
    text_tokens, text_labels = input[input.index('[TEXT]') + 1: len(input) - 1], labels[input.index('[TEXT]') + 1: len(
        input) - 1]  # !!!

    url_start, url_end = find_product_indices(url_tokens, url_labels)
    title_start, title_end = find_product_indices(title_tokens, title_labels)
    text_start, text_end = find_product_indices(text_tokens, text_labels)

    if text_start is not None:
        product_tag = word_tag_tuples[text_start][1]
        product_name = ' '.join([token for token in text_tokens[text_start:text_end + 1]])
        product_price = find_currency_tag(product_tag)
        product_img = find_img_tag(product_tag)
        product_price, product_img = product_price.get_text() if product_price else None, product_img if product_img else None
        return product_name, product_price, product_img, link
    elif title_start is not None:
        product_name = title_tokens[title_start:title_end + 1]
        return product_name, None, None, link
    elif url_start is not None:
        product_name = url_tokens[url_start:url_end + 1]
        return product_name, None, None, link
    return None, None, None, link


# print(inference_on_link(
#     'https://claytongrayhome.com/sitemap_products_1.xml?from=7491002949&to=6858385588272'))


# def inference_on_links(links, max_workers=32):
#     results = []
#     # ThreadPoolExecutor for concurrent execution
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         # Submit tasks for concurrent execution
#         futures = {executor.submit(inference_on_link, link): link for link in links}
#
#         for future in as_completed(futures):
#             link = futures[future]
#             try:
#                 result = future.result()  # Get the result of the inference
#                 results.append(result)
#                 print(f"Processed link: {link}, result: {result}")
#             except Exception as e:
#                 print(f"Error processing link {link}: {e}")
#
#     return results



# class FileUpdateHandler(FileSystemEventHandler):
#     def __init__(self, inference_callback, links_file):
#         self.inference_callback = inference_callback
#         self.links_file = links_file
#         self.processed_links = set()
#
#     def on_modified(self, event):
#         if event.src_path == self.links_file:
#             with open(self.links_file, 'r') as file:
#                 for line in file:
#                     link = line.strip()
#                     if link not in self.processed_links:
#                         self.processed_links.add(link)
#                         # Trigger inference on new link
#                         self.inference_callback(link)
#
#
# event_handler = FileUpdateHandler(inference_callback=inference_on_link, links_file=links_file)
# observer = Observer()
# observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(links_file)), recursive=False)
# observer.start()
