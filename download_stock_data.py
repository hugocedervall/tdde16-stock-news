import pyEX
import os
import datetime
import logging

# Constants
SANDBOX = False
UPDATE_FILES = False  # Get ticker if already downloaded?
DATA_FOLDER = "news_data_test/" if SANDBOX else "news_data/"
PRICE_FOLDER = "alpha_vantage_processed_data/"
TICKER_FILE = "nyse_tickers.txt"
LOG_FOLDER = "logs/"

# IEX cloud settings
api_token = "Tsk_bb7989a0d56a400ebcdcfcd1827c7f8e" if SANDBOX else "sk_d3676fd812c84568b062d0176ad61667"
version = "sandbox" if SANDBOX else "v1"

# Setup logging
logging_file = f"{LOG_FOLDER}{datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%s')}.log"
logging.basicConfig(filename=logging_file,
                    level=logging.DEBUG)

# Client to fetch data
client = pyEX.Client(version=version, api_token=api_token)


def get_tickers():
    """
    Returns: list of all company tickers that we have price data for
    """
    return sorted(os.listdir(PRICE_FOLDER))


def download_news():
    """
    Downloads and stores news for all tickers
    """
    tickers = get_tickers()[:200]

    # Vill ha related==ticker, source=valdsource, lang=en
    news_filter = "datetime,headline,summary,related,lang,source"

    counter = 0
    for ticker in tickers:
        counter += 1

        if not UPDATE_FILES:
            if ticker in os.listdir(DATA_FOLDER):
                continue
        try:
            news_df = client.newsDF(symbol=ticker, count=-1, filter=news_filter)
        except Exception as e:
            logging.warning(f"could not download news for {ticker} : {e}")
            continue
        if news_df.empty:
            logging.warning(f"Empty news data for {ticker}")
            continue

        # Add timezone to index and convert to EST
        news_df.index = news_df.index.tz_localize('GMT').tz_convert('EST')

        news_df.to_csv(DATA_FOLDER + ticker)
        logging.info(f" Stock {counter}/{len(tickers)}: Downloaded {len(news_df.index)} news for {ticker}")
        print(f" Stock {counter}/{len(tickers)}: Downloaded {len(news_df.index)} news for {ticker}")


if __name__ == "__main__":
    download_news()

"""
TODO: update stock prices with timezone 
df["datetime"] = df["datetime"].dt.tz_localize("EST")
"""
