import random
import time
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
]

# function to get page content - removed all debug prints (present in other versions of this function)
def get_data(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}  # it uses a random user agent from the list above - it avoids getting IP banned from most websites inside the CSV if I scrape multiple times
    try:
        response = requests.get(url, headers=headers, timeout=3)
        # handle rate-limiting (HTTP 429) by pausing and retrying
        if response.status_code == 429:
            time.sleep(random.uniform(3, 6))  # random delay to avoid detection - you may have to adjust this if you are getting blocked
            return get_data(url)

        if response.status_code == 200:
            return response.content  # return content if successful
        return None

    except requests.RequestException as e:
        return None