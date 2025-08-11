import logging
from dcal import submit_double_calendar
from ibstrat.market_data import get_current_mid_price
from ibstrat.qualify import qualify_contract, get_front_month_contract_date
from ibstrat.ib_instance import connect_to_ib
from ibstrat.positions import load_positions, check_positions
import cfg
import sys
from ibstrat.chain import fetch_option_chain,find_next_closest_expiry
from ibstrat.options import find_option_by_target_delta,find_option_by_target_strike
import argparse
from ibstrat.dteutil import calculate_expiry_date
from ibstrat.trclass import get_trading_class_for_symbol

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
logging.getLogger("ibstrat.market_data").setLevel(logging.DEBUG)
logging.getLogger("ibstrat.options").setLevel(logging.DEBUG)
logging.getLogger("ibstrat.chain").setLevel(logging.ERROR)
logging.getLogger("ibstrat.orders").setLevel(logging.ERROR)

def open_double_calendar(symbol: str, params: dict, is_live: bool):
    logger.info(f"Starting Double Calendar Trade Submission for {symbol}")
    logger.debug(f"Strategy parameters: {params}")

    tr_class = get_trading_class_for_symbol(symbol)

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
        logger.debug(f"short expiry days are set to: {params['short_put_expiry_days']} {params['short_call_expiry_days']} ")
        logger.debug(f"long expiry days are set to: {params['long_put_expiry_days']} {params['long_call_expiry_days']} ")

        short_put_expiry_date = find_next_closest_expiry(und_contract=und_contract,
                                                         target_expiry=calculate_expiry_date(params["short_put_expiry_days"]),
                                                         trading_class=tr_class)
        short_call_expiry_date = find_next_closest_expiry(und_contract=und_contract,
                                                         target_expiry=calculate_expiry_date(params["short_call_expiry_days"]),
                                                         trading_class=tr_class)
        long_put_expiry_date = find_next_closest_expiry(und_contract=und_contract,
                                                         target_expiry=calculate_expiry_date(params["long_put_expiry_days"]),
                                                         trading_class=tr_class)
        long_call_expiry_date = find_next_closest_expiry(und_contract=und_contract,
                                                         target_expiry=calculate_expiry_date(params["long_call_expiry_days"]),
                                                         trading_class=tr_class)

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

        logger.debug(f"Option chains fetched. Calculating strikes...")
        short_call_strike = find_option_by_target_delta(short_call_tickers, 'C', params["target_call_delta"],
                                                        trading_class=params['trading_class']).contract.strike
        logger.debug(f"short call found: {short_call_strike}")

        short_put_strike = find_option_by_target_delta(short_put_tickers, 'P', params["target_put_delta"],
                                                       trading_class=params['trading_class']).contract.strike
        logger.debug(f"short put found: {short_put_strike}")

        long_call = find_option_by_target_strike(contract=und_contract,
                                                        right='C',
                                                        exchange=params["opt_exchange"],
                                                        expiry=long_call_expiry_date,
                                                        target_strike=short_call_strike,
                                                        trading_class=params['trading_class'])
        logger.debug(f"long call found: {long_call.strike}")
        long_call_strike = long_call.strike

        long_put = find_option_by_target_strike(contract=und_contract,
                                                        right='P',
                                                        exchange=params["opt_exchange"],
                                                        expiry=long_put_expiry_date,
                                                        target_strike=short_put_strike,
                                                        trading_class=params['trading_class'])
        logger.debug(f"long put found: {long_put.strike}")
        long_put_strike = long_put.strike

        logger.debug(f"Calculated strikes - Short Call: {short_call_strike}, Short Put: {short_put_strike}, "
                     f"Long Call: {long_call_strike}, Long Put: {long_put_strike}")

        # Prepare position check list
        pos_check_list = [
            {'strike': short_put_strike, 'right': 'P', 'expiry': short_put_expiry_date, 'position_type': 'long'},
            {'strike': short_call_strike, 'right': 'C', 'expiry': short_call_expiry_date, 'position_type': 'long'},
            {'strike': long_put_strike, 'right': 'P', 'expiry': long_put_expiry_date, 'position_type': 'short'},
            {'strike': long_call_strike, 'right': 'C', 'expiry': long_call_expiry_date, 'position_type': 'short'},
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
    parser.add_argument('-m24', '--monday24', action='store_true', help="Submit Monday Double Calendar using Monday 24 config.")
    parser.add_argument('-m37', '--monday37', action='store_true', help="Submit Monday Double Calendar using Monday 37 config.")
    parser.add_argument('-w78', '--wednesday78', action='store_true', help="Submit Wednesday Double Calendar using Wednesday config.")
    parser.add_argument('-f57', '--friday57', action='store_true', help="Submit Friday Double Calendar using 57 config.")
    parser.add_argument('-f67', '--friday67', action='store_true', help="Submit Friday Double Calendar using 67 config.")
    parser.add_argument('-s', '--symbol', type=str, help="Trade a specific symbol only (overrides config list).")

    args = parser.parse_args()

    # Collect selected config flags
    selected_configs = []
    if args.friday57:
        selected_configs.append(("Friday57", cfg.fri_57dc_symbols, cfg.fri_57dc_params))
    if args.friday67:
        selected_configs.append(("Friday67", cfg.fri_67dc_symbols, cfg.fri_67dc_params))
    if args.monday24:
        selected_configs.append(("Monday24", cfg.mon_dc24_symbols, cfg.mon_dc24_params))
    if args.monday37:
        selected_configs.append(("Monday37", cfg.mon_dc37_symbols, cfg.mon_dc37_params))
    if args.wednesday78:
        selected_configs.append(("Wednesday78", cfg.wed_dc78_symbols, cfg.wed_dc78_params))

    # Enforce exactly one config flag always
    if len(selected_configs) != 1:
        logger.error("You must specify exactly one configuration: -f57, -f67, -m24, -m37, or -w78.")
        return

    cfg_name, cfg_symbols, cfg_params = selected_configs[0]

    # If -s is provided, restrict to that symbol within the chosen config
    if args.symbol:
        symbol = args.symbol.strip().upper()
        if symbol not in cfg_params:
            logger.error(f"Symbol '{symbol}' not found in {cfg_name} parameters.")
            return
        symbols = [symbol]
        params = {symbol: cfg_params[symbol]}
        logger.info(f"Running single symbol DC for {symbol} using {cfg_name}")
    else:
        symbols = cfg_symbols
        params = cfg_params
        logger.info(f"Running {cfg_name}")

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

    load_positions()

    # Execute the selected action
    for symbol in symbols:
        open_double_calendar(symbol, params[symbol], live_orders)


if __name__ == "__main__":
    main()
