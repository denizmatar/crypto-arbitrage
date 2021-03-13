from arbitrage_opportunity_checker import ArbitrageOpportunityChecker, ExchangeInitializer, ExchangePairs
from exchange_pairs import ExchangePairs


if __name__ == '__main__':
    get_exchange_pairs = ExchangePairs()
    all_exchanges_symbols_dictionary = get_exchange_pairs.all_exchanges_symbols_dictionary
    all_symbols_list = get_exchange_pairs.all_symbols_list

    opportunity_checker = ArbitrageOpportunityChecker(all_symbols_list, all_exchanges_symbols_dictionary)

    main_asyncio_loop = opportunity_checker.asyncio_loop
    operating_exchange_names = opportunity_checker.operating_exchange_names

    exchange_initializer = ExchangeInitializer(main_asyncio_loop, operating_exchange_names)

    exchange_instances = exchange_initializer.exchange_instances

    opportunity_checker.run(exchange_instances)
