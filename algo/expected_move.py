import pandas as pd
import numpy as np


def get_df_daily_expectation(df_market_open_history, volatility_values, expected_move_multiplyer):
    df_algo = df_market_open_history.copy()
    df_algo["expected_move"] = round(volatility_values / np.sqrt(252) * expected_move_multiplyer, 4)
    df_algo["lower_price"] = round(df_algo['c_open'] * (1.0 - df_algo['expected_move']), 2)
    df_algo["upper_price"] = round(df_algo['c_open'] * (1.0 + df_algo['expected_move']), 2)
    return df_algo


def get_df_daily_expected_move_and_actual(df_market_open_close_history, df_atm_vol_history, expected_move_multiplyer):
    df_goog_daily_expected_move = get_df_daily_expectation(
        df_market_open_close_history,
        (df_atm_vol_history.atm_call_vol_market_open + df_atm_vol_history.atm_put_vol_market_open) / 2,
        expected_move_multiplyer)

    if 'actual_change' not in df_goog_daily_expected_move.columns:
        df_goog_daily_expected_move = df_goog_daily_expected_move.join(df_market_open_close_history["actual_change"])
        df_goog_daily_expected_move["expected_change_size"] = (df_goog_daily_expected_move.upper_price - df_goog_daily_expected_move.lower_price) / 2.

    return df_goog_daily_expected_move
