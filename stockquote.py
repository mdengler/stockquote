#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Gets stock quotes from Yahoo and Google Finance, and historical prices from Yahoo Finance.

Examples:

>>> import stockquote, os

>>> h = list(stockquote.historical_prices("GOOG", "20010101", "20101231"))
>>> print os.linesep.join(["%25s: %s" % (k, h[0][k]) for k in sorted(h[0].keys())])
                Adj Close: 593.97
                    Close: 593.97
                     Date: 2010-12-31
                     High: 598.42
                      Low: 592.03
                     Open: 596.74
                   Volume: 1539300

>>> q = stockquote.from_google("GOOG")
>>> print os.linesep.join(["%25s: %s" % (k, q[k]) for k in sorted(q.keys())])
         UNKNOWN_KEY_ccol: chr
           UNKNOWN_KEY_ec: -0.07
        UNKNOWN_KEY_eccol: chr
          UNKNOWN_KEY_ecp: -0.01
       UNKNOWN_KEY_el_cur: 615.92
           UNKNOWN_KEY_id: 694653
        UNKNOWN_KEY_l_cur: 615.99
            UNKNOWN_KEY_s: 1
          UNKNOWN_KEY_yld: 
                   change: -1.79
                 dividend: 
                 exchange: NASDAQ
              price_close: -0.29
               price_last: 615.99
      price_last_datetime: Mar 14, 4:00PM EDT
      price_last_exchange: 615.92
 price_last_exchange_time: Mar 15, 4:13AM EDT
          price_last_time: 4:00PM EDT
                   symbol: GOOG


@author Martin Dengler
@author Corey Goldberg
@author Alex K (from http://coreygoldberg.blogspot.com/2011/09/python-stock-quotes-from-google-finance.html?showComment=1317261837589#c1165604274543334045 )

Copyright 2012

License: GPLv3+

TODO: There is much to do.  This is just a 15 minute hack job to
extend
http://coreygoldberg.blogspot.com/2011/09/python-stock-quotes-from-google-finance.html
without turning into http://www.goldb.org/ystockquote.html .



"""

import csv
import json
import urllib, urllib2


CODES_YAHOO = {
    "a": "Ask",
    "a2": "Average Daily Volume",
    "a5": "Ask Size b Bid",
    "b2": "Ask (Real-time)",
    "b3": "Bid (Real-time)",
    "b4": "Book Value",
    "b6": "Bid Size",
    "c": "Change & Percent Change",
    "c1": "Change",
    "c3": "Commission",
    "c6": "Change (Real-time)",
    "c8": "After Hours Change (Real-time)",
    "d": "Dividend/Share",
    "d1": "Last Trade Date",
    "d2": "Trade Date",
    "e": "Earnings/Share",
    "e1": "Error Indication (returned for symbol changed / invalid)",
    "e7": "EPS Estimate Current Year",
    "e8": "EPS Estimate Next Year",
    "e9": "EPS Estimate Next Quarter",
    "f6": "Float Shares",
    "g": "Day's Low",
    "h": "Day's High",
    "j": "52-week Low",
    "k": "52-week High",
    "g1": "Holdings Gain Percent",
    "g3": "Annualized Gain",
    "g4": "Holdings Gain",
    "g5": "Holdings Gain Percent (Real-time)",
    "g6": "Holdings Gain (Real-time)",
    "i": "More Info",
    "i5": "Order Book (Real-time)",
    "j1": "Market Capitalization",
    "j3": "Market Cap (Real-time)",
    "j4": "EBITDA",
    "j5": "Change From 52-week Low",
    "j6": "Percent Change From 52-week Low",
    "k1": "Last Trade (Real-time) With Time",
    "k2": "Change Percent (Real-time)",
    "k3": "Last Trade Size",
    "k4": "Change From 52-week High",
    "k5": "Percebt Change From 52-week High",
    "l": "Last Trade (With Time)",
    "l1": "Last Trade (Price Only)",
    "l2": "High Limit",
    "l3": "Low Limit",
    "m": "Day's Range",
    "m2": "Day's Range (Real-time)",
    "m3": "50-day Moving Average",
    "m4": "200-day Moving Average",
    "m5": "Change From 200-day Moving Average",
    "m6": "Percent Change From 200-day Moving Average",
    "m7": "Change From 50-day Moving Average",
    "m8": "Percent Change From 50-day Moving Average",
    "n": "Name",
    "n4": "Notes",
    "o": "Open",
    "p": "Previous Close",
    "p1": "Price Paid",
    "p2": "Change in Percent",
    "p5": "Price/Sales",
    "p6": "Price/Book",
    "q": "Ex-Dividend Date",
    "r": "P/E Ratio",
    "r1": "Dividend Pay Date",
    "r2": "P/E Ratio (Real-time)",
    "r5": "PEG Ratio",
    "r6": "Price/EPS Estimate Current Year",
    "r7": "Price/EPS Estimate Next Year",
    "s": "Symbol",
    "s1": "Shares Owned",
    "s7": "Short Ratio",
    "t1": "Last Trade Time",
    "t6": "Trade Links",
    "t7": "Ticker Trend",
    "t8": "1 yr Target Price",
    "v": "Volume",
    "v1": "Holdings Value",
    "v7": "Holdings Value (Real-time)",
    "w": "52-week Range",
    "w1": "Day's Value Change",
    "w4": "Day's Value Change (Real-time)",
    "x": "Stock Exchange",
    "y": "Dividend Yield",
}

CODES_GOOGLE = {
    'c': "change",
    'cp': "price_close",
    "div": "dividend",
    "e": "exchange",
    "el": "price_last_exchange",
    "elt": "price_last_exchange_time",
    "l": "price_last",
    "lt": "price_last_datetime",
    "ltt": "price_last_time",
    "t": "symbol",
    }

REUTERS_TO_GOOGLE = {
    ".N225": "INDEXNIKKEI:NI225",
}

GOOGLE_EXCHANGES = {
    "NYSE": "New York Stock Exchange",
    "NASDAQ": "The NASDAQ Stock Market, Inc. – NASDAQ Last Sale",
    "NYSEAMEX": "NYSE AMEX",
    "NYSEARCA": "NYSE ARCA",
    "OTC": "FINRA OTC Bulletin Board",
    "PINK": "FINRA OTC Bulletin Board",
    "TSE": "Toronto Stock Exchange",
    "CVE": "Toronto TSX Ventures Exchange",
    "OPRA": "Option Chains",
    "LON": "London Stock Exchange",
    "FRA": "Deutsche Börse Frankfurt Stock Exchange",
    "ETR": "Deutsche Börse XETRA",
    "BIT": "Borsa Italiana Milan Stock Exchange",
    "EPA": "NYSE Euronext Paris",
    "EBR": "NYSE Euronext Brussels",
    "ELI": "NYSE Euronext Lisbon",
    "AMS": "NYSE Euronext Amsterdam",
    "BOM": "Bombay Stock Exchange Limited",
    "NSE": "National Stock Exchange of India",
    "SHA": "Shanghai Stock Exchange",
    "SHE": "Shenzhen Stock Exchange",
    "TPE": "Taiwan Stock Exchange",
    "HKG": "Hong Kong Stock Exchange",
    "TYO": "Tokyo Stock Exchange",
    "ASX": "Australian Securities Exchange",
    "NZE": "New Zealand Stock Exchange",
}



def from_google(symbol):
    if symbol.startswith("."):
        symbol = REUTERS_TO_GOOGLE.get(symbol, symbol)
    url = 'http://www.google.com/finance/info?q=%s' % symbol
    lines = urllib2.urlopen(url).read().splitlines()
    raw_dict = json.loads(''.join([x.decode("utf-8", "replace").strip() for x in lines
                                   if x not in ('// [', ']')]))

    normalized_dict = dict([(CODES_GOOGLE.get(key, "UNKNOWN_KEY_%s" % key),
                             value)
                            for key, value in raw_dict.iteritems()])
    normalized_dict["source_url"] = url
    return normalized_dict


def from_yahoo(symbol):
    if symbol.startswith("."):
        symbol = "^" + symbol[1:]
    elif "." in symbol:
        symbol = symbol[:symbol.index(".")]
    stats = CODES_YAHOO.keys()
    url = 'http://download.finance.yahoo.com/d/quotes.csv?'
    fields = {"s": symbol, "f": "".join(stats), "e": ".csv"}
    url += urllib.urlencode(fields)
    csv_string = urllib.urlopen(url).read().strip()
    lines = [csv_string]
    csv_reader = csv.DictReader(lines, fieldnames=stats)
    csv_results = list(csv_reader)
    first_result_all = csv_results[0]
    first_result = dict([(CODES_YAHOO.get(k, "UNKNOWN_KEY_%s" % k), v)
                         for k, v in first_result_all.iteritems()
                         if v is not None])
    first_result["source_url"] = url
    return first_result


def historical_prices(symbol, start_date, end_date):
    """
    Get historical prices for the given ticker symbol.
    Date format is 'YYYYMMDD'

    Returns a nested list.
    """
    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % str(int(end_date[4:6]) - 1) + \
          'e=%s&' % str(int(end_date[6:8])) + \
          'f=%s&' % str(int(end_date[0:4])) + \
          'g=d&' + \
          'a=%s&' % str(int(start_date[4:6]) - 1) + \
          'b=%s&' % str(int(start_date[6:8])) + \
          'c=%s&' % str(int(start_date[0:4])) + \
          'ignore=.csv'
    lines = urllib2.urlopen(url).readlines()
    csv_reader = csv.DictReader(lines[1:], fieldnames=lines[0].strip().split(","))
    prices = [dict(csv_line) for csv_line in csv_reader]
    for price_dict in prices:
        price_dict["source_url"] = url
    return prices



if __name__ == "__main__":
    import sys, os
    for ticker in sys.argv[1:]:
        for quote in from_yahoo(ticker), from_google(ticker):
            sys.stderr.write("Quote from %s\n" % quote["source_url"])
            sys.stdout.write(os.linesep.join(["%28s: %s" % (k, quote[k])
                                              for k in sorted(quote.keys())
                                              if k != "source_url"]))
            sys.stdout.write("\n")

