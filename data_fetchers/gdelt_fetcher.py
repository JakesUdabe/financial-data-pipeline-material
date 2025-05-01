# gdelt_fetcher.py

import os
import logging
import time
import random
from typing import List
import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
KEYWORDS = ["lithium", "cobalt", "nickel", "manganese"]

def retry_request(func):
    """
    Decorator to retry a function with exponential backoff in case of exceptions.
    """
    def wrapper(*args, **kwargs):
        retries = 3
        delay = 1
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except (RequestException, Exception) as e:
                logging.warning(f"Attempt {attempt+1} failed with error: {e}")
                time.sleep(delay)
                delay *= 2 * random.uniform(0.8, 1.5)
        logging.error(f"All {retries} attempts failed for {func.__name__}.")
        raise
    return wrapper

@retry_request
def _fetch_gdelt_articles_for_keyword(keyword: str, mode: str = "ArtList") -> List[dict]:
    """
    Internal function to fetch articles from GDELT for a given keyword.
    
    Args:
        keyword (str): Material keyword to search.
        mode (str): GDELT mode, default "ArtList" for article list.

    Returns:
        List[dict]: List of GDELT article records.
    """
    params = {
        "query": keyword,
        "mode": mode,
        "format": "json",
        "maxrecords": 250  # reasonable limit for one pull
    }

    response = requests.get(GDELT_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    articles = data.get("articles", [])
    return articles

def fetch_gdelt_articles() -> pd.DataFrame:
    """
    Fetch articles related to commodities from GDELT.
    
    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from GDELT...")
    
    records = []

    for keyword in KEYWORDS:
        logging.info(f"Fetching GDELT articles for keyword: {keyword}")
        articles = _fetch_gdelt_articles_for_keyword(keyword)
        
        for article in articles:
            record = {
                "timestamp": article.get("seendate"),  # when GDELT saw the article
                "source": "GDELT",
                "text_or_indicator": article.get("title", ""),
                "sentiment": None,  # GDELT includes "tone" but not directly mapped here
                "additional_metadata": {
                    "domain": article.get("domain"),
                    "url": article.get("url"),
                    "language": article.get("language"),
                    "sourcecountry": article.get("sourcecountry"),
                    "tone": article.get("socialimage"),
                    "keyword": keyword
                }
            }
            records.append(record)

    df = pd.DataFrame(records)

    if df.empty:
        logging.warning("No GDELT articles were fetched.")
    else:
        logging.info(f"Successfully fetched {len(df)} GDELT articles.")

    return df

if __name__ == "__main__":
    # For quick testing
    df = fetch_gdelt_articles()
    print(df.head())
