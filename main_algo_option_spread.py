import os, logging, sys

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



def get_df_daily_expectation_actual(df_daily_history, df_intraday_history, df_atm_vol_history, expected_move_multiplyer):
    df_regime = df_daily_history[["c"]].copy()
    df_regime["1_mo_avg"] = df_regime["c"].rolling(window=20).mean()
    df_regime["3_mo_avg"] = df_regime["c"].rolling(window=60).mean()
    df_regime['regime'] = (df_regime.c.shift() > df_regime['1_mo_avg']).astype(int) * 2 - 1

    df_market_open_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "open")
    df_market_close_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "close")
    df_market_open_close_history = df_market_open_history.join(df_market_open_history, lsuffix="_open", rsuffix="_close")
    df_market_open_close_history["actual_change"] = df_market_close_history.c_close - df_market_close_history.c_open

    df_goog_daily_expectation = algo.expected_move.get_df_daily_expectation(
        df_market_open_history,
        (df_atm_vol_history.atm_call_vol_market_open + df_atm_vol_history.atm_put_vol_market_open) / 2,
        expected_move_multiplyer)

    df_daily_expectation_actual = df_goog_daily_expectation.join(df_market_open_close_history["actual_change"])
    df_daily_expectation_actual['regime'] = df_regime.regime
    df_daily_expectation_actual["expected_change_size"] = (df_daily_expectation_actual.upper_price - df_daily_expectation_actual.lower_price) / 2.

    return df_daily_expectation_actual


import pandas as pd

df_spy_daily_history = pd.read_pickle(f'market_data/df_{util.tickers.ticker_spy}_daily_history.pkl')
df_spx_daily_history = pd.read_pickle(f'market_data/df_{util.tickers.ticker_spx}_daily_history.pkl')


df_regime = df_spy_daily_history[["c"]].copy()
df_regime["1_mo_avg"] = df_regime["c"].rolling(window=20).mean()
df_regime["3_mo_avg"] = df_regime["c"].rolling(window=60).mean()
df_regime['regime'] = (df_regime.c.shift() > df_regime['1_mo_avg']).astype(int) * 2 - 1

df_spx_market_open_close_history = data.daily.load_df_market_open_close_history(util.tickers.ticker_ispx)
df_vix1d_market_open_close_history = data.daily.load_df_market_open_close_history(util.tickers.ticker_vix1d)

df_spx_daily_expectation = algo.expected_move.get_df_daily_expectation(
    df_spx_market_open_close_history[["c_open"]],
    df_vix1d_market_open_close_history.c_open / 100, 1.0)

df_spx_call_options_history = pd.read_pickle(f'market_data/df_{util.tickers.ticker_spx}_call_options_history.pkl')
df_spx_put_options_history = pd.read_pickle(f'market_data/df_{util.tickers.ticker_spx}_put_options_history.pkl')

#'''
print('call option')
df_spx_otm_call_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(
    df_spx_daily_expectation, df_spx_call_options_history,
    "call", trading_dates, tolerance_days=5
)

df_spx_otm_call_options_spread_history.to_pickle(f'market_data/df_{util.tickers.ticker_spx}_otm_call_options_spread_history.pkl')
#'''

print('put option')
df_spx_otm_put_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(
    df_spx_daily_expectation, df_spx_put_options_history,
    "put", trading_dates, tolerance_days=5
)

df_spx_otm_put_options_spread_history.to_pickle(f'market_data/df_{util.tickers.ticker_spx}_otm_put_options_spread_history.pkl')

print('done')
