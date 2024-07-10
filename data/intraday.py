import pandas as pd
import data.polygon

def get_df_intrady_history(ticker, dates):
    dfs = []
    for date in dates[1:]:
        df_intraday = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
            data.polygon.get_polygon_intraday_query_url(ticker, date)))
        dfs.append(df_intraday.reset_index())
    df = pd.concat(dfs, ignore_index=True).set_index("t")
    return df