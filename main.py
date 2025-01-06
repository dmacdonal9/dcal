import logging
from dcal import submit_double_calendar
from ibstrat.market_data import get_current_mid_price
from ibstrat.qualify import qualify_contract, get_front_month_contract_date
from ibstrat.ib_instance import connect_to_ib
from ibstrat.positions import check_positions
import cfg
from ibstrat.chain import fetch_option_chain
from ibstrat.options import find_option_by_target_delta
import argparse
from ibstrat.dteutil import calculate_expiry_date

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('DC')

logging.getLogger("ib_async").setLevel(logging.CRITICAL)
logging.getLogger("ibstrat.indicators").setLevel(logging.ERROR)
logging.getLogger("ibstrat.ib_instance").setLevel(logging.ERROR)
logging.getLogger("ibstrat.dteutil").setLevel(logging.ERROR)
logging.getLogger("ibstrat.qualify").setLevel(logging.ERROR)
logging.getLogger("ibstrat.market_data").setLevel(logging.ERROR)
logging.getLogger("ibstrat.options").setLevel(logging.ERROR)
logging.getLogger("ibstrat.chain").setLevel(logging.ERROR)
logging.getLogger("ibstrat.orders").setLevel(logging.DEBUG)

def open_double_calendar(symbol: str, params: dict, is_live: bool):
    logger.info(f"Starting Double Calendar Trade Submission for {symbol} with strategy tag {params['strategy_tag']}")

    try:
        # Qualify the underlying contract
        if params["sec_type"] == 'FUT':
            fut_date = get_front_month_contract_date(symbol, params["exchange"], params["mult"],
                                                     calculate_expiry_date(params["long_call_expiry_days"]))
            logger.debug(f"Front month contract date for {symbol}: {fut_date}")
        else:
            fut_date = ''
            logger.debug(f"No front month date required for {symbol}, secType: {params['sec_type']}")

        und_contract = qualify_contract(
            symbol=symbol,
            lastTradeDateOrContractMonth=fut_date,
            secType=params["sec_type"],
            exchange=params["exchange"],
            currency='USD'
        )
        logger.debug(f"Qualified underlying contract: {und_contract}")

        # Fetch the current market mid-price
        current_mid = get_current_mid_price(und_contract)
        logger.info(f"Current market price for {symbol}: {current_mid}")

        # Calculate expiry dates
        short_put_expiry_date = calculate_expiry_date(params["short_put_expiry_days"])
        short_call_expiry_date = calculate_expiry_date(params["short_call_expiry_days"])
        long_put_expiry_date = calculate_expiry_date(params["long_put_expiry_days"])
        long_call_expiry_date = calculate_expiry_date(params["long_call_expiry_days"])
        logger.debug(f"Expiry dates - Short Put: {short_put_expiry_date}, Long Put: {long_put_expiry_date}, "
                     f"Short Call: {short_call_expiry_date}, Long Call: {long_call_expiry_date}")

        # Fetch option chain and find strikes
        logger.debug(f"Fetching option chains for {symbol}")
        opt_exchange = params["opt_exchange"]
        short_put_tickers = fetch_option_chain(und_contract, opt_exchange, short_put_expiry_date, current_mid,
                                               trading_class=params['trading_class'])
        if short_put_expiry_date == short_call_expiry_date:
            short_call_tickers = short_put_tickers
        else:
            short_call_tickers = fetch_option_chain(und_contract, opt_exchange, short_call_expiry_date, current_mid,
                                                    trading_class=params['trading_class'])

        long_put_tickers = fetch_option_chain(und_contract, opt_exchange, long_put_expiry_date, current_mid,
                                              trading_class=params['trading_class'])
        if long_put_expiry_date == long_call_expiry_date:
            long_call_tickers = long_put_tickers
        else:
            long_call_tickers = fetch_option_chain(und_contract, opt_exchange, long_call_expiry_date, current_mid,
                                                   trading_class=params['trading_class'])

        logger.debug(f"Option chains fetched. Calculating strikes...")
        short_call_strike = find_option_by_target_delta(short_call_tickers, 'C', params["target_call_delta"],
                                                        trading_class=params['trading_class']).contract.strike
        short_put_strike = find_option_by_target_delta(short_put_tickers, 'P', params["target_put_delta"],
                                                       trading_class=params['trading_class']).contract.strike
        long_call_strike = find_option_by_target_delta(long_call_tickers, 'C', params["target_call_delta"],
                                                       trading_class=params['trading_class']).contract.strike
        long_put_strike = find_option_by_target_delta(long_put_tickers, 'P', params["target_put_delta"],
                                                      trading_class=params['trading_class']).contract.strike

        logger.debug(f"Calculated strikes - Short Call: {short_call_strike}, Short Put: {short_put_strike}, "
                     f"Long Call: {long_call_strike}, Long Put: {long_put_strike}")

        # Prepare position check list
        pos_check_list = [
            {'strike': short_put_strike, 'right': 'P', 'expiry': short_put_expiry_date, 'position_type': None},
            {'strike': short_call_strike, 'right': 'C', 'expiry': short_call_expiry_date, 'position_type': None},
            {'strike': long_put_strike, 'right': 'P', 'expiry': long_put_expiry_date, 'position_type': None},
            {'strike': long_call_strike, 'right': 'C', 'expiry': long_call_expiry_date, 'position_type': None},
        ]
        logger.debug(f"Position check list: {pos_check_list}")

        # Check existing positions
        existing_pos_open = check_positions(symbol, pos_check_list)
        if existing_pos_open:
            logger.warning(f"We have potential collisions on strikes, aborting trade")
            return None

        # Submit the trade
        logger.info(f"Submitting Double Calendar trade for {symbol}")
        trade = submit_double_calendar(
            und_contract=und_contract,
            short_put_strike=short_put_strike,
            short_call_strike=short_call_strike,
            long_put_strike=long_put_strike,
            long_call_strike=long_call_strike,
            short_put_expiry_date=short_put_expiry_date,
            long_put_expiry_date=long_put_expiry_date,
            short_call_expiry_date=short_call_expiry_date,
            long_call_expiry_date=long_call_expiry_date,
            is_live=is_live,
            strategy_params=params
        )
        logger.info(f"Trade submission result: {trade}")
    except Exception as e:
        logger.exception(f"Error during trade submission for {symbol}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Process double calendar options strategies.")
    parser.add_argument('-l', '--live', action='store_true', help="Use live orders?")
    parser.add_argument('-t', '--test', action='store_true', help="Use test TWS configuration.")
    parser.add_argument('-m', '--monday', action='store_true', help="Submit Mon Double Calendar using mon config.")
    parser.add_argument('-w', '--wednesday', action='store_true', help="Submit Wed Double Calendar using wed config.")
    parser.add_argument('-f', '--friday', action='store_true', help="Submit Fri Double Calendar using fri config.")

    args = parser.parse_args()

    # Ensure mutually exclusive -f and -m
    if args.friday and args.monday:
        logger.error("Arguments -f and -m are mutually exclusive. Please use only one.")
        return

    # Determine the selected configuration
    if args.friday:
        symbols = cfg.fri_dc_symbols
        strategy = cfg.fri_dc_params
        logger.info(f"Running Friday DC")
    elif args.monday:
        symbols = cfg.mon_dc_symbols
        strategy = cfg.mon_dc_params
        logger.info(f"Running Monday DC")
    elif args.wednesday:
        symbols = cfg.wed_dc_symbols
        strategy = cfg.wed_dc_params
        logger.info(f"Running Wednesday DC")
    else:
        logger.error("You must specify either -f (Friday config) or -m (Monday config).")
        return

    live_orders = args.live
    use_test_tws = args.test

    logger.info(f"Live trading mode: {'Enabled' if live_orders else 'Disabled'}")
    logger.info(f"Test TWS mode: {'Enabled' if use_test_tws else 'Disabled'}")

    # Connect to the appropriate IBKR instance
    if use_test_tws:
        connect_to_ib(cfg.test_ib_host, cfg.test_ib_port, cfg.test_ib_clientid, 2)
        logger.info("Connected to test TWS configuration.")
    else:
        connect_to_ib(cfg.ib_host, cfg.ib_port, cfg.ib_clientid, 2)
        logger.info("Connected to live TWS configuration.")

    # Execute the selected action
    for symbol in symbols:
        strategies = strategy.get(symbol)
        if not strategies:
            logger.error(f"No strategies found for {symbol} in configuration.")
            continue

        for params in strategies:
            logger.info(f"Processing strategy for {symbol} with strategy tag {params['strategy_tag']}")
            open_double_calendar(symbol, params, live_orders)


if __name__ == "__main__":
    main()