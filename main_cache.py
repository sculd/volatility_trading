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
import data.polygon
import data.intraday
import data.daily
import data.option_contracts

import algo.option_spread
import algo.volatility

import util.tickers


ticker_spy = "SPY"
ticker_spx = "I:SPX"

ticker_vix1d = "I:VIX1D"
options_ticker = "SPX"


from pandas_market_calendars import get_calendar

calendar = get_calendar("NYSE")
trading_dates = calendar.schedule(
    start_date = "2023-05-01", 
    end_date = "2024-07-02"
    #end_date = (datetime.today()-timedelta(days = 1))
).index.strftime("%Y-%m-%d").values



def get_cache_df_daily_history(ticker, df_name, date_from_str = "2020-01-01", date_to_str = "2024-07-02"):
    df_daily_history = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
        data.polygon.get_polygon_range_query_url(ticker, date_from_str, date_to_str)))
    df_daily_history.index = df_daily_history.index.strftime("%Y-%m-%d")
    df_daily_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_daily_history

def get_cache_df_intraday_history(ticker, df_name):
    df_intraday_history = data.intraday.get_df_intrady_history(ticker, trading_dates)
    if "index" in df_intraday_history.columns:
        df_intraday_history = df_intraday_history.drop(columns=["index"])
    df_intraday_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_intraday_history

def get_cache_options_history(ticker, option_type, df_name):
    df_options_history = data.option_contracts.get_df_options_history(ticker, option_type, trading_dates)
    df_options_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_options_history


def cache_ticker(ticker):
    print(f"{ticker=}")
    df_daily_history = get_cache_df_daily_history(ticker, f"df_{ticker}_daily_history")
    print(f"df_daily_history:\n{df_daily_history}")

    df_intraday_history = get_cache_df_intraday_history(ticker, f"df_{ticker}_intraday_history")
    print(f"df_intraday_history:\n{df_intraday_history}")

    df_call_options_history = get_cache_options_history(ticker, "call", f"df_{ticker}_call_options_history")
    print(f"df_call_options_history:\n{df_call_options_history}")

    df_put_options_history = get_cache_options_history(ticker, "put", f"df_{ticker}_put_options_history")
    print(f"df_put_options_history:\n{df_put_options_history}")


'''
cache_ticker(ticker_spy)
cache_ticker(ticker_spx)
# note: vix only needs intraday
cache_ticker(ticker_vix1d)
cache_ticker(util.tickers.ticker_goog)
cache_ticker(util.tickers.ticker_sbux)
'''

cache_ticker(util.tickers.ticker_aapl)
cache_ticker(util.tickers.ticker_msft)
cache_ticker(util.tickers.ticker_nvda)
cache_ticker(util.tickers.ticker_amzn)
cache_ticker(util.tickers.ticker_meta)
cache_ticker(util.tickers.ticker_tsm)
cache_ticker(util.tickers.ticker_tsla)




