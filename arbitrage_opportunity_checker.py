import time
import ccxt.async_support as ccxt
import csv

from asyncio import gather, get_event_loop

SLIPPAGE = 0#0.005
MAKER_FEE = 0#0.002
TAKER_FEE = 0#0.002

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange', 'slippage', 'maker_fee', 'taker_fee']

prices_dict = {}


class ExchangePairs:
    all_exchanges_list = ['binance', 'huobipro', 'coinbasepro', 'kraken', 'kucoin', 'bitstamp', 'hitbtc', 'coinex',
                 'bittrex', 'poloniex', 'okcoin', 'gateio', 'cex', 'exmo', 'bitmax']

    all_exchanges_symbols_dictionary = {}
    all_symbols_list = set()

    def __init__(self):
        self.all_exchanges_symbols_dictionary, self.all_symbols_list = self.run_main()

    async def exchange_symbols_looper(self, exchange_id, asyncio_loop):
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'enableRateLimit': True,
            'asyncio_loop': asyncio_loop
        })

        await exchange.load_markets()
        await exchange.close()
        self.all_exchanges_symbols_dictionary[exchange.id] = exchange.symbols
        self.all_symbols_list.update(exchange.symbols)

    async def main_func(self, asyncio_loop):
        print("Loading all exchange symbols...")
        loops = [self.exchange_symbols_looper(exchange_id, asyncio_loop) for exchange_id in self.all_exchanges_list]
        await gather(*loops)

    def run_main(self):
        asyncio_loop = get_event_loop()
        asyncio_loop.run_until_complete(self.main_func(asyncio_loop))
        return self.all_exchanges_symbols_dictionary, self.all_symbols_list

class ArbitrageOpportunityChecker(ExchangePairs):
    def __init__(self):
        super().__init__()
        self.exchanges = [exchange['name'] for exchange in self.fetch_database('exchanges', {}, {'name': 1})]
        self.coins = [coin['name'] for coin in self.fetch_database('coins', {}, {'name': 1})]
        self.all_possible_pairs = [f'{x}/{y}' for x in self.coins for y in self.coins if x != y]
        self.prices_dict = self.dict_constructor(prices_dict)
        self.asyncio_loop = get_event_loop()
        self.exchange_instances = self.exchange_initializer()

    def exchange_initializer(self):
        exchanges = [getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'asyncio_loop': self.asyncio_loop
        }) for exchange_id in self.exchanges]
        return exchanges

    async def exchange_loop(self, exchange, symbol):
        if symbol in self.all_exchanges_symbols_dictionary[exchange.id]:
            print(f'Starting the {exchange.id.upper()} exchange loop for {symbol}')

            while True:
                try:
                    orderbook = await exchange.fetch_order_book(symbol)
                    self.prices_dict[symbol]['ask'].update({exchange.id: orderbook['asks'][0]})
                    self.prices_dict[symbol]['bid'].update({exchange.id: orderbook['bids'][0]})
                    # print(f"prices for {exchange.id} for {symbol} added successfully.")
                    self.opportunity_checker(symbol)
                    # pprint(self.prices_dict)
                    # t = time.ctime(time.time())
                    # print(t)
                except Exception as e:
                    print('error', str(e))
                    break
                # finally:
            await exchange.close()  # peki bu burda mi olmali??

    async def symbol_loop(self, symbol):
        # this for loop and if statement filters the unavailable pairs
        # for exchange_id in exchange_ids:
        #     if symbol in self.all_exchanges_symbols_dictionary[exchange_id]:
        #         print(f"Starting the {symbol} symbol loop for {exchange_id.upper()}")
        #         exchanges = [getattr(ccxt, exchange_id)({
        #             binance'e her bir pair icin request atinca too many request erroru veriyor. Limit -> 1200/1m
        #             ayni error poloniex icin de geldi...
                    # 'enableRateLimit': True,
                    # 'asyncio_loop': asyncio_loop
                # }) for exchange_id in exchange_ids]

        loops = [self.exchange_loop(exchange, symbol) for exchange in self.exchange_instances]
        await gather(*loops)

    async def main(self):
        loops = [self.symbol_loop(pair) for pair in self.all_possible_pairs]
        await gather(*loops)



    def dict_constructor(self, dictionary):
        exchanges_dict = {exchange: None for exchange in self.exchanges}
        for pair in self.all_possible_pairs:
            if pair in self.all_symbols_list:
                dictionary[pair] = {'ask': {}, 'bid': {}}
        return dictionary

    @staticmethod
    def fetch_database(collection, query, fields=None):
        from pymongo import MongoClient

        print(f"Fetching available {collection} from DB...")

        client = MongoClient(
            'mongodb+srv://denizmatar:aqxmGvgBp6Og3JLX@cluster0.2i4ln.mongodb.net/crypto-arbitrage?retryWrites=true&w=majority',
            ssl=True,
            ssl_ca_certs='/Library/Frameworks/Python.framework/Versions/3.7/etc/openssl/cert.pem')

        db = client['crypto-arbitrage']
        collection = db[collection]
        result = collection.find(query, fields)

        return result

    @staticmethod
    def csv_writer(field_names, headers, data):
        with open(CSV_PATH, mode='a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=',', extrasaction='ignore')
            if headers:
                writer.writeheader()
            writer.writerow(data)
            print("CSV WRITTEN\n")

    @staticmethod
    def float_formatter(flt):
        return "{:.2f}".format(flt)

    def opportunity_checker(self, pair):
        ask_prices_dict = self.prices_dict[pair]['ask']
        bid_prices_dict = self.prices_dict[pair]['bid']

        best_ask_price = min([value[0] for value in list(ask_prices_dict.values())])
        best_ask_price_index = [value[0] for value in list(ask_prices_dict.values())].index(best_ask_price)
        best_ask_price_amount = list(ask_prices_dict.values())[best_ask_price_index][1]
        best_ask_price_exchange = list(ask_prices_dict.keys())[best_ask_price_index]

        best_bid_price = min([value[0] for value in list(bid_prices_dict.values())])
        best_bid_price_index = [value[0] for value in list(bid_prices_dict.values())].index(best_bid_price)
        best_bid_price_amount = list(bid_prices_dict.values())[best_bid_price_index][1]
        best_bid_price_exchange = list(bid_prices_dict.keys())[best_bid_price_index]

        print(f"{time.ctime(time.time())} best ask price for {pair} is {best_ask_price} and best bid price is {best_bid_price}")
        # print(self.prices_dict)

        if best_ask_price < best_bid_price:
            #  Change slippage on the top
            potential_profit = (best_bid_price / best_ask_price - (1 + MAKER_FEE + TAKER_FEE + (SLIPPAGE * 2))) * 100

            if potential_profit > 0:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                print(current_time)

                print("{} POTENTIAL PROFIT OF {}%. BUY ON {} AND SELL ON {}".format(current_time,
                                                                                    self.float_formatter(potential_profit),
                                                                                    best_ask_price_exchange,
                                                                                    best_bid_price_exchange
                                                                                    ))
                # detected = True
                data_dict = {"time": str(current_time),
                             "pair": pair,
                             "profit": potential_profit,
                             "buy_exchange": best_ask_price_exchange,
                             "sell_exchange": best_bid_price_exchange,
                             "slippage": SLIPPAGE,
                             "maker_fee": MAKER_FEE,
                             'taker_fee': TAKER_FEE
                             }

                self.csv_writer(FIELD_NAMES, headers=False, data=data_dict)
            else:
                print("NO POTENTIAL PROFIT")
        else:
            print("NO POTENTIAL PROFIT")

    def run(self):
        print(time.ctime(time.time()))
        self.asyncio_loop.run_until_complete(self.main())

