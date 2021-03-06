import time
import ccxt.async_support as ccxt

from asyncio import gather, get_event_loop

SLIPPAGE = 0.005
MAKER_FEE = 0.002
TAKER_FEE = 0.002

CSV_PATH = "/Users/denizmatar/PycharmProjects/crypto-arbitrage/data.csv"
FIELD_NAMES = ['time', 'pair', 'profit', 'buy_exchange', 'sell_exchange', 'slippage', 'maker_fee', 'taker_fee']

ask_prices_dict = {
    'last_update': None,
    'BTC/USDT': {'binance': None,
                 'kraken': None,
                 'poloniex': None},
    'ATOM/BTC': {'binance': None,
                 'kraken': None,
                 'poloniex': None},
    'ETH/BTC': {'binance': None,
                'kraken': None,
                'poloniex': None}}
bid_prices_dict = {
    'last_update': None,
    'BTC/USDT': {'binance': None,
                 'kraken': None,
                 'poloniex': None},
    'ATOM/BTC': {'binance': None,
                 'kraken': None,
                 'poloniex': None},
    'ETH/BTC': {'binance': None,
                'kraken': None,
                'poloniex': None}}

def float_formatter(flt):
    return "{:.2f}".format(flt)


# async def per_exchange_per_symbol()


async def exchange_loop(exchange, symbol):
    global orderbook
    print(f'Starting the {exchange.id.upper()} exchange loop for {symbol}')

    while True:
        try:
            orderbook = await exchange.fetch_order_book(symbol)
            print(f"best ask price for {symbol} in {exchange.id} is {orderbook['asks'][0]}")
            print(f"best bid price for {symbol} in {exchange.id} is {orderbook['bids'][0]}")
            ask_prices_dict[symbol].update({exchange.id: orderbook['asks'][0][0]})
            bid_prices_dict[symbol].update({exchange.id: orderbook['bids'][0][0]})
            print(ask_prices_dict)
            print(bid_prices_dict)
        except Exception as e:
            print(str(e))
            break
    # print(ask_prices_dict)
    # print(bid_prices_dict)



async def symbol_loop(asyncio_loop, symbol, exchange_ids):
    print(f"Starting the {symbol} symbol loop for {exchange_ids}")
    # ask_prices_dict = {}
    # bid_prices_dict = {}
    exchanges = [getattr(ccxt, exchange_id)({
        'enableRateLimit': True,
        'asyncio_loop': asyncio_loop
    }) for exchange_id in exchange_ids]

    loops = [exchange_loop(exchange, symbol) for exchange in exchanges]
    await gather(*loops)

    # ask_prices_dict[symbol] = {exchange.id: orderbook['asks'][0][0]}
    # bid_prices_dict[symbol] = {exchange.id: orderbook['bids'][0][0]}
    # print(ask_prices_dict)
    # print(bid_prices_dict)
    await exchange.close()



async def main(asyncio_loop):
    exchanges = {
        'binance': ['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
        'kraken': ['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
        'bitfinex': ['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
    }

    pairs = {
        'BTC/USDT': ['binance', 'kraken', 'poloniex'],
        'ATOM/BTC': ['binance', 'kraken', 'poloniex'],
        'ETH/BTC': ['binance', 'kraken', 'poloniex']
    }
    loops = [symbol_loop(asyncio_loop, symbol, exchange_ids) for symbol, exchange_ids in pairs.items()]
    await gather(*loops)


if __name__ == '__main__':
    asyncio_loop = get_event_loop()
    asyncio_loop.run_until_complete(main(asyncio_loop))