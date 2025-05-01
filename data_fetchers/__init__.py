# fetchers/__init__.py

from .newsapi_fetcher import fetch_newsapi_articles
from .gdelt_fetcher import fetch_gdelt_events
from .eventregistry_fetcher import fetch_eventregistry_articles
from .webscraper_fetcher import fetch_webscraped_articles
from .worldbank_fetcher import fetch_worldbank_data
from .imf_fetcher import fetch_imf_data
from .oecd_fetcher import fetch_oecd_data
from .fred_fetcher import fetch_fred_data
from .yahoo_finance_fetcher import fetch_yfinance_data
from .quandl_fetcher import fetch_quandl_data
from .twitter_fetcher import fetch_twitter_data

__all__ = [
    "fetch_newsapi_articles",
    "fetch_gdelt_events",
    "fetch_eventregistry_articles",
    "fetch_webscraped_articles",
    "fetch_worldbank_data",
    "fetch_imf_data",
    "fetch_oecd_data",
    "fetch_fred_data",
    "fetch_yfinance_data",
    "fetch_quandl_data",
    "fetch_twitter_data",
]
