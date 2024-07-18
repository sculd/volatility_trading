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


def cache_ticker(ticker):
    df_daily_history = get_cache_df_daily_history(ticker, f"df_{ticker}_daily_history")
    df_intraday_history = get_cache_df_intraday_history(ticker, f"df_{ticker}_intraday_history")
    df_call_options_history = get_cache_options_history(ticker, "call", f"df_{ticker}_call_options_history")
    df_put_options_history = get_cache_options_history(ticker, "put", f"df_{ticker}_put_options_history")


cache_ticker(ticker_spy)
cache_ticker(ticker_spx)
# note: vix only needs intraday
cache_ticker(ticker_vix1d)
cache_ticker(ticker_goog)
cache_ticker(ticker_sbux)

