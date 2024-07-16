import pandas as pd
import data.polygon

def get_df_options_history(ticker, side, dates, zero_day_expiration=True):
    # zero_day_expiration True only queries the 0DTE options.
    dfs = []
    for date in dates[:]:
        exp_date = date if zero_day_expiration else None
        df = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_options_contracts_query_url(
            ticker, side, date, exp_date))
        df['date'] = date
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df