import time
import ccxt.async_support as ccxt

from asyncio import gather, get_event_loop

SLIPPAGE = 0.005
MAKER_FEE = 0.002
TAKER_FEE = 0.002

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange', 'slippage', 'maker_fee', 'taker_fee']

ask_prices_dict = {}
bid_prices_dict = {}


def float_formatter(flt):
    return "{:.2f}".format(flt)


async def exchange_loop(exchange, symbol):
    global orderbook
    print(f'Starting the {exchange.id.upper()} exchange loop for {symbol}')

    while True:
        try:
            orderbook = await exchange.fetch_order_book(symbol)
            print(f"best ask price for {symbol} in {exchange.id} is {orderbook['asks'][0]}")
            print(f"best bid price for {symbol} in {exchange.id} is {orderbook['bids'][0]}")
            ask_prices_dict[symbol].update({exchange.id: orderbook['asks'][0]})
            bid_prices_dict[symbol].update({exchange.id: orderbook['bids'][0]})
            print(ask_prices_dict)
            print(bid_prices_dict)
            t = time.ctime(time.time())
            print(t)
        except Exception as e:
            print(str(e))
            break


async def symbol_loop(asyncio_loop, symbol, exchange_ids):
    print(f"Starting the {symbol} symbol loop for {exchange_ids}")
    exchanges = [getattr(ccxt, exchange_id)({
        'enableRateLimit': True,
        'asyncio_loop': asyncio_loop
    }) for exchange_id in exchange_ids]

    loops = [exchange_loop(exchange, symbol) for exchange in exchanges]
    await gather(*loops)
    await exchange.close()


async def main(asyncio_loop):

    exchanges = [exchange['name'] for exchange in await fetch_database('exchanges', {}, {'name': 1})]
    pairs = [pair['name'] for pair in await fetch_database('pairs', {}, {'name': 1})]
    all_possible_pairs = [f'{x}/{y}' for x in pairs for y in pairs if x != y]

    dict_constructor(ask_prices_dict)
    dict_constructor(bid_prices_dict)


    loops = [symbol_loop(asyncio_loop, pair, exchanges) for pair in all_possible_pairs]
    await gather(*loops)


async def fetch_database(collection, query, fields=None):
    from pymongo import MongoClient

    client = MongoClient(
        'mongodb+srv://denizmatar:aqxmGvgBp6Og3JLX@cluster0.2i4ln.mongodb.net/crypto-arbitrage?retryWrites=true&w=majority',
        ssl=True,
        ssl_ca_certs='/Library/Frameworks/Python.framework/Versions/3.7/etc/openssl/cert.pem')

    db = client['crypto-arbitrage']
    collection = db[collection]
    result = collection.find(query, fields)

    return result


async def dict_constructor(dictionary):

    exchanges_dict = {exchange: None for exchange in exchanges}
    for pair in all_available_pairs:
        dictionary[pair] = exchanges_dict
        dictionary[pair] = exchanges_dict



if __name__ == '__main__':
    t = time.ctime(time.time())
    print(t)
    asyncio_loop = get_event_loop()
    asyncio_loop.run_until_complete(main(asyncio_loop))