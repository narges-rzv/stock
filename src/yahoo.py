#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Joschi Krause
from __future__ import print_function
from __future__ import division

import re
import os
import json
import time
import argparse
import datetime
import requests


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) " + \
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"


def get_crumb(symbol):
    r = requests.get("https://finance.yahoo.com/quote/{0}/history?p={0}".format(symbol))
    data = r.text
    if r.status_code != 200:
        raise ValueError("{0}: {1}".format(r.status_code, data))
    m = re.search('"crumb":"([a-zA-Z0-9]+)"', data)
    return m.group(1), r.cookies


def get_time(date):
#    date = "{0}-01-01".format(date)
    return int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))


def get_range(symbol, crumb, cookies, from_time, to_time):
    f = get_time(from_time)
    t = get_time(to_time)
    url = ("https://query1.finance.yahoo.com/v7/" + \
        "finance/download/{0}?period1={1}&period2={2}" + \
        "&interval=1d&events=history&crumb={3}").format(symbol, f, t, crumb)
    headers = {
        "User-Agent": USER_AGENT,
    }
    r = requests.get(url, cookies=cookies, headers=headers)
    data = r.text
    if r.status_code != 200 or data[0] == "{":
        raise ValueError("{0} {1}: {2}".format(url, r.status_code, data))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch Yahoo stock price data')
    parser.add_argument('--state', type=str, default=None, help="state file")
    parser.add_argument('--start', type=str, help="start time (inclusive Y-m-d)")
    parser.add_argument('--end', type=str, help="end time (exclusive Y-m-d)")
    parser.add_argument('symbol', type=str, help="the symbol(s)")
    args = parser.parse_args()

    crumb = None
    for sym in args.symbol.split(","):
        try:
          if crumb is None:
            if args.state is not None and os.path.exists(args.state):
                print("loading cookies from file")
                with open(args.state, "r") as f_in:
                    crumb, cookies = json.load(f_in)
                    cookies = requests.cookies.cookiejar_from_dict(cookies)
            else:
                print("getting cookies")
                crumb, cookies = get_crumb(sym)
                if args.state is not None:
                    with open(args.state, "w") as s_out:
                        cobj = requests.utils.dict_from_cookiejar(cookies)
                        json.dump([ crumb, cobj ], s_out)
          print("getting {0}".format(sym))
          data = get_range(sym, crumb.strip(), cookies, args.start, args.end)
          with open("prices/{0}.csv".format(sym), "w") as f_out:
             print(data, file=f_out)
        except:
          print('problem with stock', sym)
          continue
