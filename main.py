import csv
import requests
from urllib.parse import urljoin

# List of common sitemap paths to check
SITEMAP_PATHS = [
    "sitemap.xml",
    "sitemap_index.xml",
    ".sitemap.xml",
    "sitemap/sitemap.xml",
    "sitemap_index/sitemap.xml"
]

def check_sitemap(base_url):
    """
    Check if the given base URL has a sitemap in one of the common paths.
    Returns the URL of the sitemap if found, otherwise None.
    """
    for sitemap_path in SITEMAP_PATHS:
        sitemap_url = urljoin(base_url, sitemap_path)
        try:
            response = requests.head(sitemap_url, timeout=10)
            # Check if the URL exists and returns a successful status code (200)
            if response.status_code == 200:
                return sitemap_url
        except requests.RequestException as e:
            print(f"Error checking {sitemap_url}: {e}")
            continue
    return None

def main():
    input_csv = "final_links.csv"  # Input CSV file containing list of URLs
    output_csv = "sitemap_results.csv"  # Output CSV file for results

    # Open the input CSV file
    with open(input_csv, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        urls = list(csvreader)  # Read all URLs into a list

    results = []

    # Check each URL for a sitemap
    for url in urls:
        base_url = url[0].strip()  # Get the base URL from the CSV row
        website_origin = base_url
        collections_index = base_url.find('/collections/')
        if collections_index != -1:
            website_origin = base_url[:collections_index + 1]
        sitemap_url = check_sitemap(website_origin)  # Check for sitemap

        if sitemap_url:
            results.append([website_origin, "Sitemap found", sitemap_url])
            print(f"Sitemap found for {website_origin}: {sitemap_url}")
        else:
            results.append([website_origin, "No sitemap found"])
            print(f"No sitemap found for {website_origin}")

    # Write the results to the output CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["URL", "Status", "Sitemap URL"])  # Header row
        csvwriter.writerows(results)  # Write all results

    print(f"Results saved to {output_csv}.")

if __name__ == "__main__":
    main()
