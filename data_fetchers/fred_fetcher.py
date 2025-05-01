# fred_fetcher.py

import logging
import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

INDICATORS = {
    "CPIAUCSL": "Consumer Price Index (All Urban Consumers)",
    "FEDFUNDS": "Federal Funds Effective Rate",
    "INDPRO": "Industrial Production Index"
}
START_DATE = "2015-01-01"

def fetch_fred_data() -> pd.DataFrame:
    """
    Fetch economic indicators from FRED API.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from FRED...")
    all_records = []

    for indicator_code, indicator_name in INDICATORS.items():
        try:
            logging.info(f"Fetching FRED data for {indicator_name} ({indicator_code})...")
            series = fred.get_series(indicator_code, observation_start=START_DATE)
            if series.empty:
                logging.warning(f"No data returned for {indicator_code}.")
                continue

            for timestamp, value in series.items():
                if pd.isna(value):
                    continue
                record = {
                    "timestamp": timestamp,
                    "source": "FRED",
                    "text_or_indicator": f"{indicator_name}: {value}",
                    "sentiment": None,
                    "additional_metadata": {
                        "indicator_code": indicator_code,
                        "indicator_name": indicator_name,
                        "value": value
                    }
                }
                all_records.append(record)

        except Exception as e:
            logging.error(f"Error fetching FRED data for {indicator_code}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        logging.info(f"Successfully fetched {len(df)} FRED records.")
        return df
    else:
        logging.warning("No FRED data fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_fred_data()
    print(df.head())
