#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Gets stock quotes from Yahoo and Google Finance, and historical prices from Yahoo Finance.

Examples:

>>> import stockquote, os

>>> h = list(stockquote.historical("GOOG", "20010101", "20101231"))
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
import pprint
import urllib2

CODES_YAHOO = {
    "l1": "price_last",
    "c1": "change",
    "v": "volume",
    "a2": "avg_daily_volume",
    "x": "stock_exchange",
    "j1": "market_cap",
    "b4": "book_value",
    "j4": "ebitda",
    "d": "dividend_per_share",
    "y": "dividend_yield",
    "e": "earnings_per_share",
    "k": "52_week_high",
    "j": "52_week_low",
    "m3": "50day_moving_avg",
    "m4": "200day_moving_avg",
    "r": "price_earnings_ratio",
    "r5": "price_earnings_growth_ratio",
    "p5": "price_sales_ratio",
    "p6": "price_book_ratio",
    "s7": "short_ratio",
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



def from_google(symbol):
    url = 'http://finance.google.com/finance/info?q=%s' % symbol
    lines = urllib2.urlopen(url).read().splitlines()
    raw_dict = json.loads(''.join([x.decode("utf-8").strip() for x in lines
                                   if x not in ('// [', ']')]))
    normalized_dict = dict([(CODES_GOOGLE.get(key, "UNKNOWN_KEY_%s" % key),
                             value)
                            for key, value in raw_dict.iteritems()])
    return normalized_dict


def from_yahoo(symbol):
    stats = "l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7" # Yahoo craziness
    url = 'http://download.finance.yahoo.com/quotes.csv?s=%s&f=%s' % (symbol, stats)
    #"http://download.finance.yahoo.com/d/quotes.csv?s=%sфsl1d1t1c1ohgvе" % symbol
    raw_dict = urllib.urlopen(url).read().strip().strip('"')
    normalized_dict = dict([(CODES_YAHOO.get(key, "UNKNOWN_KEY_%s" % key),
                             value)
                            for key, value in raw_dict.iteritems()])
    return normalized_dict


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
    return csv_reader



