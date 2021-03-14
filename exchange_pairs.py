import ccxt.async_support as ccxt
from asyncio import gather, get_event_loop


class ExchangePairs:
    all_exchanges_list = ['binance', 'huobipro', 'coinbasepro', 'kraken', 'kucoin', 'bitstamp', 'hitbtc', 'coinex',
                          'bittrex', 'poloniex', 'okcoin', 'gateio', 'cex', 'exmo', 'bitmax', 'bitstamp', 'bithumb',
                          'gemini', 'okex', 'liquid', 'coincheck', 'zaif', 'aax',
                          'bitmex', 'bitvavo', 'bytetrade', 'currencycom', 'eterbase', 'ftx', 'gopax', 'idex', 'xena'
                          ]

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
        # exchange.verbose = True
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
