import data.daily, data.intraday
import algo.volatility


def _get_df_high_call_vol_actual_change(df_market_open_close_history, df_atm_vol_history, high_vol_threshold = 0.3, low_vol_threshold = 0.3):
    df_large_atm_call_vol_history = df_atm_vol_history[
        (df_atm_vol_history.atm_call_vol_market_open > high_vol_threshold) &
        (df_atm_vol_history.atm_put_vol_market_open < low_vol_threshold)
    ]
    df_large_atm_call_vol_atm_actual_change = df_large_atm_call_vol_history[['atm_call_vol_market_open', 'atm_put_vol_market_open', 'atm_call_vol_market_close', 'atm_put_vol_market_close']].\
        join(df_market_open_close_history[['actual_change', 'actual_return', 'return_nextday_open']])
    return df_large_atm_call_vol_atm_actual_change

def _get_df_high_put_vol_actual_change(df_market_open_close_history, df_atm_vol_history, high_vol_threshold = 0.3, low_vol_threshold = 0.3):
    df_large_atm_put_vol_history = df_atm_vol_history[
        (df_atm_vol_history.atm_put_vol_market_open > high_vol_threshold) &
        (df_atm_vol_history.atm_call_vol_market_open < low_vol_threshold)
    ]
    df_large_atm_put_vol_atm_actual_change = df_large_atm_put_vol_history[['atm_call_vol_market_open', 'atm_put_vol_market_open', 'atm_call_vol_market_close', 'atm_put_vol_market_close']].\
        join(df_market_open_close_history[['actual_change', 'actual_return', 'return_nextday_open']])
    return df_large_atm_put_vol_atm_actual_change


def get_df_high_call_vol_actual_change(ticker, high_vol_threshold = 0.3, low_vol_threshold = 0.3):
    df_market_open_close_history = data.daily.load_df_market_open_close_history(ticker)
    df_atm_vol_history = algo.volatility.load_df_atm_vol_history(ticker)
    df_high_call_vol_actual_change = _get_df_high_call_vol_actual_change(
        df_market_open_close_history, df_atm_vol_history, high_vol_threshold=high_vol_threshold, low_vol_threshold=low_vol_threshold)
    df_high_call_vol_actual_change['ticker'] = ticker
    return df_high_call_vol_actual_change


def get_df_high_put_vol_actual_change(ticker, high_vol_threshold = 0.3, low_vol_threshold = 0.3):
    df_market_open_close_history = data.daily.load_df_market_open_close_history(ticker)
    df_atm_vol_history = algo.volatility.load_df_atm_vol_history(ticker)
    df_high_put_vol_actual_change = _get_df_high_put_vol_actual_change(
        df_market_open_close_history, df_atm_vol_history, high_vol_threshold=high_vol_threshold, low_vol_threshold=low_vol_threshold)
    df_high_put_vol_actual_change['ticker'] = ticker
    return df_high_put_vol_actual_change

