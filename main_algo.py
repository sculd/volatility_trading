from pandas_market_calendars import get_calendar

import pandas as pd

import data.polygon
import data.intraday
import data.daily
import algo.option_spread

import algo.expectation
import algo.volatility

ticker_spy = "SPY"
ticker_spx = "I:SPX"
ticker_goog = "GOOG"
ticker_sbux = "SBUX"
ticker_vix1d = "I:VIX1D"
options_ticker = "SPX"


calendar = get_calendar("NYSE")
trading_dates = calendar.schedule(
    start_date = "2023-05-01", 
    end_date = "2024-07-02"
    #end_date = (datetime.today()-timedelta(days = 1))
).index.strftime("%Y-%m-%d").values


df_spy_daily_history = pd.read_pickle('market_data/df_spy_daily_history.pkl')
df_goog_daily_history = pd.read_pickle('market_data/df_goog_daily_history.pkl')
df_sbux_daily_history = pd.read_pickle('market_data/df_sbux_daily_history.pkl')

df_spy_intraday_history = pd.read_pickle('market_data/df_spy_intraday_history.pkl')
df_vix1d_intraday_history = pd.read_pickle('market_data/df_vix1d_intraday_history.pkl')
df_spx_intraday_history = pd.read_pickle('market_data/df_spx_intraday_history.pkl')
df_goog_intraday_history = pd.read_pickle('market_data/df_goog_intraday_history.pkl')
df_sbux_intraday_history = pd.read_pickle('market_data/df_sbux_intraday_history.pkl')

df_spx_call_options_history = pd.read_pickle('market_data/df_spx_call_options_history.pkl')
df_spx_put_options_history = pd.read_pickle('market_data/df_spx_put_options_history.pkl')
df_goog_call_options_history = pd.read_pickle('market_data/df_goog_call_options_history.pkl')


df_spy_market_open_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_spy_intraday_history, "open")
df_vix1d_market_open_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_vix1d_intraday_history, "open")
df_spx_market_open_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_spx_intraday_history, "open")


# intraday optinos
df_spx_otm_call_options_spread_history = pd.read_pickle('market_data/df_spx_otm_call_options_spread_history.pkl')
df_spx_otm_put_options_spread_history = pd.read_pickle('market_data/df_spx_otm_put_options_spread_history.pkl')
df_goog_otm_call_options_spread_history = pd.read_pickle('market_data/df_goog_otm_call_options_spread_history.pkl')
df_goog_otm_put_options_spread_history = pd.read_pickle('market_data/df_goog_otm_put_options_spread_history.pkl')
df_sbux_otm_call_options_spread_history = pd.read_pickle('market_data/df_sbux_otm_call_options_spread_history.pkl')
df_sbux_otm_put_options_spread_history = pd.read_pickle('market_data/df_sbux_otm_put_options_spread_history.pkl')


# volatility
df_goog_atm_vol_history = pd.read_pickle('market_data/df_goog_atm_vol_history.pkl')
df_sbux_atm_vol_history = pd.read_pickle('market_data/df_sbux_atm_vol_history.pkl')


# intraday optinos
'''
df_spx_daily_expectation = algo.expectation.get_df_daily_expectation(df_spx_market_open_history)

df_spx_otm_call_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(df_spx_daily_expectation, df_spx_call_options_history, "call", trading_dates)
df_spx_otm_call_options_spread_history.to_pickle('market_data/df_spx_otm_call_options_spread_history.pkl')

df_spx_otm_put_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(df_spx_daily_expectation, df_spx_put_options_history, "put", trading_dates)
df_spx_otm_put_options_spread_history.to_pickle('market_data/df_spx_otm_put_options_spread_history.pkl')


# volatility
df_goog_atm_vol_history = algo.volatility.get_df_atm_vol_history("GOOG")
df_goog_atm_vol_history.to_pickle('market_data/df_goog_atm_vol_history.pkl')

df_sbux_atm_vol_history = algo.volatility.get_df_atm_vol_history("SBUX")
df_sbux_atm_vol_history.to_pickle('market_data/df_sbux_atm_vol_history.pkl')
'''

df_goog_otm_call_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(df_goog_daily_expectation, df_goog_call_options_history, "call", trading_dates, tolerance_days=5)





