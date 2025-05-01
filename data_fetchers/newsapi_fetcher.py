# newsapi_fetcher.py

import os
import logging
import time
import random
from typing import List
from dotenv import load_dotenv
import pandas as pd
from newsapi import NewsApiClient
from requests.exceptions import RequestException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
KEYWORDS = ["lithium", "cobalt", "nickel", "manganese"]
MAX_PAGE_SIZE = 100  # NewsAPI max page size
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

if not NEWSAPI_KEY:
    raise ValueError("NEWSAPI_KEY not found in environment variables. Please set it in your .env file.")

# Initialize NewsAPI Client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

def retry(max_attempts=3, delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logging.warning(f"Attempt {attempt + 1} failed with error: {e}")
                    time.sleep(delay)
            logging.error(f"All {max_attempts} attempts failed for {func.__name__}.")
            raise last_exception  # Raise the last caught exception properly
        return wrapper
    return decorator

@retry(max_attempts=3, delay=3)
def _fetch_articles_for_keyword(keyword: str) -> list:
    logging.info(f"Fetching articles for keyword: {keyword}")
    
    all_articles = []
    page = 1
    page_size = 100  # Max allowed in free plan

    # Only fetch page 1, no pagination beyond 100 articles
    response = newsapi.get_everything(
        q=keyword,
        language="en",
        sort_by="publishedAt",
        page_size=page_size,
        page=page
    )
    
    if response.get('status') != 'ok':
        raise Exception(response)
    
    all_articles.extend(response.get('articles', []))
    
    return all_articles

def fetch_newsapi_articles() -> pd.DataFrame:
    """
    Fetch articles mentioning specific materials from NewsAPI.
    
    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from NewsAPI...")
    
    records = []

    for keyword in KEYWORDS:
        logging.info(f"Fetching articles for keyword: {keyword}")
        articles = _fetch_articles_for_keyword(keyword)
        
        for article in articles:
            record = {
                "timestamp": article.get("publishedAt"),
                "source": "NewsAPI",
                "text_or_indicator": article.get("content") or article.get("description") or "",
                "sentiment": None,  # No sentiment analysis here yet
                "additional_metadata": {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "source_name": article.get("source", {}).get("name"),
                    "keyword": keyword
                }
            }
            records.append(record)

    df = pd.DataFrame(records)

    if df.empty:
        logging.warning("No articles were fetched.")
    else:
        logging.info(f"Successfully fetched {len(df)} articles.")

    return df

if __name__ == "__main__":
    # For quick testing
    df = fetch_newsapi_articles()
    print(df.head())
