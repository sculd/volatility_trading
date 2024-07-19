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
    price = df_market_open_from_intraday.loc[as_of_date].c
    
    calls["distance_from_price"] = abs(round(((calls["strike_price"] - price) / price)*100, 2))

    atm_call = calls.nsmallest(1, "distance_from_price")
    call_quotes = pd.json_normalize(requests.get(f"https://api.polygon.io/v3/quotes/{atm_call['ticker'].iloc[0]}?timestamp.gte={quote_timestamp}&timestamp.lt={close_timestamp}&order=desc&limit=100&sort=timestamp&apiKey={polygon_api_key}").json()["results"])
    call_quotes = call_quotes.set_index("sip_timestamp")
    call_quotes.index = pd.to_datetime(call_quotes.index, unit = "ns", utc = True).tz_convert("America/New_York")
    call_quotes["mid_price"] = round((call_quotes["bid_price"] + call_quotes["ask_price"]) / 2, 2)    
    
    time_to_expiration = atm_call.days_to_exp.values[0] / 252
    atm_call_vol = call_implied_vol(S=price, K=atm_call["strike_price"].iloc[0], t=time_to_expiration, r=.045, option_price=call_quotes["mid_price"].iloc[0])
    
    return atm_call_vol

def get_atm_put_volatility(ticker, as_of_date):
    quote_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 15, minutes = 55)).value
    close_timestamp = (pd.to_datetime(as_of_date).tz_localize("America/New_York") + timedelta(hours = 16, minutes = 0)).value    
    
    puts = pd.json_normalize(requests.get(f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&contract_type=put&as_of={as_of_date}&limit=1000&apiKey={polygon_api_key}").json()["results"])
    puts["days_to_exp"] = (pd.to_datetime(puts["expiration_date"]) - pd.to_datetime(as_of_date)).dt.days
    nearest_exp_date = puts["expiration_date"].iloc[0]
    puts = puts[puts["expiration_date"] == nearest_exp_date].copy()

    df_intraday = data.polygon.polygon_result_to_dataframe(data.polygon.get_polygon_result_dict(
        data.polygon.get_polygon_intraday_query_url(ticker, as_of_date)))    
    df_market_open_from_intraday = data.daily.get_df_market_open_from_intraday(df_intraday)
    price = df_market_open_from_intraday.loc[as_of_date].c
    
    puts["distance_from_price"] = abs(round(((price - puts["strike_price"]) / puts["strike_price"])*100, 2))
    
    atm_put = puts.nsmallest(1, "distance_from_price")

    put_quotes = pd.json_normalize(requests.get(f"https://api.polygon.io/v3/quotes/{atm_put['ticker'].iloc[0]}?timestamp.gte={quote_timestamp}&timestamp.lt={close_timestamp}&order=desc&limit=100&sort=timestamp&apiKey={polygon_api_key}").json()["results"]).set_index("sip_timestamp")
    put_quotes.index = pd.to_datetime(put_quotes.index, unit = "ns", utc = True).tz_convert("America/New_York")
    put_quotes["mid_price"] = round((put_quotes["bid_price"] + put_quotes["ask_price"]) / 2, 2)    
    
    time_to_expiration = atm_put.days_to_exp.values[0] / 252
    atm_put_vol = put_implied_vol(S=price, K=atm_put["strike_price"].iloc[0], t=time_to_expiration, r=.045, option_price=put_quotes["mid_price"].iloc[0])    
    
    return atm_put_vol

def get_df_atm_vol_history(ticker, dates):
    atm_call_vols = []
    atm_put_vols = []
    valid_dates = []
    for date in dates[:]:
        logging.info(f"{date=}")
        try:
            atm_call_vol = get_atm_call_volatility(ticker, date)
        except Exception as ex:
            print(ex)
            continue
            
        try:
            atm_put_vol = get_atm_put_volatility(ticker, date)
        except Exception as ex:
            print(ex)
            continue

        atm_call_vols.append(atm_call_vol)
        atm_put_vols.append(atm_put_vol)
        valid_dates.append(date)
    df = pd.DataFrame({"atm_call_vol": atm_call_vols, "atm_put_vol": atm_put_vols, "date": valid_dates}).set_index("date")
    return df


def load_df_atm_vol_history(ticker):
    df_name = f"df_{ticker}_atm_vol_history"
    return pd.read_pickle(f"market_data/{df_name}.pkl")

