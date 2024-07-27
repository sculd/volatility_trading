from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import data.polygon
import data.daily


def concat_otm_short_long(df_otm_short, df_otm_long, o_or_c_or_m, option_type):
    df_otm_options = pd.concat([
        df_otm_short.add_suffix(f"_market_{o_or_c_or_m}_s_{option_type}"),
        df_otm_long.add_suffix(f"_market_{o_or_c_or_m}_l_{option_type}")], axis = 1)
    short_price_column = "bid_price" if o_or_c_or_m == "o" else "ask_price"
    long_price_column = "ask_price" if o_or_c_or_m == "o" else "bid_price"
    df_otm_options[f"market_{o_or_c_or_m}_spread"] = df_otm_options[f"{short_price_column}_market_{o_or_c_or_m}_s_{option_type}"] - \
        df_otm_options[f"{long_price_column}_market_{o_or_c_or_m}_l_{option_type}"]
    return df_otm_options


def get_df_otm_options_spread(date_str, df_otm_options_history, option_type, tolerance_days=0):
    # df_otm_options_daily = df_otm_options_history[df_otm_options_history.expiration_date == date_str]
    expiration_date_max = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=tolerance_days)).strftime("%Y-%m-%d")
    df_otm_options_daily = df_otm_options_history[
        (df_otm_options_history.expiration_date <= expiration_date_max) &
        (df_otm_options_history.date == date_str)
    ]    

    if df_otm_options_daily.empty:
        return None

    if option_type == "call":
        otm_short_ticker = df_otm_options_daily.head(1).ticker.values[0]
        otm_long_ticker = df_otm_options_daily.head(2).tail(1).ticker.values[0]
    else:
        otm_short_ticker = df_otm_options_daily.tail(1).ticker.values[0]
        otm_long_ticker = df_otm_options_daily.tail(2).head(1).ticker.values[0]

    '''
    df_otm_short_option_intraday = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_intraday_query_url(otm_short_ticker, date_str))
    df_otm_long_option_intraday = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_intraday_query_url(otm_long_ticker, date_str))
    if df_otm_short_option_intraday.empty or df_otm_long_option_intraday.empty:
        return None
    
    df_otm_short_option_market_open = data.daily.get_df_market_open_from_intraday(df_otm_short_option_intraday)
    df_otm_short_option_market_open['ticker'] = otm_short_ticker
    df_otm_long_option_market_open = data.daily.get_df_market_open_from_intraday(df_otm_long_option_intraday)
    df_otm_long_option_market_open['ticker'] = otm_long_ticker
    df_otm_options_market_open = concat_otm_short_long(
        df_otm_short_option_market_open, df_otm_long_option_market_open,
        "o", option_type
    )

    df_otm_short_option_market_close = data.daily.get_df_market_close_from_intraday(df_otm_short_option_intraday)
    df_otm_long_option_market_close = data.daily.get_df_market_close_from_intraday(df_otm_long_option_intraday)
    df_otm_options_market_close = concat_otm_short_long(
        df_otm_short_option_market_close, df_otm_long_option_market_close,
        "c", option_type
    )
    #'''

    def get_df_spread_at_timestamp(ticker_short, ticker_long, o_or_c_or_m, epoch_nano_head, epoch_nano_tail):
        df_otm_short_open_quote = data.polygon.polygon_url_to_dataframe(
            data.polygon.get_polygon_quotes_url(ticker_short, epoch_nano_head, epoch_nano_tail)).head(1)
        df_otm_long_open_quote = data.polygon.polygon_url_to_dataframe(
            data.polygon.get_polygon_quotes_url(ticker_long, epoch_nano_head, epoch_nano_tail)).head(1)
        if df_otm_short_open_quote.empty or df_otm_long_open_quote.empty:
            return None
        df_otm_short_open_quote['date'] = date_str
        df_otm_long_open_quote['date'] = date_str
        df_otm_short_open_quote = df_otm_short_open_quote.set_index('date')
        df_otm_long_open_quote = df_otm_long_open_quote.set_index('date')
        df_otm_spread = concat_otm_short_long(
            df_otm_short_open_quote, df_otm_long_open_quote,
            o_or_c_or_m, option_type
        )
        return df_otm_spread

    market_early_minutes_timestamp_head = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 35)).value
    market_early_minutes_timestamp_tail = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 37)).value
    df_otm_options_market_open = get_df_spread_at_timestamp(otm_short_ticker, otm_long_ticker, "o", market_early_minutes_timestamp_head, market_early_minutes_timestamp_tail)
    if df_otm_options_market_open is None:
        return None

    market_midday_timestamp_head = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 13, minutes = 0)).value
    market_midday_timestamp_tail = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 13, minutes = 5)).value
    df_otm_options_midday = get_df_spread_at_timestamp(otm_short_ticker, otm_long_ticker, "m", market_midday_timestamp_head, market_midday_timestamp_tail)
    if df_otm_options_midday is None:
        return None

    quote_timestamp = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 15, minutes = 55)).value
    close_timestamp = (pd.to_datetime(date_str).tz_localize("America/New_York") + timedelta(hours = 16, minutes = 0)).value
    df_otm_options_market_close = get_df_spread_at_timestamp(otm_short_ticker, otm_long_ticker, "c", quote_timestamp, close_timestamp)
    if df_otm_options_market_close is None:
        return None

    # df_otm_options is of length 1
    df_otm_options = df_otm_options_market_open.join(df_otm_options_market_close).join(df_otm_options_midday)
    df_otm_options["pnl_midday"] = df_otm_options["market_o_spread"] - df_otm_options["market_m_spread"]
    df_otm_options["pnl_market_close"] = df_otm_options["market_o_spread"] - df_otm_options["market_c_spread"]
    df_otm_options["pnl"] = df_otm_options["pnl_market_close"]
    #df_otm_options["pnl"] = np.where(df_otm_options.pnl_midday < 0, df_otm_options.pnl_midday, df_otm_options.pnl_market_close)
    min_pnl = df_otm_options["market_o_spread"] - 5
    df_otm_options["pnl"] = np.where(df_otm_options.pnl < min_pnl, min_pnl, df_otm_options.pnl)

    return df_otm_options


def get_df_otm_options_spread_history(df_daily_expectation, df_options_history, option_type, dates, tolerance_days=0):
    df_otm_options_history = df_options_history.join(df_daily_expectation, on='date')
    if option_type == "call":
        df_otm_options_history = df_otm_options_history[
            df_otm_options_history.strike_price > df_otm_options_history.upper_price
        ]
    else:
        df_otm_options_history = df_otm_options_history[
            df_otm_options_history.strike_price < df_otm_options_history.lower_price
        ]
    
    dfs = []
    for date in dates[:]:
        print(f'{date=}')
        df_date = get_df_otm_options_spread(date, df_otm_options_history, option_type, tolerance_days=tolerance_days)
        if df_date is None:
            continue
        dfs.append(df_date)
    df = pd.concat(dfs, ignore_index=False)
    return df

