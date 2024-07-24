import pandas as pd
import data.polygon

def get_df_market_open_from_intraday(df_intraday):
    df_market_open = df_intraday[df_intraday.index.time >= pd.Timestamp("09:35").time()].head(1)[["c"]]
    df_market_open.index = df_market_open.index.strftime("%Y-%m-%d")     
    return df_market_open

def get_df_market_close_from_intraday(df_intraday):
    df_market_close = df_intraday.tail(1)[["c"]]
    df_market_close.index = df_market_close.index.strftime("%Y-%m-%d")
    return df_market_close

def get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, open_or_close):
    df_market_dailys = []
    for date in sorted(list(set([t for t in df_intraday_history.index.date if t is not pd.NaT]))):
        df_intraday = df_intraday_history[
            (df_intraday_history.index.date == date)
        ]
        if open_or_close == "open":
            df_market_daily = get_df_market_open_from_intraday(df_intraday)
        else:
            df_market_daily = get_df_market_close_from_intraday(df_intraday)
        df_market_dailys.append(df_market_daily)
    return pd.concat(df_market_dailys)


def get_df_market_open_close_history_from_intraday_history(df_intraday_history):
    df_market_open_history = get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "open")
    df_market_close_history = get_df_market_open_or_close_history_from_intraday_history(df_intraday_history, "close")
    df_market_open_close_history = df_market_open_history.join(df_market_close_history, lsuffix="_open", rsuffix="_close")
    df_market_open_close_history["actual_change"] = df_market_open_close_history.c_close - df_market_open_close_history.c_open
    df_market_open_close_history["actual_return"] = (df_market_open_close_history.c_close - df_market_open_close_history.c_open) / df_market_open_close_history.c_open

    return df_market_open_close_history

def load_df_daily_history(ticker):
    df_name = f"df_{ticker}_daily_history"
    return pd.read_pickle(f"market_data/{df_name}.pkl")

def load_df_market_open_close_history(ticker):
    df_name = f"df_{ticker}_market_open_close_history"
    df = pd.read_pickle(f"market_data/{df_name}.pkl")
    df['c_open_nextday'] = df.shift(-1)[['c_open']]
    df['return_nextday_open'] = (df.c_open_nextday - df.c_close) / df.c_close
    return df

