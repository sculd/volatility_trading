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

11	AVGO	Broadcom Inc.	747.20B	160.52	2.91%	42.62B
12	JPM	JPMorgan Chase & Co.	602.99B	209.98	-3.18%	161.69B
13	NVO	Novo Nordisk A/S	596.94B	129.99	-4.01%	35.35B
14	WMT	Walmart Inc.	569.64B	70.82	-0.30%	657.33B
15	V	Visa Inc.	538.57B	269.15	-1.30%	34.14B
16	XOM	Exxon Mobil Corporation	532.93B	118.80	0.99%	341.10B
17	UNH	UnitedHealth Group Incorporated	519.41B	564.34	-1.56%	379.49B
18	MA	Mastercard Incorporated	413.93B	448.72	-0.54%	25.70B
19	PG	The Procter & Gamble Company	397.54B	168.44	-0.59%	84.06B
20	ORCL	Oracle Corporation	380.39B	138.03	-0.88%	52.96B

21	ASML	ASML Holding N.V.	378.09B	924.15	-0.85%	27.36B
22	JNJ	Johnson & Johnson	374.05B	155.42	-0.74%	81.80B
23	COST	Costco Wholesale Corporation	372.12B	839.37	-0.82%	253.70B
24	HD	The Home Depot, Inc.	363.01B	366.08	-1.56%	151.83B
25	BAC	Bank of America Corporation	336.35B	43.01	-2.21%	98.14B
26	MRK	Merck & Co., Inc.	314.70B	124.25	-1.30%	61.40B
27	ABBV	AbbVie Inc.	302.21B	171.14	-2.36%	54.40B
28	CVX	Chevron Corporation	298.51B	161.97	0.46%	198.87B
29	KO	The Coca-Cola Company	280.84B	65.19	-0.03%	46.07B
30	TM	Toyota Motor Corporation	280.50B	199.85	-2.22%	297.86B

31	NFLX	Netflix, Inc.	277.09B	643.04	-0.68%	34.93B
32	AMD	Advanced Micro Devices, Inc.	251.77B	155.77	-2.30%	22.80B
33	ADBE	Adobe Inc.	246.91B	556.85	-1.11%	20.43B
34	AZN	AstraZeneca PLC	242.03B	78.06	-2.13%	47.61B
35	CRM	Salesforce, Inc.	239.68B	247.35	-1.54%	35.74B
36	SHEL	Shell plc	235.01B	73.25	-0.04%	323.18B
37	PEP	PepsiCo, Inc.	234.02B	170.37	0.28%	92.05B
38	SAP	SAP SE	230.21B	197.23	-1.39%	34.66B
39	NVS	Novartis AG	222.05B	107.22	-4.10%	48.86B
40	LIN	Linde plc	214.42B	446.04	-0.72%	32.76B
41	QCOM	QUALCOMM Incorporated	213.67B	191.46	-0.07%	36.41B
'''

ticker_spy = "SPY"
ticker_spx = "I:SPX"
# top 8 (10 less 2)
ticker_aapl = "AAPL"
ticker_msft = "MSFT"
ticker_nvda = "NVDA"
ticker_goog = "GOOG"
ticker_amzn = "AMZN"
ticker_meta = "META"
ticker_tsm = "TSM"
ticker_tsla = "TSLA"
# sbux
ticker_sbux = "SBUX"
# top 20
ticker_avgo = "AVGO"
ticker_jpm = "JPM"
ticker_nvo = "NVO"
ticker_wmt = "WMT"
ticker_v = "V"
ticker_xom = "XOM"
ticker_unh = "UNH"
ticker_ma = "MA"
ticker_pg = "PG"
ticker_orcl = "ORCL"
# top 30
ticker_asml = "ASML"
ticker_jnj = "JNJ"
ticker_cost = "COST"
ticker_hd = "HD"
ticker_bac = "BAC"
ticker_mrk = "MRK"
ticker_abbv = "ABBV"
ticker_cvs = "CVX"
ticker_ko = "KO"
ticker_tm = "TM"


ticker_vix1d = "I:VIX1D"
options_ticker = "SPX"

def get_stock_tickers():
    top8 = [ticker_aapl, ticker_msft, ticker_nvda, ticker_goog, ticker_amzn, ticker_meta, ticker_tsm, ticker_tsla]
    sbux = [ticker_sbux]
    top20 = [ticker_avgo, ticker_jpm, ticker_nvo, ticker_wmt, ticker_v, ticker_xom, ticker_unh, ticker_ma, ticker_pg, ticker_orcl]
    top30 = [ticker_asml, ticker_jnj, ticker_cost, ticker_hd, ticker_bac, ticker_mrk, ticker_abbv, ticker_cvs, ticker_ko, ticker_tm]

    return top8 + sbux + top20 + top30




