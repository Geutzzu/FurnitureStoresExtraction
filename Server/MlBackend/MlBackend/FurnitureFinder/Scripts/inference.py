# CODE DESCRIPTION PRESENT INSIDE THE NOTEBOOK app_inference.ipynb
import csv
csv.field_size_limit(5000000)
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

from MlBackend.FurnitureFinder.Scripts.boilerplate import get_data

# load the model and tokenizer
model_name = model_checkpoint = "MlBackend/FurnitureFinder/Models/ROB_0.89F1_16B_100000DAT"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
label_list = ['O', 'B-PRODUCT', 'I-PRODUCT']
links_file = 'scraped_links.txt' # not actually used in the app, I kept this in here in case storing the scraped links is needed in the future

def clean_text(s):
    # this pattern keeps only normal alphanumerical characters and some special symbols
    allowed_pattern = r"[^a-zA-Z0-9\s,.:;\'\"!?()\-&+]"
    return re.sub(allowed_pattern, '', s)

def has_letters(input_string):
    # helper method for checking if a string contains any letters
    return any(char.isalpha() for char in input_string)

# this maps each token to its tag in HTML
# this is done so I can find the price and the images of the product after the model has predicted the product name from this page
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

    # finding the title in the head of the HTML
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
    url_last_path = link[url_index + 1:].replace('-', ' ').replace('_', ' ') # the text I am looking for can only be separated by these two characters

    if not has_letters(url_last_path):
        url_last_path = None

    return word_tag_tuples, title, url_last_path, soup


# one observation about cleaning the text in this method is that its usage is subject to change
# depending on the website it may do more harm than good
def formated_link_content(word_tag_tuples, title, url_last_path):
    cleaned_word_tag_tuples = []

    for word, tag in word_tag_tuples:
        clean_word = clean_text(word)
        if clean_word:  # only append if the word is not an empty string
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


# method for predicting the labels of the tokens
def predict_labels(text, model, tokenizer, label_list, max_length=512):
    inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True, is_split_into_words=True)
    word_ids = inputs.word_ids()

    with torch.no_grad():
        outputs = model(**inputs) # these are the logits or the scores for each token

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)

    predictions = [label_list[prediction] for prediction in predictions[0]] # convert the predictions to the actual labels
    tokenized_tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])  # convert the token ids to the actual tokens

    labels = ['O'] * len(text) # initialize the labels with 'O'

    for idx, (token, prediction) in enumerate(zip(tokenized_tokens, predictions)): # assign the predictions to the correct tokens
        original_token_index = word_ids[idx]
        if original_token_index is not None: # we filter out for the tokens that are not part of the original text (sub-word tokens or special tokens)
            labels[original_token_index] = prediction

    return labels

# methods for rule-based price and image extraction (after finding the product name)
def contains_currency(tag):
    currency_symbols = ['$', '€', '£', '¥', '₹', '₽', '₩', '₪', 'RON', 'USD', 'EUR'] # add more...
    if tag and tag.string:
        text = tag.string
        for symbol in currency_symbols:
            if symbol in text:
                return True
    return False

# finds the first currency tag in the soup
# the currency tag will always be located after the product name (down the page)
def find_currency_tag(start_tag):
    if contains_currency(start_tag):
        return start_tag
    while start_tag:
        if contains_currency(start_tag):
            return start_tag
        start_tag = start_tag.find_next()
    return None


# finds the img tags before or after the product name (depending on where they first are found)
# because we know the position of the product (if the model performed well) we can search and hopefully find the correct images
def find_img_tag(start_tag):
    previous_img = start_tag.find_previous('img')
    next_img = start_tag.find_next('img')

    previous_img_class = previous_img.get('class') if previous_img else None # we search up the page
    next_img_class = next_img.get('class') if next_img else None # down the page

    img_srcs = []

    if previous_img:
        while (previous_img.get('class') == previous_img_class) or previous_img_class is None: # we keep going if there are multiple images with the same class (so we can hopefully get the carousel of product images)
            img_src = previous_img.get('src')
            if img_src:
                img_srcs.append(img_src) # append the image source to the list if it exists
            previous_img = previous_img.find_previous('img') # update previous_img
            if not previous_img: # if we don't find any more images, we break and return the list of image sources
                break
        return img_srcs
    elif next_img: # we do the same for the bottom of the page
        while (next_img.get('class') == next_img_class) or next_img_class is None:
            img_src = next_img.get('src')
            if img_src:
                img_srcs.append(img_src)
            next_img = next_img.find_next('img')
            if not next_img:
                break
        return img_srcs
    return None


# takes a sequence of tokens and labels of equal length and returns the start and end index of the product name if found
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


# returns the product name, price, images and the link of the page
def inference_on_link(link):
    word_tag_tuples, title, url_last_path, soup = link_content(link)
    if word_tag_tuples is None:
        print("No HTML content found for the link:", link)
        return None, None, None, link

    input, word_tag_tuples = formated_link_content(word_tag_tuples, title,
                                                   url_last_path)  # this contains the [TEXT] tokens as tuples

    labels = predict_labels(input, model, tokenizer, label_list)

    # slicing in order to get the 3 parts of the input
    url_tokens, url_labels = input[1:input.index('[URL]')], labels[1:input.index('[URL]')]
    title_tokens, title_labels = input[input.index('[TITLE]') + 1:input.index('[TEXT]') - 1], labels[input.index(
        '[TITLE]') + 1:input.index('[TEXT]') - 1]
    text_tokens, text_labels = input[input.index('[TEXT]') + 1: len(input) - 1], labels[input.index('[TEXT]') + 1: len(
        input) - 1]  # !!!

    url_start, url_end = find_product_indices(url_tokens, url_labels)
    title_start, title_end = find_product_indices(title_tokens, title_labels)
    text_start, text_end = find_product_indices(text_tokens, text_labels)

    if text_start is not None:
        product_tag = word_tag_tuples[text_start][1]  # the tag of the first token of the product name
        product_name = ' '.join([token for token in text_tokens[text_start:text_end + 1]])  # the product name
        product_price = find_currency_tag(product_tag)  # the tag of the first token of the price
        product_img = find_img_tag(product_tag)  # the tag of the first token of the image - actually a list of image sources
        product_price, product_img = product_price.get_text() if product_price else None, product_img if product_img else None  # the price and images
        print(product_name, product_price, product_img, link)
        return product_name, product_price, product_img, link  # return the product name, price, images and link
    elif title_start is not None:  # if the product name is in the title and not in the text, the result may actually be easier to find here, since there is less room for error
        product_name = ' '.join([token for token in title_tokens[title_start:title_end + 1]])
        print(product_name, None, None, link)
        return product_name, None, None, link
    elif url_start is not None:  # if the product name is in the url, same as with the title
        product_name = ' '.join([token for token in url_tokens[url_start:url_end + 1]])
        print(product_name, None, None, link)
        return product_name, None, None, link
    print(None, None, None, link)
    return None, None, None, link # return just the link if the product name is not found (in the frontend you don't want to display the link if there is no product name)
    # at least as I coded it, if you want to see what it missed, this can be changed

# inference_on_links... inside consumers.py



