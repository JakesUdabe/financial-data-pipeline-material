# imf_fetcher.py

import logging
import os
import pandas as pd
import requests
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
IMF_DATASETS = [
    "WEO"  # World Economic Outlook database (other datasets like IFS exist)
]
BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc/"
COUNTRIES = ["US", "CN", "AU", "CA", "CL", "ZA"]  # United States, China, Australia, Canada, Chile, South Africa
INDICATORS = {
    "NGDP_RPCH": "Real GDP Growth (Annual % Change)",
    "PCPIPCH": "Consumer Prices Inflation (Annual % Change)"
}

def fetch_imf_series(dataset_id: str, indicator_code: str, country: str) -> pd.DataFrame:
    """
    Fetch a single IMF series.

    Args:
        dataset_id (str): IMF dataset code, e.g., "WEO".
        indicator_code (str): Economic indicator code.
        country (str): Country ISO code.

    Returns:
        pd.DataFrame: DataFrame with time series for the country/indicator.
    """
    # Build request URL
    url = f"{BASE_URL}CompactData/{dataset_id}/{country}.{indicator_code}.?startPeriod=2015"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    json_data = response.json()

    try:
        observations = json_data['CompactData']['DataSet']['Series']['Obs']
    except KeyError:
        logging.warning(f"No data found for {country} - {indicator_code}")
        return pd.DataFrame()

    records = []
    for obs in observations:
        record = {
            "timestamp": obs['@TIME_PERIOD'],
            "source": "IMF",
            "text_or_indicator": f"{INDICATORS[indicator_code]}: {obs['@OBS_VALUE']}",
            "sentiment": None,
            "additional_metadata": {
                "country": country,
                "indicator_code": indicator_code,
                "indicator_name": INDICATORS[indicator_code],
                "value": obs['@OBS_VALUE']
            }
        }
        records.append(record)

    return pd.DataFrame(records)

def fetch_imf_data() -> pd.DataFrame:
    """
    Fetch macroeconomic indicators from IMF REST API.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from IMF Data Services...")
    all_records = []

    for dataset_id in IMF_DATASETS:
        for country in COUNTRIES:
            for indicator_code in INDICATORS.keys():
                try:
                    logging.info(f"Fetching IMF data: {dataset_id} - {country} - {indicator_code}")
                    df = fetch_imf_series(dataset_id, indicator_code, country)
                    if not df.empty:
                        all_records.append(df)
                except Exception as e:
                    logging.error(f"Failed to fetch IMF data for {country} {indicator_code}: {e}")

    if all_records:
        final_df = pd.concat(all_records, ignore_index=True)
        logging.info(f"Successfully fetched {len(final_df)} IMF records.")
        return final_df
    else:
        logging.warning("No IMF data fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_imf_data()
    print(df.head())
