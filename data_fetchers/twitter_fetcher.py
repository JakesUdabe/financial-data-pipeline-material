# twitter_fetcher.py

import logging
import os
import pandas as pd
import tweepy
import time
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
KEYWORDS = ["lithium", "cobalt", "battery materials", "nickel", "manganese"]
MAX_RESULTS = 100  # Per page
MAX_TWEETS = 500   # Total limit to avoid rate limit
WAIT_SECONDS = 60  # In case of hitting rate limits

# Twitter Client
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

def fetch_twitter_data() -> pd.DataFrame:
    """
    Fetch public tweets mentioning battery materials.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from Twitter...")
    all_records = []
    query = " OR ".join(KEYWORDS) + " -is:retweet lang:en"

    try:
        tweets = tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            tweet_fields=["created_at", "public_metrics", "author_id"],
            max_results=MAX_RESULTS
        ).flatten(limit=MAX_TWEETS)

        for tweet in tweets:
            metrics = tweet.public_metrics
            record = {
                "timestamp": tweet.created_at,
                "source": "Twitter",
                "text_or_indicator": tweet.text,
                "sentiment": None,  # Placeholder for future sentiment analysis
                "additional_metadata": {
                    "author_id": tweet.author_id,
                    "like_count": metrics.get("like_count"),
                    "retweet_count": metrics.get("retweet_count"),
                    "reply_count": metrics.get("reply_count"),
                    "quote_count": metrics.get("quote_count")
                }
            }
            all_records.append(record)

    except tweepy.TooManyRequests:
        logging.warning("Rate limit hit. Waiting before retrying...")
        time.sleep(WAIT_SECONDS)
    except Exception as e:
        logging.error(f"Error fetching tweets: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        logging.info(f"Successfully fetched {len(df)} tweets.")
        return df
    else:
        logging.warning("No tweets fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_twitter_data()
    print(df.head())
