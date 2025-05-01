# worldbank_fetcher.py

import logging
import pandas as pd
import wbdata
import datetime
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
# World Bank Indicator Codes
INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP Growth (annual %)",
    "NV.IND.MANF.ZS": "Manufacturing, value added (% of GDP)"
}
COUNTRIES = ["USA", "CHN", "AUS", "CAN", "CHL", "ZAF"]  # Examples: US, China, Australia, Canada, Chile, South Africa
START_DATE = datetime.datetime(2015, 1, 1)
END_DATE = datetime.datetime.today()

def fetch_worldbank_data() -> pd.DataFrame:
    """
    Fetch macroeconomic indicators from World Bank Data API.

    Returns:
        pd.DataFrame: Standardized DataFrame with columns:
                      ['timestamp', 'source', 'text_or_indicator', 'sentiment', 'additional_metadata']
    """
    logging.info("Starting fetch from World Bank...")
    
    try:
        data = wbdata.get_dataframe(
            indicators=INDICATORS,
            country=COUNTRIES,
            data_date=(START_DATE, END_DATE),
            convert_date=True
        )
        data.reset_index(inplace=True)

        records = []
        for _, row in data.iterrows():
            for indicator_code, indicator_name in INDICATORS.items():
                if pd.notnull(row.get(indicator_name)):
                    record = {
                        "timestamp": row["date"],
                        "source": "World Bank",
                        "text_or_indicator": f"{indicator_name}: {row[indicator_name]}",
                        "sentiment": None,
                        "additional_metadata": {
                            "country": row["country"],
                            "indicator_code": indicator_code,
                            "indicator_name": indicator_name,
                            "value": row[indicator_name]
                        }
                    }
                    records.append(record)

        df = pd.DataFrame(records)

        if df.empty:
            logging.warning("No World Bank data fetched.")
        else:
            logging.info(f"Successfully fetched {len(df)} World Bank records.")

        return df

    except Exception as e:
        logging.error(f"Error fetching World Bank data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # For quick testing
    df = fetch_worldbank_data()
    print(df.head())
