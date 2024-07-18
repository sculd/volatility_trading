import pandas as pd
import numpy as np


def get_df_daily_expectation(df_market_open_history, regime_values, volatility_values, expected_move_multiplyer):
    df_algo = df_market_open_history.add_suffix("_market_open").copy()
    df_algo['regime'] = regime_values
    df_algo["expected_move"] = round(volatility_values / np.sqrt(252) * expected_move_multiplyer, 4)
    df_algo["lower_price"] = round(df_algo['c_market_open'] * (1.0 - df_algo['expected_move']), 2)
    df_algo["upper_price"] = round(df_algo['c_market_open'] * (1.0 + df_algo['expected_move']), 2)
    return df_algo



