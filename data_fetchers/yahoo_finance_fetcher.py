# yahoo_finance_fetcher.py

import logging
import pandas as pd
import yfinance as yf
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
TICKERS = {
    "LIT": "Global Lithium & Battery Tech ETF (proxy for Lithium)",
    "JJCTF": "Cobalt 27 Capital Corp (proxy for Cobalt)",
    "NICL": "Nickel Industries Limited (proxy for Nickel)",
    "MMC.L": "Mining Minerals & Metals plc (proxy for Manganese)"
}
START_DATE = "2015-01-01"

def fetch_yfinance_data() -> pd.DataFrame:
    """
    Fetch commodity-related data from Yahoo Finance using yfinance.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from Yahoo Finance...")
    all_records = []

    for ticker, description in TICKERS.items():
        try:
            logging.info(f"Fetching Yahoo Finance data for {ticker} ({description})...")
            data = yf.download(ticker, start=START_DATE)
            if data.empty:
                logging.warning(f"No data returned for {ticker}.")
                continue

            for timestamp, row in data.iterrows():
                if pd.isna(row["Close"]):
                    continue
                record = {
                    "timestamp": timestamp,
                    "source": "Yahoo Finance",
                    "text_or_indicator": f"{description} Closing Price: {row['Close']}",
                    "sentiment": None,
                    "additional_metadata": {
                        "ticker": ticker,
                        "description": description,
                        "close_price": row["Close"]
                    }
                }
                all_records.append(record)

        except Exception as e:
            logging.error(f"Error fetching Yahoo Finance data for {ticker}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        logging.info(f"Successfully fetched {len(df)} Yahoo Finance records.")
        return df
    else:
        logging.warning("No Yahoo Finance data fetched.")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_yfinance_data()
    print(df.head())
