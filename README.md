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

