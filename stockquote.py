#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Gets stock quotes from Yahoo and Google Finance, and historical prices from Yahoo Finance.

Examples:

>>> import stockquote, os

>>> h = list(stockquote.historical_quotes("GOOG", "20010101", "20101231"))
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
         GOOGLE_CODE_ccol: chr
           GOOGLE_CODE_id: 694653
        GOOGLE_CODE_l_cur: 701.96
            GOOGLE_CODE_s: 0
                   change: -0.74
                 exchange: NASDAQ
              price_close: -0.10
               price_last: 701.96
      price_last_datetime: Dec 14, 4:00PM EST
          price_last_time: 4:00PM EST
               source_url: http://www.google.com/finance/info?q=GOOG
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
import dateutil.parser
import json
import optparse
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

# from http://fixprotocol.org/specifications/exchanges.shtml
REUTERS_EXCHANGE_CODES = {
    "CI": "Abidjan Stock Exchange",
    "E": "AEX Options and Futures Exchange",
    "AS": "AEX Stock Exchange",
    "AL": "Alpha Trading Systems",
    "A": "American Stock Exchange",
    "AM": "Amman Stock Exchange",
    "AX": "Australian Stock Exchange",
    "BH": "Bahrain Stock Exchange",
    "MC": "Barcelona Stock Exchange - CATS Feed",
    "BC": "Barcelona Stock Exchange - Floor Trading",
    "BY": "Beirut Stock Exchange",
    "b": "Belfox",
    "BE": "Berlin Stock Exchange",
    "BN": "Berne Stock Exchange",
    "BI": "Bilbao Stock Exchange",
    "BBK": "BlockBook ATS",
    "BO": "Bombay Stock Exchange",
    "B": "Boston Stock Exchange",
    "BT": "Botswana Share Market",
    "BM": "Bremen Stock Exchange",
    "BR": "Brussels Stock Exchange",
    "C2OX": "C2 Options Exchange ",
    "CA": "Cairo and Alexandria Stock Exchange",
    "CL": "Calcutta Stock Exchange",
    "V": "Canadian Ventures Exchange",
    "CH": "Channel Islands",
    "W": "Chicago Board Options Exchange",
    "MW": "Chicago Stock Exchange",
    "CEX": "Chi-East",
    "CE": "Chile Electronic Exchange",
    "CHA": "Chi-X Australia",
    "INS": "CHI-X Exchange",
    "C": "Cincinnati Stock Exchange",
    "CM": "Colombo Stock Exchange",
    "CO": "Copenhagen Stock Exchange",
    "DL": "Dehli Stock Exchange",
    "QA": "Doha Securities Market",
    "DU": "Dubai Financial Market",
    "DI": "Dubai International Financial Exchange",
    "D": "Dusseldorf Stock Exchange",
    "EB": "Electronic Stock Exchange  of Venezuela",
    "F": "Frankfurt Stock Exchange",
    "FU": "Fukuoka Stock Exchange",
    "GH": "Ghana Stock Exchange",
    "H": "Hamburg Stock Exchange",
    "HA": "Hanover Stock Exchange",
    "HE": "Helsinki Stock Exchange",
    "HK": "Hong Kong Stock Exchange",
    "IC": "Iceland Stock Exchange",
    "IN": "Interbolsa (Portugal)",
    "Y": "International Securities Exchange (ISE)",
    "I": "Irish Stock Exchange",
    "IS": "Istanbul Stock Exchange",
    "JK": "Jakarta Stock Exchange",
    "Q": "Japanese Securities Dealers Association (JASDAQ)",
    "J": "Johannesburg Stock Exchange",
    "KAB": "Kabu.com PTS",
    "KA": "Karachi Stock Exchange",
    "KZ": "Kazakhstan Stock Exchange",
    "KFE": "Korean Futures Exchange",
    "KS": "Korea Stock Exchange",
    "KQ": "KOSDAQ (Korea)",
    "KL": "Kuala Lumpur Stock Exchange",
    "KW": "Kuwait Stock Exchange",
    "KY": "Kyoto Stock Exchange",
    "LG": "Lagos Stock Exchange",
    "LA": "Latin American Market in Spain (LATIBEX)",
    "LN": "Le Nouveau Marche",
    "LM": "Lima Stock Exchange",
    "LS": "Lisbon Stock Exchange (Portugal)",
    "L": "London Stock Exchange",
    "LZ": "Lusaka Stock Exchange",
    "LU": "Luxembourg Stock Exchange",
    "MD": "Madras Stock Exchange",
    "MA": "Madrid Stock Exchange - Floor Trading",
    "MT": "Malta Stock Exchange",
    "MZ": "Mauritius Stock Exchange",
    "ML": "Medellin Stock Excahnge",
    "MX": "Mexican Stock Exchange",
    "MI": "Milan Stock Exchange",
    "p": "MONEP Paris Stock Options",
    "M": "Montreal Exchange",
    "MM": "Moscow Inter Bank Currency Exchange",
    "MO": "Moscow Stock Exchange",
    "MU": "Munich Stock Exchange",
    "OM": "Muscat Stock Exchange",
    "NG": "Nagoya Stock Exchange",
    "NR": "Nairobi Stock Exchange",
    "NM": "Namibia Stock Exchange",
    "OQ": "NASDAQ",
    "OB": "NASDAQ Dealers - Bulletin Board",
    "OJ": "NASDAQ Japan",
    "NS": "National Stock Exchange of India",
    "NW": "NewEx (Austria)",
    "N": "New York Stock Exchange",
    "NZ": "New Zealand Stock Exchange",
    "MP": "NYSE MatchPoint",
    "OD": "Occidente Stock Exchange",
    "OS": "Osaka Stock Exchange",
    "OL": "Oslo Stock Exchange",
    "P": "Pacific Stock Exchange",
    "PA": "Paris Stock Exchange",
    "PH": "Philadelphia Stock Exchange",
    "X": "Philadelphia Stock Exchange Options",
    "PS": "Phillipine Stock Exchange",
    "PNK": "Pink Sheets (National Quotation Bureau)",
    "PR": "Prague Stock Exchange",
    "PT": "Pure Trading",
    "RQ": "RASDAQ (Romania)",
    "RI": "Riga Stock Exchange",
    "SO": "Rio de Janeiro OTC Stock Exchange (SOMA)",
    "RTS": "Russian Trading System",
    "SN": "Santiago Stock Exchange",
    "SA": "Sao Paulo Stock Exchange",
    "SP": "Sapporo Stock Exchange",
    "SE": "Saudi Stock Exchange",
    "JNX": "SBI Japannext",
    "SBI": "SBI Stock Exchange (Sweden)",
    "SS": "Shanghai Stock Exchange",
    "SZ": "Shenzhen Stock Exchange",
    "SIM": "Singapore Exchange - Derivatives",
    "SI": "Singapore Stock Exchange",
    "ST": "Stockholm Stock Exchange",
    "PE": "St. Petersburg Stock Exchange",
    "SG": "Stuttgart Stock Exchange",
    "SU": "Surabaya Stock Exchange",
    "QMH": "SWX Quotematch AG",
    "S": "SWX Swiss Exchange",
    "SFE": "Sydney Futures Exchange",
    "TWO": "Taiwan OTC Securities Exchange",
    "TW": "Taiwan Stock Exchange",
    "TL": "Tallinn Stock Exchange",
    "TA": "Tel Aviv Stock Exchange",
    "BK": "Thailand Stock Exchange",
    "TH": "Third Market",
    "TCE": "Tokyo Commodity Exchange",
    "TFF": "Tokyo Financial Futures Exchange",
    "T": "Tokyo Stock Exchange",
    "K": "Toronto Options Exchange",
    "TO": "Toronto Stock Exchange",
    "TP": "Tradepoint Stock Exchange",
    "TN": "Tunis Stock Exchange",
    "TQ": "Turquoise",
    "UBS": "UBS MTF",
    "PFT": "Ukraine PFTS",
    "VA": "Valencia Stock Exchange",
    "VI": "Vienna Stock Exchange",
    "VL": "Vilnus Stock Exchange",
    "VX": "virt-x",
    "DE": "Xetra",
    "ZA": "Zagreb Stock Exchange",
    "ZI": "Zimbabwe Stock Exchange",

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

    normalized_dict = dict([(CODES_GOOGLE.get(key, "GOOGLE_CODE_%s" % key),
                             value)
                            for key, value in raw_dict.iteritems()])
    normalized_dict["source_url"] = url
    normalized_dict["source"] = "Google"
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
    first_result = dict([(CODES_YAHOO.get(k, "YAHOO_CODE_%s" % k), v)
                         for k, v in first_result_all.iteritems()
                         if v is not None])
    first_result["source_url"] = url
    first_result["source"] = "Yahoo!"
    return first_result


def historical_quotes(symbol, start_date, end_date):
    """
    Get historical quotes for the given ticker symbol.

    Date format is 'YYYYMMDD', or anything understood by
    dateutil.parser.parse, or a datetime instance.

    Returns a nested list.
    """
    if isinstance(start_date, str):
        start_date = dateutil.parser.parse(start_date)
    if isinstance(end_date, str):
        end_date = dateutil.parser.parse(end_date)

    url = ("http://ichart.yahoo.com/table.csv?"
           "s=%s&"

           "d=%s&"
           "e=%s&"
           "f=%s&"

           "a=%s&"
           "b=%s&"
           "c=%s&"

           "g=d&"
           "ignore=.csv"
           % (symbol,
              end_date.month - 1,
              end_date.day,
              end_date.year,
              start_date.month - 1,
              start_date.day,
              start_date.year,
              ))

    lines = urllib2.urlopen(url).readlines()
    csv_reader = csv.DictReader(lines[1:], fieldnames=lines[0].strip().split(","))

    prices = [dict(csv_line) for csv_line in csv_reader]

    for price_dict in prices:
        price_dict["symbol"] = symbol
        price_dict["source_url"] = url
        price_dict["source"] = "Yahoo!"

    return prices


def format_quote(quote):
    sys.stdout.write(os.linesep.join(["%28s: %s" % (k, quote[k])
                                      for k in sorted(quote.keys())]))
    sys.stdout.write("\n")


def format_quote_csv(quote, csv_writer=None, outfh=None):
    if outfh is None:
        outfh = sys.stdout
    if csv_writer is None:
        csv_writer = csv.DictWriter(outfh, quote.keys())
    csv_writer.writerow(quote)


def format_quote_json(quote, outfh=None):
    if outfh is None:
        outfh = sys.stdout
    outfh.write(json.dumps(quote))
    outfh.write("\n")


def _get_csv_writer(quotes):
    quote_fields = set()
    for q in quotes:
        quote_fields.update(set(q.keys()))
    header_fields_first = ["symbol",
                           "Date",
                           ]
    header_fields_last = ["source",
                          "source_url",
                          ]
    quote_fields = (header_fields_first
                    + list((quote_fields
                            - set(header_fields_first)
                            - set(header_fields_last)))
                    + header_fields_last)
    return csv.DictWriter(sys.stdout, fieldnames=quote_fields)


def get(symbol, start_date=None, end_date=None):
    quotes = []

    if any((start_date, end_date)):
        quotes.extend(historical_quotes(symbol,
                                        options.date_start,
                                        options.date_end))
    else:
        quotes.append(from_yahoo(symbol))
        quotes.append(from_google(symbol))

    return quotes




if __name__ == "__main__":
    import sys, os

    parser = optparse.OptionParser()
    parser.add_option("-s", "--start", dest="date_start",
                      help="start date of quotes wanted (inclusive)")
    parser.add_option("-e", "--end", dest="date_end",
                      help="end date of quotes wanted (inclusive)")
    parser.add_option("--csv", action="store_true",
                      help="write csv as output (default is formatted text)")
    parser.add_option("--json", action="store_true",
                      help="write json as output (default is formatted text)")
    parser.add_option("--format",
                      help="output format: formatted text, json, csv")
    options, symbols = parser.parse_args()

    date_options = (options.date_start, options.date_end)
    if any(date_options):
        if not all(date_options):
            sys.stderr.write("must specify both --start and --end (got: %s)\n"
                             % ("--start: %s; --to: %s" % (options.date_start,
                                                           options.date_end)))
            sys.exit(1)

        options.date_start = dateutil.parser.parse(options.date_start)
        options.date_end   = dateutil.parser.parse(options.date_end)

    want_format = options.format
    if options.csv:
        want_format = "csv"
    if options.json:
        want_format = "json"

    if want_format == "csv":
        options.csv = True
    if want_format == "json":
        options.json = True

    formatters = {
        "json": format_quote_json,
        "csv" : format_quote_csv,
        }

    quotes = []
    for symbol in symbols:
        quotes.extend(get(symbol,
                          start_date=options.date_start,
                          end_date=options.date_end))

    format_quote = formatters.get(want_format, format_quote)

    # csv output has a bit of state, so handle that here...
    if options.csv:
        csv_writer = _get_csv_writer(quotes)
        csv_writer.writeheader()
        format_quote = lambda quote: format_quote_csv(quote, csv_writer=csv_writer)

    for quote in quotes:
        format_quote(quote)

