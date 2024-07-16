from pandas_market_calendars import get_calendar

import data.polygon
import data.intraday
import data.daily
import data.option_contracts

import algo.option_spread
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


# daily

'''
def get_cache_df_daily_history(ticker, df_name, date_from_str = "2020-01-01", date_to_str = "2024-07-02"):
    df_daily_history = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
        data.polygon.get_polygon_range_query_url(ticker, date_from_str, date_to_str)))
    df_daily_history.index = df_daily_history.index.strftime("%Y-%m-%d")
    df_daily_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_daily_history

df_spy_daily_history = get_cache_df_daily_history(ticker_spy, "df_spy_daily_history")
df_spx_daily_history = get_cache_df_daily_history(ticker_spx, "df_spx_daily_history")
df_goog_daily_history = get_cache_df_daily_history(ticker_goog, "df_goog_daily_history")
df_sbux_daily_history = get_cache_df_daily_history(ticker_sbux, "df_sbux_daily_history")


# intraday

def get_cache_df_intraday_history(ticker, df_name):
    df_intraday_history = data.intraday.get_df_intrady_history(ticker)
    if "index" in df_intraday_history.columns:
        df_intraday_history = df_intraday_history.drop(columns=["index"])
    df_intraday_history.to_pickle(f'market_data/{df_name}.pkl')
    return df_intraday_history

df_spy_intraday_history = get_cache_df_intraday_history(ticker_spy, "df_spy_intraday_history")
df_vix1d_intraday_history = get_cache_df_intraday_history(ticker_vix1d, "df_vix1d_intraday_history")
df_spx_intraday_history = get_cache_df_intraday_history(ticker_spx, "df_spx_intraday_history")
df_goog_intraday_history = get_cache_df_intraday_history(ticker_goog, "df_goog_intraday_history")
df_sbux_intraday_history = get_cache_df_intraday_history(ticker_sbux, "df_sbux_intraday_history")


# options contracts

df_spx_call_options_history = data.option_contracts.get_df_options_history("SPX", "call", trading_dates)
df_spx_call_options_history.to_pickle('market_data/df_spx_call_options_history.pkl')

df_spx_put_options_history = data.option_contracts.get_df_options_history("SPX", "put", trading_dates)
df_spx_put_options_history.to_pickle('market_data/df_spx_put_options_history.pkl')
'''

# normally, company options have weekly exp options.
df_goog_call_options_history = data.option_contracts.get_df_options_history("GOOG", "call", trading_dates, zero_day_expiration=False)
df_goog_call_options_history.to_pickle('market_data/df_goog_call_options_history.pkl')




