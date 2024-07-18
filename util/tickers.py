import os, logging, sys

'''
Top 10 stocks by market cap
1	AAPL	Apple Inc	3,509.67B	228.88	-2.53%	381.62B
2	MSFT	Microsoft Corporation	3,296.38B	443.52	-1.33%	236.58B
3	NVDA	NVIDIA Corporation	2,902.55B	117.99	-6.62%	79.77B
4	GOOGL	Alphabet Inc.	2,246.09B	181.02	-1.58%	318.15B
5	AMZN	Amazon.com, Inc.	1,955.71B	187.93	-2.64%	590.74B
6	META	Meta Platforms, Inc.	1,171.85B	461.99	-5.68%	142.71B
7	BRK.B	Berkshire Hathaway Inc.	961.54B	445.61	1.53%	368.96B
8	LLY	Eli Lilly and Company	860.68B	905.59	-3.82%	35.93B
9	TSM	Taiwan Semiconductor Manufacturing Company Limited	838.04B	171.20	-7.98%	70.20B
10	TSLA	Tesla, Inc.	792.52B	248.50	-3.14%	94.75B
'''

ticker_spy = "SPY"
ticker_spx = "I:SPX"

ticker_aapl = "AAPL"
ticker_msft = "MSFT"
ticker_nvda = "NVDA"
ticker_goog = "GOOG"
ticker_amzn = "AMZN"
ticker_meta = "META"
ticker_tsm = "TSM"
ticker_tsla = "TSLA"
ticker_sbux = "SBUX"

ticker_vix1d = "I:VIX1D"
options_ticker = "SPX"

def get_stock_tickers():
    return [ticker_aapl, ticker_msft, ticker_nvda, ticker_goog, ticker_amzn, ticker_meta, ticker_tsm, ticker_tsla, ticker_sbux]




