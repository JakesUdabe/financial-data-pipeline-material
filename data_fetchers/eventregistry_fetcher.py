# eventregistry_fetcher.py

import os
import logging
import time
import random
from typing import List
import pandas as pd
from dotenv import load_dotenv
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
KEYWORDS = ["lithium", "cobalt", "nickel", "manganese"]
EVENTREGISTRY_API_KEY = os.getenv("EVENTREGISTRY_API_KEY")

if not EVENTREGISTRY_API_KEY:
    raise ValueError("EVENTREGISTRY_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize EventRegistry client
er = EventRegistry(apiKey=EVENTREGISTRY_API_KEY)

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
            except Exception as e:
                logging.warning(f"Attempt {attempt+1} failed with error: {e}")
                time.sleep(delay)
                delay *= 2 * random.uniform(0.8, 1.5)
        logging.error(f"All {retries} attempts failed for {func.__name__}.")
        raise
    return wrapper

@retry_request
def _fetch_eventregistry_articles_for_keyword(keyword: str, lang: str = "eng", max_items: int = 100) -> List[dict]:
    """
    Internal function to fetch articles from EventRegistry for a given keyword.

    Args:
        keyword (str): Material keyword to search.
        lang (str): Language code, default 'eng'.
        max_items (int): Maximum number of articles to retrieve.

    Returns:
        List[dict]: List of EventRegistry article records.
    """
    query = QueryArticlesIter(
        keywords=keyword,
        lang=lang,
        dataType="news",
        maxItems=max_items
    )

    articles = []
    for article in query.execQuery(er):
        articles.append(article)

    return articles

def fetch_eventregistry_articles() -> pd.DataFrame:
    """
    Fetch articles mentioning specific materials from EventRegistry.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from EventRegistry...")
    
    records = []

    for keyword in KEYWORDS:
        logging.info(f"Fetching EventRegistry articles for keyword: {keyword}")
        articles = _fetch_eventregistry_articles_for_keyword(keyword)
        
        for article in articles:
            record = {
                "timestamp": article.get("dateTime"),
                "source": "EventRegistry",
                "text_or_indicator": article.get("body", "") or article.get("title", ""),
                "sentiment": article.get("sentiment", None),  # EventRegistry sometimes has a sentiment field
                "additional_metadata": {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("title"),
                    "location": article.get("location", {}).get("country", {}).get("label", None),
                    "keyword": keyword
                }
            }
            records.append(record)

    df = pd.DataFrame(records)

    if df.empty:
        logging.warning("No EventRegistry articles were fetched.")
    else:
        logging.info(f"Successfully fetched {len(df)} EventRegistry articles.")

    return df

if __name__ == "__main__":
    # For quick testing
    df = fetch_eventregistry_articles()
    print(df.head())
