# CODE DESCRIPTION PRESENT INSIDE THE app_scraping.jpynb FILE
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import concurrent
from urllib.parse import urlparse

from MlBackend.FurnitureFinder.Scripts.boilerplate import get_data


# user input variables
wanted_words = None  # words that should be in the URL
is_sitemap = True # whether the URL is a sitemap or not - not actually user input the user can input a sitemap
custom_sitemap_tags = None # custom tags to look for in the sitemap

def get_base_url(url):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception as e:
        return None


def is_valid_link(url,
                  wanted_words=None):
    # Exclude common unwanted patterns
    unwanted_patterns = [
    # Account/Authentication Related
    "login", "sign-up", "register", "account", "auth", "forgot-password",
    "reset-password", "logout", "user-profile",

    # Non-Product Pages
    "blog", "article", "news", "press", "about-us", "team", "careers", "jobs",
    "contact", "help", "faq", "support", "terms", "privacy-policy", "disclaimer",
    "feedback", "reviews", "promotions",

    # Media or External Resources
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".video", ".audio", ".image", ".media",
    ".download", "upload", "assets", "static", "css", "js", "fonts", "icons",

    # Advertising and Tracking
    "ads", "ad", "affiliate", "campaign", "referral", "tracking", "utm_",

    # Search and Filtering
    "search", "filter", "query", "results", "sort", "pagination",

    # Non-Essential Pages
    "rss", "archive", "calendar", "event", "newsletter", "survey",

    # E-commerce Irrelevant Pages
    "cart", "checkout", "order-history", "wishlist", "invoice", "payment",
    "shipping", "return-policy",

    # Miscellaneous
    "javascript", "mailto:", "tel:", "sms:", "geo:", "maps.", "calendar.", "webinar",

    # Social Media
    "twitter.com", "facebook.com", "instagram.com", "linkedin.com", "pinterest.com", "youtube.com", "tiktok.com",
    "snapchat.com", "whatsapp.com", "reddit.com", "tumblr.com", "vimeo.com", "flickr.com", "quora.com", "medium.com",
    "sharer.php", "share.php", "share?", "share=", "share/", "share-", "share.", "share_", "share~", "share&",
]
    for pattern in unwanted_patterns:
        if pattern in url:
            return False
    if wanted_words is None:
        return True
    for word in wanted_words:
        if word in url:
            return True
    return False

def get_links_from_sitemap(website_link, dict_href_links,  custom_sitemap_tags=None,
                           wanted_words=None):  # modified version from the one in the other notebook
    # set the base of the URL depending on whether "collections" or "products" is in the link
    website_origin = get_base_url(website_link)

    html_data = get_data(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    list_links = []

    tags = ["loc"]
    if custom_sitemap_tags is not None:
        tags = custom_sitemap_tags

    for link in soup.find_all(tags):  # this contains the links inside xml files
        link = link.text
        if not is_valid_link(link, wanted_words):
            continue

        link_to_append = None

        # handle absolute URLs that start with the origin
        if link.startswith(str(website_origin)):
            link_to_append = link

        # handle relative URLs that start with "/"
        elif link.startswith("/"):
            link_with_www = website_origin + link[1:]
            link_to_append = link_with_www

        # if link_to_append is not None, check if it's already in dict_href_links and if it's accessible
        if link_to_append is not None:
            if link_to_append not in dict_href_links:  # and check_website(link_to_append) - I will not check the links here, I will check them after I get all the links
                dict_href_links[link_to_append] = None  # mark it as seen

                list_links.append(link_to_append)

    # convert list of links to a dictionary with "Not-checked" as the default value for each
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links, dict_href_links

def soup_trimmer(soup):
    for script in soup(["script", "style", "footer", "nav", "header", "noscript", "head"]):
        script.extract()
    return soup


def get_links(website_link, dict_href_links,  wanted_words=None):
    website_origin = get_base_url(website_link)

    html_data = get_data(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    soup = soup_trimmer(soup)
    list_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # filter out invalid links (non-product/collection pages)
        if not is_valid_link(href, wanted_words):
            continue

        link_to_append = None

        # handle absolute URLs that start with the origin
        if href.startswith(str(website_origin)):
            link_to_append = href

        # handle relative URLs that start with "/"
        elif href.startswith("/"):
            link_with_www = website_origin + href
            link_to_append = link_with_www

        # if link_to_append is not None, check if it's already in dict_href_links and if it's accessible
        if link_to_append is not None:
            if link_to_append not in dict_href_links:  # and check_website(link_to_append) - I will not check the links here, I will check them after I get all the links
                dict_href_links[link_to_append] = None  # mark it as seen
                list_links.append(link_to_append)

    # convert list of links to a dictionary with "Not-checked" as the default value for each
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links, dict_href_links


def write_links_to_csv(links_dict, csv_filename):
    with open(csv_filename, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for link in links_dict.keys():
            csvwriter.writerow([link])

    print(f"Links saved to {csv_filename}.")


def get_subpage_links(l, dict_href_links, is_sitemap=False, custom_sitemap_tags=None, wanted_words=None, max_depth=2, current_depth=0,
                      write_frequency=20, csv_filename="app_feature_test.csv"):
    processed_links_count = 0
    dict_href_links_new = dict_href_links.copy()

    if current_depth >= max_depth:
        return l

    with ThreadPoolExecutor(max_workers=32) as executor:
        if is_sitemap:
            futures = {executor.submit(get_links_from_sitemap, link, dict_href_links ,custom_sitemap_tags, wanted_words): link for link
                       in l if l[link] == "Not-checked"}
        else:
            futures = {executor.submit(get_links, link, dict_href_links , wanted_words): link for link in l if l[link] == "Not-checked"}

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                           desc="Processing subpage links"):
            link = futures[future]
            try:
                dict_links_subpages, dict_href_links_new = future.result()
            except Exception as e:
                l[link] = "Checked"
                processed_links_count += 1

                # write to file every 'write_frequency' processed links - left this here in case I decided to store scraped links but as it stands I am not using this
                if processed_links_count >= write_frequency:
                    processed_links_count = 0  # reset the counter
                continue
            l[link] = "Checked"
            l.update(dict_links_subpages)
            processed_links_count += 1

            # write to file every 'write_frequency' processed links
            if processed_links_count >= write_frequency:
                processed_links_count = 0  # Reset the counter

    # recursively call the function for the next depth level (max depth level is left at 2 so that the scraping does not take too long)
    return get_subpage_links(l, dict_href_links_new , is_sitemap, custom_sitemap_tags, wanted_words, max_depth, current_depth + 1,
                             write_frequency, csv_filename)


# main loop inside consumers.py ...


