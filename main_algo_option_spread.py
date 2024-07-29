import os, logging, sys

import pandas as pd
import util.tickers

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

import algo.expected_move
import algo.volatility

ticker_spy = "SPY"
ticker_spx = "I:SPX"
ticker_goog = "GOOG"
ticker_sbux = "SBUX"
ticker_vix1d = "I:VIX1D"
options_ticker = "SPX"


from pandas_market_calendars import get_calendar

calendar = get_calendar("NYSE")
trading_dates = calendar.schedule(
    start_date = "2023-05-01", 
    end_date = "2024-07-02"
    #end_date = (datetime.today()-timedelta(days = 1))
).index.strftime("%Y-%m-%d").values



def get_df_daily_expected_move_and_actual(df_market_open_close_history, df_atm_vol_history, expected_move_multiplyer):
    df_goog_daily_expected_move = algo.expected_move.get_df_daily_expectation(
        df_market_open_close_history,
        (df_atm_vol_history.atm_call_vol_market_open + df_atm_vol_history.atm_put_vol_market_open) / 2,
        expected_move_multiplyer)

    if 'actual_change' not in df_goog_daily_expected_move.columns:
        df_goog_daily_expected_move = df_goog_daily_expected_move.join(df_market_open_close_history["actual_change"])
        df_goog_daily_expected_move["expected_change_size"] = (df_goog_daily_expected_move.upper_price - df_goog_daily_expected_move.lower_price) / 2.

    return df_goog_daily_expected_move


def cache_get_otm_options_spread_history_with_given_expected_move(ticker, trading_dates, df_daily_expected_move):
    df_otm_call_options_spread_history = None
    #'''
    print(f'{ticker} call option')
    df_call_options_history = data.option_contracts.load_df_options_history(ticker, 'call')
    df_otm_call_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(
        df_daily_expected_move, df_call_options_history,
        "call", trading_dates, tolerance_days=5
    )

    if df_otm_call_options_spread_history is not None:
        df_otm_call_options_spread_history.to_pickle(
            f'market_data/df_{ticker}_otm_call_options_spread_history.pkl')
    #'''

    df_otm_put_options_spread_history = None
    #'''
    print('put option')
    df_put_options_history = data.option_contracts.load_df_options_history(ticker, 'put')
    df_otm_put_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(
        df_daily_expected_move, df_put_options_history,
        "put", trading_dates, tolerance_days=5
    )

    if df_otm_put_options_spread_history is not None:
        df_otm_put_options_spread_history.to_pickle(
            f'market_data/df_{ticker}_otm_put_options_spread_history.pkl')

    #'''

    print('done')

    return df_otm_call_options_spread_history, df_otm_put_options_spread_history

def cache_get_otm_options_spread_history(ticker, trading_dates, expected_move_multiplyer):
    df_atm_vol_history = algo.volatility.load_df_atm_vol_history(ticker)
    df_market_open_close_history = data.daily.load_df_market_open_close_history(ticker)
    df_daily_expected_move_and_actual = get_df_daily_expected_move_and_actual(df_market_open_close_history, df_atm_vol_history, expected_move_multiplyer)

    return cache_get_otm_options_spread_history_with_given_expected_move(ticker, trading_dates, df_daily_expected_move_and_actual)


df_spx_market_open_close_history = data.daily.load_df_market_open_close_history(util.tickers.ticker_ispx)
df_vix1d_market_open_close_history = data.daily.load_df_market_open_close_history(util.tickers.ticker_vix1d)


df_spx_daily_expected_move = algo.expected_move.get_df_daily_expectation(
    df_spx_market_open_close_history[["c_open"]],
    df_vix1d_market_open_close_history.c_open / 100, 1.0)


#df_spx_otm_call_options_spread_history, df_spx_otm_put_options_spread_history = cache_get_otm_options_spread_history_with_given_expected_move(
#    util.tickers.ticker_spx, trading_dates, df_spx_daily_expected_move)

'''
for ticker in util.tickers.get_stock_tickers():
    print(f'{ticker=}')
    cache_get_otm_options_spread_history(
        ticker, trading_dates, expected_move_multiplyer=1.0,
    )
'''

cache_get_otm_options_spread_history(
    util.tickers.ticker_goog, trading_dates, expected_move_multiplyer=2.0,
)
