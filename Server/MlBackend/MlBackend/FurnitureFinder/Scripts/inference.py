# CODE DESCRIPTION PRESENT INSIDE THE NOTEBOOK app_inference.ipynb
import csv
csv.field_size_limit(5000000)
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

from MlBackend.FurnitureFinder.Scripts.boilerplate import get_data

# load the model and tokenizer
model_name = model_checkpoint = "MlBackend/FurnitureFinder/Models/ROB_0.81F1_16B_12000DAT"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
label_list = ['O', 'B-PRODUCT', 'I-PRODUCT']
links_file = 'scraped_links.txt'

def clean_text(s):
    # this pattern keeps only normal alphanumerical characters and some special symbols
    allowed_pattern = r"[^a-zA-Z0-9\s,.:;\'\"!?()\-&+]"
    return re.sub(allowed_pattern, '', s)

def has_letters(input_string):
    return any(char.isalpha() for char in input_string)

# this maps the each token to its tag in html
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

    # finding the title in the meta tags
    title = soup.find('title')
    if title:
        title = title.get_text()
    else:
        title = None

    # remove scripts, styles, and irrelevant content
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

    # gather text tokens from the cleaned word-tag tuples
    text_tokens = [word_tag_tuple[0] for word_tag_tuple in cleaned_word_tag_tuples]

    # format the input for the model
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


# methods for rule based price and image extraction (after finding the product name)
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
            # check if 'src' attribute exists before appending
            img_src = previous_img.get('src')
            if img_src:
                img_srcs.append(img_src)
            previous_img = previous_img.find_previous('img')
            if not previous_img:
                break
        return img_srcs
    elif next_img:
        while (next_img.get('class') == next_img_class) or next_img_class is None:
            # check if 'src' attribute exists before appending
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
    word_tag_tuples, title, url_last_path, soup = link_content(link)
    if word_tag_tuples is None:
        return None, None, None, link

    input, word_tag_tuples = formated_link_content(word_tag_tuples, title,
                                                   url_last_path)  # this contains the [TEXT] tokens as tuples

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

# inference_on_links... inside consumers.py



