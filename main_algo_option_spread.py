import pandas as pd

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
df_spx_daily_expectation = algo.expected_move.get_df_daily_expectation(df_spx_market_open_history)

df_spx_otm_call_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(df_spx_daily_expectation, df_spx_call_options_history, "call", trading_dates)
df_spx_otm_call_options_spread_history.to_pickle('market_data/df_spx_otm_call_options_spread_history.pkl')

df_spx_otm_put_options_spread_history = algo.option_spread.get_df_otm_options_spread_history(df_spx_daily_expectation, df_spx_put_options_history, "put", trading_dates)
df_spx_otm_put_options_spread_history.to_pickle('market_data/df_spx_otm_put_options_spread_history.pkl')


# volatility
df_goog_atm_vol_history = algo.volatility.get_df_atm_vol_history("GOOG", trading_dates)
df_goog_atm_vol_history.to_pickle('market_data/df_goog_atm_vol_history.pkl')

df_sbux_atm_vol_history = algo.volatility.get_df_atm_vol_history("SBUX", trading_dates)
df_sbux_atm_vol_history.to_pickle('market_data/df_sbux_atm_vol_history.pkl')
'''




def get_cache_df_atm_vol_history(ticker, dates, df_name):
    df_atm_vol_history = algo.volatility.get_df_atm_vol_history(ticker, dates)
    df_atm_vol_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_atm_vol_history

df_goog_atm_vol_history = get_cache_df_atm_vol_history("GOOG", trading_dates, "df_goog_atm_vol_history")

def get_df_daily_expectation_actual(df_daily_history, df_intraday_history, df_atm_vol_history, expected_move_multiplyer):
    df_regime = df_daily_history[["c"]].copy()
    df_regime["1_mo_avg"] = df_regime["c"].rolling(window=20).mean()
    df_regime["3_mo_avg"] = df_regime["c"].rolling(window=60).mean()
    df_regime['regime'] = df_regime.apply(lambda row: 1 if (row['c'] > row['1_mo_avg']) else -1, axis=1)

    df_market_open_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "open")
    df_market_close_history = data.daily.get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "close")
    df_market_open_close_history = df_market_open_history.join(df_market_open_history, lsuffix="_open", rsuffix="_close")
    df_market_open_close_history["actual_change"] = df_market_close_history.c_close - df_market_close_history.c_open

    df_goog_daily_expectation = algo.expected_move.get_df_daily_expectation(
        df_market_open_history, df_regime.regime,
        (df_atm_vol_history.atm_call_vol + df_atm_vol_history.atm_put_vol) / 2,
        expected_move_multiplyer)

    df_daily_expectation_actual = df_goog_daily_expectation.join(df_market_open_close_history["actual_change"])
    df_daily_expectation_actual["expected_change_size"] = (df_daily_expectation_actual.upper_price - df_daily_expectation_actual.lower_price) / 2.

    return df_daily_expectation_actual


df_goog_daily_expectation_actual = get_df_daily_expectation_actual(df_goog_daily_history, df_goog_intraday_history, df_goog_atm_vol_history, 1.0)


