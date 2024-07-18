import os, logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

polygon_api_key = os.getenv("QUANT_GALORE_POLYGON_API_KEY")

from pandas_market_calendars import get_calendar

import pandas as pd

import algo.volatility

import util.tickers

calendar = get_calendar("NYSE")
trading_dates = calendar.schedule(
    start_date = "2023-05-01", 
    end_date = "2024-07-02"
    #end_date = (datetime.today()-timedelta(days = 1))
).index.strftime("%Y-%m-%d").values


def get_cache_df_atm_vol_history(ticker, dates, df_name):
    logging.info(f"{ticker=}")
    df_atm_vol_history = algo.volatility.get_df_atm_vol_history(ticker, dates)
    df_atm_vol_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_atm_vol_history

for ticker in util.tickers.get_stock_tickers():
    get_cache_df_atm_vol_history(ticker, trading_dates, f"df_{ticker}_atm_vol_history")

