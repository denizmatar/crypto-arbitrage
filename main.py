# -*- coding: utf-8 -*-

import asyncio
import os
import sys
import json
from pprint import pprint

# root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(root + '/python')

import ccxt.async_support as ccxt  # noqa: E402
import pairs
import exchanges


EXCHANGE_IDS = exchanges.exchanges_list

SLIPPAGE = 0.005
MAKER_FEE = 0.002
TAKER_FEE = 0.002

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange', 'slippage', 'maker_fee', 'taker_fee']


def csv_writer(field_names, headers, data):
    with open(CSV_PATH, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=',', extrasaction='ignore')
        if headers:
            writer.writeheader()
        writer.writerow(data)
        print("CSV WRITTEN\n")


def float_formatter(flt):
    return "{:.2f}".format(flt)

async def loop(exchange_id, symbol):

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({'enableRateLimit': True})
    try:
        # exchange.verbose = True  # uncomment for debugging purposes
        ticker = await exchange.fetch_ticker(symbol)
        print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)

        ask_prices_dict[exchange.name] = ticker['ask']
        bid_prices_dict[exchange.name] = ticker['bid']
    except Exception as e:
        print(type(e).__name__, str(e))
    await exchange.close()

async def run(EXCHANGE_IDS, symbol):
    coroutines = [loop(exchange_id, symbol) for exchange_id in EXCHANGE_IDS]
    return await asyncio.gather(*coroutines)


# main = run(EXCHANGE_IDS, symbol)
# results = asyncio.get_event_loop().run_until_complete(main)
while True:
    for pair in pairs.pairs:
        global ask_prices_dict, bid_prices_dict
        ask_prices_dict = {}
        bid_prices_dict = {}
        main = run(EXCHANGE_IDS, pair)
        results = asyncio.get_event_loop().run_until_complete(main)
        # print(json.dumps(results, indent=4))
        best_ask_price = min(list(ask_prices_dict.values()))
        best_ask_price_index = list(ask_prices_dict.values()).index(best_ask_price)
        best_ask_price_exchange = list(ask_prices_dict.keys())[best_ask_price_index]

        best_bid_price = max(list(bid_prices_dict.values()))
        best_bid_price_index = list(bid_prices_dict.values()).index(best_bid_price)
        best_bid_price_exchange = list(bid_prices_dict.keys())[best_bid_price_index]

        if best_ask_price < best_bid_price:
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
                             "sell_exchange": best_bid_price_exchange,
                             "slippage": SLIPPAGE,
                             "maker_fee": MAKER_FEE,
                             'taker_fee': TAKER_FEE
                             }

                csv_writer(FIELD_NAMES, headers=False, data=data_dict)
            else:
                print("NO POTENTIAL PROFIT\n")
        else:
            print("NO POTENTIAL PROFIT\n")
