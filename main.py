"""
# EXCHANGE A        B         C         D         E            F           G
    # [33245.9, 33185.19, 33192.14, 45998.8, 33145.27, 33184.33038462, 33211.61]  # ask prices
    # [33141.5, 33158.49, 33085.33, 30000.1, 33134.99, 33087.40818475, 33037.91]  # bid prices

    # eger ask pricestaki minimum deger bid pricestaki maximum degerden kucukse:
    #    ask tarafinda al, bid tarafinda sat
"""

import ccxt
import json
import csv
import time
from exchanges import *

exchange = ccxt.binance()
exchange.load_markets()

ask_prices_dict = {}
bid_prices_dict = {}

PAIR = "ADA/USDT"

SLIPPAGE = 0
MAKER_FEE = 0
TAKER_FEE = 0

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange']

def csv_writer(field_names, headers, data):

    with open(CSV_PATH, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=',', extrasaction='ignore')
        if headers:
            writer.writeheader()
        writer.writerow(data)
        print("CSV WRITTEN\n")

def float_formatter(float):
    return "{:.2f}".format(float)

def arbitrage_opportunity_check(exchanges_list, pair_list=None):
    detected = False

    while not detected:
        count = 1

        for ex in exchanges_list:
            try:
                exchange_id = ex
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class({
                    'apiKey': 'YOUR_API_KEY',
                    'secret': 'YOUR_SECRET',
                    'timeout': 30000,
                    'enableRateLimit': True,
                })

                result = exchange.fetch_ticker(PAIR)

                ask_prices_dict[ex] = result['ask']
                bid_prices_dict[ex] = result['bid']

                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)

                print(current_time, count, ex, "done")

                count += 1
            except Exception as e:
                print(count, ex, "ERROR:", e)

                count += 1

        print("ASK PRICES:", ask_prices_dict) # dict
        print("BID PRICES:", bid_prices_dict) # dict

        best_ask_price = min(list(ask_prices_dict.values()))
        best_ask_price_index = list(ask_prices_dict.values()).index(best_ask_price)
        best_ask_price_exchange = list(ask_prices_dict.keys())[best_ask_price_index]

        best_bid_price = max(list(bid_prices_dict.values()))
        best_bid_price_index = list(bid_prices_dict.values()).index(best_bid_price)
        best_bid_price_exchange = list(bid_prices_dict.keys())[best_bid_price_index]

        if  best_ask_price < best_bid_price:
            #  Change slippage on the top
            potential_profit = (best_bid_price / best_ask_price - (1 + MAKER_FEE + TAKER_FEE + (SLIPPAGE * 2))) * 100

            if potential_profit > 0:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                print(current_time)

                print("{} POTENTIAL PROFIT OF {}%. BUY ON {} AND SELL ON {}".format(current_time,
                                                                                     float_formatter(potential_profit),
                                                                                     best_ask_price_exchange,
                                                                                     best_bid_price_exchange
                                                                                     ))
                # detected = True
                data_dict = {"time": str(current_time),
                             "pair": PAIR,
                             "profit": potential_profit,
                             "buy_exchange": best_ask_price_exchange,
                             "sell_exchange": best_bid_price_exchange
                             }

                csv_writer(FIELD_NAMES, headers=False, data=data_dict)
        else:
            print("NO POTENTIAL PROFIT")
# TODO: research websocket and FIX


arbitrage_opportunity_check(exchanges_list)





