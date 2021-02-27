"""
    #   A         B         C         D         E            F           G
    # [33245.9, 33185.19, 33192.14, 45998.8, 33145.27, 33184.33038462, 33211.61]  # ask prices
    # [33141.5, 33158.49, 33085.33, 30000.1, 33134.99, 33087.40818475, 33037.91]  # bid prices

    # eger ask pricestaki minimum deger bid pricestaki maximum degerden kucukse:
    #    ask tarafinda al, bid tarafinda sat
"""

import ccxt
import json
from exchanges import *

exchange = ccxt.binance()
exchange.load_markets()

ask_prices_dict = {}
bid_prices_dict = {}

SLIPPAGE = 0

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

                result = exchange.fetch_ticker("YFI/USDT")

                ask_prices_dict[ex] = result['ask']
                bid_prices_dict[ex] = result['bid']

                print(count, ex, "done")

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
            potential_profit = (best_bid_price / best_ask_price - (1 + (SLIPPAGE * 2))) * 100

            if potential_profit > 0:
                print("POTENTIAL PROFIT OF {}. BUY ON {} AND SELL ON {}\n".format(potential_profit,
                                                                                best_ask_price_exchange,
                                                                                best_bid_price_exchange
                                                                                ))
                # detected = True
        else:
            print("NO POTENTIAL PROFIT\n")



arbitrage_opportunity_check(exchanges_list)





