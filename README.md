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

