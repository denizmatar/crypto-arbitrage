import time
import ccxt.async_support as ccxt

from asyncio import gather, get_event_loop
from pprint import pprint

SLIPPAGE = 0.005
MAKER_FEE = 0.002
TAKER_FEE = 0.002

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange', 'slippage', 'maker_fee', 'taker_fee']

ask_prices_dict = {}
bid_prices_dict = {}

class ArbitrageOpportunityChecker:
    def __init__(self):
        self.exchanges = [exchange['name'] for exchange in self.fetch_database('exchanges', {}, {'name': 1})]
        self.pairs = [pair['name'] for pair in self.fetch_database('pairs', {}, {'name': 1})]
        self.all_possible_pairs = [f'{x}/{y}' for x in self.pairs for y in self.pairs if x != y]
        self.dict_constructor(ask_prices_dict)
        self.dict_constructor(bid_prices_dict)


    async def exchange_loop(self, exchange, symbol):
        global orderbook
        print(f'Starting the {exchange.id.upper()} exchange loop for {symbol}')

        while True:
            try:
                orderbook = await exchange.fetch_order_book(symbol)
                print(f"best ask price for {symbol} in {exchange.id} is {orderbook['asks'][0]}")
                print(f"best bid price for {symbol} in {exchange.id} is {orderbook['bids'][0]}")
                ask_prices_dict[symbol].update({exchange.id: orderbook['asks'][0]})
                bid_prices_dict[symbol].update({exchange.id: orderbook['bids'][0]})
                pprint(ask_prices_dict)
                pprint(bid_prices_dict)
                t = time.ctime(time.time())
                print(t)
            except Exception as e:
                print(str(e))
                break

    async def symbol_loop(self, asyncio_loop, symbol, exchange_ids):
        print(f"Starting the {symbol} symbol loop for {exchange_ids}")
        exchanges = [getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'asyncio_loop': asyncio_loop
        }) for exchange_id in exchange_ids]

        loops = [self.exchange_loop(exchange, symbol) for exchange in exchanges]
        await gather(*loops)
        # await exchange.close()

    async def main(self, asyncio_loop):
        loops = [self.symbol_loop(asyncio_loop, pair, self.exchanges) for pair in self.all_possible_pairs]
        await gather(*loops)

    def fetch_database(self, collection, query, fields=None):
        from pymongo import MongoClient

        client = MongoClient(
            'mongodb+srv://denizmatar:aqxmGvgBp6Og3JLX@cluster0.2i4ln.mongodb.net/crypto-arbitrage?retryWrites=true&w=majority',
            ssl=True,
            ssl_ca_certs='/Library/Frameworks/Python.framework/Versions/3.7/etc/openssl/cert.pem')

        db = client['crypto-arbitrage']
        collection = db[collection]
        result = collection.find(query, fields)

        return result

    def dict_constructor(self, dictionary):
        exchanges_dict = {exchange: None for exchange in self.exchanges}
        for pair in self.all_possible_pairs:
            dictionary[pair] = exchanges_dict
            dictionary[pair] = exchanges_dict

    def run(self):
        t = time.ctime(time.time())
        print(t)
        asyncio_loop = get_event_loop()
        asyncio_loop.run_until_complete(self.main(asyncio_loop))