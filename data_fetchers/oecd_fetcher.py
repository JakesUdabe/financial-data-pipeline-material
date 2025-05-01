# oecd_fetcher.py

import logging
import pandas as pd
import requests
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://stats.oecd.org/SDMX-JSON/data/"
# Dataset to use (e.g., MEI - Main Economic Indicators)
DATASET = "MEI"
INDICATORS = {
    "CPI": "Consumer Price Index",
    "IRL": "Long-Term Interest Rates",
    "IPROD": "Industrial Production"
}
COUNTRIES = ["USA", "CHN", "AUS", "CAN", "CHL", "ZAF"]  # ISO country codes for OECD
START_YEAR = "2015"

def fetch_oecd_series(indicator: str, country: str) -> pd.DataFrame:
    """
    Fetch a single OECD time series.

    Args:
        indicator (str): Indicator code.
        country (str): ISO country code.

    Returns:
        pd.DataFrame: DataFrame with fetched series.
    """
    query = f"{DATASET}/{indicator}.{country}.M/all?startTime={START_YEAR}"
    url = BASE_URL + query
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    
    json_data = response.json()

    try:
        observations = json_data['dataSets'][0]['series']
    except (KeyError, IndexError):
        logging.warning(f"No data found for {country} - {indicator}")
        return pd.DataFrame()

    # Mapping observation indexes to actual periods
    dimensions = json_data['structure']['dimensions']['observation'][0]['values']
    periods = [dim['id'] for dim in dimensions]

    # Extract values
    records = []
    for series_key, series_data in observations.items():
        for obs_idx, obs_value in series_data['observations'].items():
            timestamp = periods[int(obs_idx)]
            value = obs_value[0]
            record = {
                "timestamp": timestamp,
                "source": "OECD",
                "text_or_indicator": f"{INDICATORS[indicator]}: {value}",
                "sentiment": None,
                "additional_metadata": {
                    "country": country,
                    "indicator_code": indicator,
                    "indicator_name": INDICATORS[indicator],
                    "value": value
                }
            }
            records.append(record)

    return pd.DataFrame(records)

def fetch_oecd_data() -> pd.DataFrame:
    """
    Fetch macroeconomic indicators from OECD API.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from OECD Stats API...")
    all_records = []

    for country in COUNTRIES:
        for indicator in INDICATORS.keys():
            try:
                logging.info(f"Fetching OECD data: {country} - {indicator}")
                df = fetch_oecd_series(indicator, country)
                if not df.empty:
                    all_records.append(df)
            except Exception as e:
                logging.error(f"Failed to fetch OECD data for {country} {indicator}: {e}")

    if all_records:
        final_df = pd.concat(all_records, ignore_index=True)
        logging.info(f"Successfully fetched {len(final_df)} OECD records.")
        return final_df
    else:
        logging.warning("No OECD data fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_oecd_data()
    print(df.head())
