import pandas as pd
import data.intraday
import numpy as np
import scipy.optimize as optimize
import math, os, logging
import requests

import data.polygon
import data.daily

from scipy.stats import norm
from datetime import datetime, timedelta

polygon_api_key = os.getenv("QUANT_GALORE_POLYGON_API_KEY")

def black_scholes(option_type, S, K, t, r, q, sigma):
    """
    Calculate the Black-Scholes option price.

    :param option_type: 'call' for call option, 'put' for put option.
    :param S: Current stock price.
    :param K: Strike price.
    :param t: Time to expiration (in years).
    :param r: Risk-free interest rate (annualized).
    :param q: Dividend yield (annualized).
    :param sigma: Stock price volatility (annualized).

    :return: Option price.
    """
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)

    if option_type == 'call':
        return S * math.exp(-q * t) * norm.cdf(d1) - K * math.exp(-r * t) * norm.cdf(d2)
    elif option_type == 'put':
        return K * math.exp(-r * t) * norm.cdf(-d2) - S * math.exp(-q * t) * norm.cdf(-d1)
    else:
        raise ValueError("Option type must be either 'call' or 'put'.")
        
def call_implied_vol(S, K, t, r, option_price):
    q = 0.01
    option_type = "call"

    def f_call(sigma):
        return black_scholes(option_type, S, K, t, r, q, sigma) - option_price

    call_newton_vol = optimize.newton(f_call, x0=0.50, tol=0.05, maxiter=100)
    return call_newton_vol

def put_implied_vol(S, K, t, r, option_price):
    q = 0.01
    option_type = "put"

    def f_put(sigma):
        return black_scholes(option_type, S, K, t, r, q, sigma) - option_price

    put_newton_vol = optimize.newton(f_put, x0=0.50, tol=0.05, maxiter=100)
    return put_newton_vol

def get_atm_call_volatility(ticker, as_of_date):
    market_2_minutes_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 32)).value
    market_5_minutes_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 35)).value
    quote_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 15, minutes = 55)).value
    close_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 16, minutes = 0)).value
    
    calls = pd.json_normalize(requests.get(f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&contract_type=call&as_of={as_of_date}&limit=1000&apiKey={polygon_api_key}").json()["results"])
    calls["days_to_exp"] = (pd.to_datetime(calls["expiration_date"]) - pd.to_datetime(as_of_date)).dt.days
    #calls = calls[calls["days_to_exp"] >= 5].copy()
    nearest_exp_date = calls["expiration_date"].iloc[0]
    calls = calls[calls["expiration_date"] == nearest_exp_date].copy()
    
    df_intraday = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
        data.polygon.get_polygon_intraday_query_url(ticker, as_of_date)))    

    df_market_open_from_intraday = data.daily.get_df_market_open_from_intraday(df_intraday)
    price_market_open = df_market_open_from_intraday.loc[as_of_date].c
    calls["distance_from_price_market_open"] = abs(round(((calls["strike_price"] - price_market_open) / price_market_open)*100, 2))
    atm_call_market_open = calls.nsmallest(1, "distance_from_price_market_open")
    time_to_expiration_market_open = atm_call_market_open.days_to_exp.values[0] / 252

    quotes_market_open = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_quotes_url(atm_call_market_open['ticker'].iloc[0], market_2_minutes_timestamp, market_5_minutes_timestamp))
    quotes_market_open = quotes_market_open.set_index("sip_timestamp")
    quotes_market_open.index = pd.to_datetime(quotes_market_open.index, unit="ns", utc=True).tz_convert("America/New_York")
    quotes_market_open["mid_price"] = round((quotes_market_open["bid_price"] + quotes_market_open["ask_price"]) / 2, 2)

    df_market_close_from_intraday = data.daily.get_df_market_close_from_intraday(df_intraday)
    price_market_close = df_market_close_from_intraday.loc[as_of_date].c
    calls["distance_from_price_market_close"] = abs(round(((calls["strike_price"] - price_market_close) / price_market_close) * 100, 2))
    atm_call_market_close = calls.nsmallest(1, "distance_from_price_market_close")
    time_to_expiration_market_close = atm_call_market_open.days_to_exp.values[0] / 252

    quotes_market_close = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_quotes_url(atm_call_market_close['ticker'].iloc[0], quote_timestamp, close_timestamp))
    quotes_market_close = quotes_market_close.set_index("sip_timestamp")
    quotes_market_close.index = pd.to_datetime(quotes_market_close.index, unit="ns", utc=True).tz_convert("America/New_York")
    quotes_market_close["mid_price"] = round((quotes_market_close["bid_price"] + quotes_market_close["ask_price"]) / 2, 2)

    atm_call_vol_market_open = call_implied_vol(S=price_market_open, K=atm_call_market_open["strike_price"].iloc[0], t=time_to_expiration_market_open, r=.045, option_price=quotes_market_open["mid_price"].iloc[0])
    atm_call_vol_market_close = call_implied_vol(S=price_market_close, K=atm_call_market_close["strike_price"].iloc[0], t=time_to_expiration_market_close, r=.045, option_price=quotes_market_close["mid_price"].iloc[0])

    return atm_call_vol_market_open, atm_call_vol_market_close

def get_atm_put_volatility(ticker, as_of_date):
    market_2_minutes_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 32)).value
    market_5_minutes_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 9, minutes = 35)).value
    quote_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 15, minutes = 55)).value
    close_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 16, minutes = 0)).value    
    
    puts = pd.json_normalize(requests.get(f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&contract_type=put&as_of={as_of_date}&limit=1000&apiKey={polygon_api_key}").json()["results"])
    puts["days_to_exp"] = (pd.to_datetime(puts["expiration_date"]) - pd.to_datetime(as_of_date)).dt.days
    nearest_exp_date = puts["expiration_date"].iloc[0]
    puts = puts[puts["expiration_date"] == nearest_exp_date].copy()

    df_intraday = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
        data.polygon.get_polygon_intraday_query_url(ticker, as_of_date)))

    df_market_open_from_intraday = data.daily.get_df_market_open_from_intraday(df_intraday)
    price_market_open = df_market_open_from_intraday.loc[as_of_date].c
    puts["distance_from_price_market_open"] = abs(round(((price_market_open - puts["strike_price"]) / puts["strike_price"])*100, 2))
    atm_put_market_open = puts.nsmallest(1, "distance_from_price_market_open")
    time_to_expiration_market_open = atm_put_market_open.days_to_exp.values[0] / 252

    quotes_market_open = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_quotes_url(atm_put_market_open['ticker'].iloc[0], market_2_minutes_timestamp, market_5_minutes_timestamp))
    quotes_market_open = quotes_market_open.set_index("sip_timestamp")
    quotes_market_open.index = pd.to_datetime(quotes_market_open.index, unit="ns", utc=True).tz_convert("America/New_York")
    quotes_market_open["mid_price"] = round((quotes_market_open["bid_price"] + quotes_market_open["ask_price"]) / 2, 2)

    df_market_close_from_intraday = data.daily.get_df_market_close_from_intraday(df_intraday)
    price_market_close = df_market_close_from_intraday.loc[as_of_date].c
    puts["distance_from_price_market_close"] = abs(round(((price_market_close - puts["strike_price"]) / puts["strike_price"]) * 100, 2))
    atm_put_market_close = puts.nsmallest(1, "distance_from_price_market_close")
    time_to_expiration_market_close = atm_put_market_close.days_to_exp.values[0] / 252

    quotes_market_close = data.polygon.polygon_url_to_dataframe(data.polygon.get_polygon_quotes_url(atm_put_market_close['ticker'].iloc[0], quote_timestamp, close_timestamp))
    quotes_market_close = quotes_market_close.set_index("sip_timestamp")
    quotes_market_close.index = pd.to_datetime(quotes_market_close.index, unit="ns", utc=True).tz_convert("America/New_York")
    quotes_market_close["mid_price"] = round((quotes_market_close["bid_price"] + quotes_market_close["ask_price"]) / 2, 2)

    atm_put_vol_market_open = put_implied_vol(S=price_market_open, K=atm_put_market_open["strike_price"].iloc[0], t=time_to_expiration_market_open, r=.045, option_price=quotes_market_open["mid_price"].iloc[0])
    atm_put_vol_market_close = put_implied_vol(S=price_market_close, K=atm_put_market_close["strike_price"].iloc[0], t=time_to_expiration_market_close, r=.045, option_price=quotes_market_close["mid_price"].iloc[0])

    return atm_put_vol_market_open, atm_put_vol_market_close

def get_df_atm_vol_history(ticker, dates):
    atm_call_vol_market_opens = []
    atm_call_vol_market_closes = []
    atm_put_vol_market_opens = []
    atm_put_vol_market_closes = []
    valid_dates = []
    for date in dates[:]:
        logging.info(f"{date=}")
        try:
            atm_call_vol_market_open, atm_call_vol_market_close = get_atm_call_volatility(ticker, date)
        except Exception as ex:
            print(ex)
            continue
            
        try:
            atm_put_vol_market_open, atm_put_vol_market_close = get_atm_put_volatility(ticker, date)
        except Exception as ex:
            print(ex)
            continue

        atm_call_vol_market_opens.append(atm_call_vol_market_open)
        atm_call_vol_market_closes.append(atm_call_vol_market_close)
        atm_put_vol_market_opens.append(atm_put_vol_market_open)
        atm_put_vol_market_closes.append(atm_put_vol_market_close)
        valid_dates.append(date)
    df = pd.DataFrame({
        "atm_call_vol_market_open": atm_call_vol_market_opens,
        "atm_call_vol_market_close": atm_call_vol_market_closes,
        "atm_put_vol_market_open": atm_put_vol_market_opens,
        "atm_put_vol_market_close": atm_put_vol_market_closes,
        "date": valid_dates,
    }).set_index("date")
    return df


def load_df_atm_vol_history(ticker):
    df_name = f"df_{ticker}_atm_vol_history"
    return pd.read_pickle(f"market_data/{df_name}.pkl")

