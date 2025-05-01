# quandl_fetcher.py

import logging
import os
import pandas as pd
import quandl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")
quandl.ApiConfig.api_key = QUANDL_API_KEY

# Example free datasets for materials (you can replace with your premium datasets if available)
DATASETS = {
    "LBMA/LBMA-GOLD": "Gold Price (proxy commodity)",
    "LME/PR_COB": "Cobalt Price",
    "LME/PR_NI": "Nickel Price",
    "LME/PR_MN": "Manganese Price"
}
START_DATE = "2015-01-01"

def fetch_quandl_data() -> pd.DataFrame:
    """
    Fetch commodity-related data from Quandl API.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from Quandl...")
    all_records = []

    for dataset_code, description in DATASETS.items():
        try:
            logging.info(f"Fetching Quandl dataset: {dataset_code} ({description})...")
            data = quandl.get(dataset_code, start_date=START_DATE)
            if data.empty:
                logging.warning(f"No data returned for {dataset_code}.")
                continue

            # Assume the first numeric column is the target
            target_column = data.select_dtypes(include=['float64', 'int64']).columns[0]

            for timestamp, row in data.iterrows():
                if pd.isna(row[target_column]):
                    continue
                record = {
                    "timestamp": timestamp,
                    "source": "Quandl",
                    "text_or_indicator": f"{description}: {row[target_column]}",
                    "sentiment": None,
                    "additional_metadata": {
                        "dataset_code": dataset_code,
                        "description": description,
                        "price": row[target_column]
                    }
                }
                all_records.append(record)

        except Exception as e:
            logging.error(f"Error fetching Quandl data for {dataset_code}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        logging.info(f"Successfully fetched {len(df)} Quandl records.")
        return df
    else:
        logging.warning("No Quandl data fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_quandl_data()
    print(df.head())
