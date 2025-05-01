# webscraper_fetcher.py

import logging
import time
import random
from typing import List
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CustomScraper/1.0; +https://yourdomain.com/)"
}
DELAY_RANGE = (1, 3)  # polite delay between requests
KEYWORDS = ["lithium", "cobalt", "nickel", "manganese"]

# Example target site
TARGET_URLS = [
    "https://www.mining.com/category/commodities/lithium/",
    "https://www.mining.com/category/commodities/cobalt/",
    "https://www.mining.com/category/commodities/nickel/",
    "https://www.mining.com/category/commodities/manganese/"
]

def polite_get(url: str) -> requests.Response:
    """
    Perform a polite HTTP GET request with randomized delay.
    """
    time.sleep(random.uniform(*DELAY_RANGE))
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response

def extract_articles_from_mining_com(url: str, keyword: str) -> List[dict]:
    """
    Scrape Mining.com commodity category pages for news articles.

    Args:
        url (str): URL to scrape.
        keyword (str): Keyword associated with the page (for metadata).

    Returns:
        List[dict]: List of articles found.
    """
    articles = []

    response = polite_get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    article_blocks = soup.find_all("div", class_="post-content")

    for block in article_blocks:
        title_tag = block.find("h3", class_="post-title")
        if not title_tag:
            continue
        
        title = title_tag.get_text(strip=True)
        link_tag = title_tag.find("a")
        article_url = link_tag["href"] if link_tag else None
        excerpt = block.find("div", class_="post-excerpt")
        text = excerpt.get_text(strip=True) if excerpt else ""

        record = {
            "timestamp": None,  # mining.com listing page doesn't provide pub date
            "source": "Mining.com",
            "text_or_indicator": text or title,
            "sentiment": None,
            "additional_metadata": {
                "title": title,
                "url": article_url,
                "keyword": keyword
            }
        }
        articles.append(record)

    return articles

def fetch_webscraped_articles() -> pd.DataFrame:
    """
    Fetch articles mentioning specific materials via web scraping (Mining.com).

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting web scraping from target sites...")
    
    records = []

    for url, keyword in zip(TARGET_URLS, KEYWORDS):
        logging.info(f"Scraping {url} for keyword: {keyword}")
        try:
            articles = extract_articles_from_mining_com(url, keyword)
            records.extend(articles)
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")

    df = pd.DataFrame(records)

    if df.empty:
        logging.warning("No articles were scraped.")
    else:
        logging.info(f"Successfully scraped {len(df)} articles.")

    return df

if __name__ == "__main__":
    # For quick testing
    df = fetch_webscraped_articles()
    print(df.head())
