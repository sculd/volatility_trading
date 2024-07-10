import pandas as pd
import data.polygon

def get_df_options_history(ticker, side, dates):
    dfs = []
    for date in dates[1:]:
        df = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_options_contracts_query_url(
            ticker, side, date, date))
        df['date'] = date
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df