import pandas as pd
import data.polygon
import data.daily


def concat_otm_short_long(df_otm_short, df_otm_long, o_or_c, option_type):
    df_otm_options = pd.concat([
        df_otm_short.add_suffix(f"_market_{o_or_c}_s_{option_type}"), 
        df_otm_long.add_suffix(f"_market_{o_or_c}_l_{option_type}")], axis = 1)
    df_otm_options[f"market_{o_or_c}_spread"] = df_otm_options[f"c_market_{o_or_c}_s_{option_type}"] - \
        df_otm_options[f"c_market_{o_or_c}_l_{option_type}"]
    return df_otm_options


def get_df_otm_options_spread(date_str, df_otm_options_history, option_type, tolerance_days = 0):
    # df_otm_options_daily = df_otm_options_history[df_otm_options_history.expiration_date == date_str]
    expiration_date_max = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=tolerance_days)).strftime("%Y-%m-%d")
    df_otm_options_daily = df_otm_options_history[
        (df_otm_options_history.expiration_date <= expiration_date_max) &
        (df_otm_options_history.expiration_date == date_str)
    ]    

    if df_otm_options_daily.empty:
        return None

    if option_type == "call":
        otm_short_ticker = df_otm_options_daily.head(1).ticker.values[0]
        otm_long_ticker = df_otm_options_daily.head(2).tail(1).ticker.values[0]
    else:
        otm_short_ticker = df_otm_options_daily.tail(1).ticker.values[0]
        otm_long_ticker = df_otm_options_daily.tail(2).head(1).ticker.values[0]

    df_otm_short_option_intraday = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_intraday_query_url(otm_short_ticker, date_str))
    df_otm_long_option_intraday = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_intraday_query_url(otm_long_ticker, date_str))
    if df_otm_short_option_intraday.empty or df_otm_long_option_intraday.empty:
        return None
    
    df_otm_short_option_market_open = data.daily.get_df_market_open_from_intraday(df_otm_short_option_intraday)
    df_otm_long_option_market_open = data.daily.get_df_market_open_from_intraday(df_otm_long_option_intraday)
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
    
    df_otm_options = df_otm_options_market_open.join(df_otm_options_market_close)
    df_otm_options["pnl"] = df_otm_options["market_o_spread"] - df_otm_options["market_c_spread"]

    return df_otm_options


def get_df_otm_options_spread_history(df_daily_expectation, df_options_history, option_type, dates):
    df_otm_options_history = df_options_history.join(df_daily_expectation, on='expiration_date')
    if option_type == "call":
        df_otm_options_history = df_otm_options_history[
            df_otm_options_history.strike_price > df_otm_options_history.upper_price
        ]    
    else:
        df_otm_options_history = df_otm_options_history[
            df_otm_options_history.strike_price < df_otm_options_history.lower_price
        ]
    
    dfs = []
    for date in dates[1:]:
        df_date = get_df_otm_options_spread(date, df_otm_options_history, option_type)
        if df_date is None:
            continue
        dfs.append(df_date)
    df = pd.concat(dfs, ignore_index=False)
    return df

