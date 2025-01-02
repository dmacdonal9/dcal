import logging
from dcal import submit_double_calendar
from ibstrat.market_data import get_current_mid_price
from ibstrat.qualify import qualify_contract, get_front_month_contract_date
from ibstrat.ib_instance import connect_to_ib
import cfg
from ibstrat.chain import fetch_option_chain
from ibstrat.options import find_option_by_target_delta
import argparse
from ibstrat.dteutil import calculate_expiry_date

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DC')
logging.getLogger('ib_async').setLevel(logging.CRITICAL)

def open_double_calendar(symbol: str, params: dict, is_live: bool):
    logger.info(f"Starting Double Calendar Trade Submission for {symbol}")

    try:
        # Qualify the underlying contract
        if params["sec_type"] == 'FUT':
            fut_date = get_front_month_contract_date(symbol, params["exchange"], params["mult"],
                                                     calculate_expiry_date(params["long_expiry_days"]))
        else:
            fut_date=''

        und_contract = qualify_contract(
            symbol=symbol,
            lastTradeDateOrContractMonth=fut_date,
            secType=params["sec_type"],
            exchange=params["exchange"],
            currency='USD'
        )

        # Fetch the current market mid-price
        current_mid = get_current_mid_price(und_contract)
        logger.info(f"Current market price for {symbol}: {current_mid}")

        # Calculate expiry dates
        short_put_expiry_date = calculate_expiry_date(params["short_put_expiry_days"])
        short_call_expiry_date = calculate_expiry_date(params["short_call_expiry_days"])
        long_put_expiry_date = calculate_expiry_date(params["long_put_expiry_days"])
        long_call_expiry_date = calculate_expiry_date(params["long_call_expiry_days"])


        # Fetch option chain and find strikes
        opt_exchange = params["opt_exchange"]
        short_put_tickers = fetch_option_chain(und_contract, opt_exchange, short_put_expiry_date, current_mid,trading_class=params['trading_class'])
        if short_put_expiry_date == short_call_expiry_date:
            short_call_tickers = short_put_tickers
        else:
            short_call_tickers = fetch_option_chain(und_contract, opt_exchange, short_call_expiry_date, current_mid,
                                                    trading_class=params['trading_class'])

        long_put_tickers = fetch_option_chain(und_contract, opt_exchange, long_put_expiry_date, current_mid,trading_class=params['trading_class'])
        if long_put_expiry_date == long_call_expiry_date:
            long_call_tickers = long_put_tickers
        else:
            long_call_tickers = fetch_option_chain(und_contract, opt_exchange, long_call_expiry_date, current_mid,
                                                   trading_class=params['trading_class'])

        short_call_strike = find_option_by_target_delta(short_call_tickers, 'C', params["target_call_delta"],trading_class=params['trading_class']).contract.strike
        short_put_strike = find_option_by_target_delta(short_put_tickers, 'P', params["target_put_delta"],trading_class=params['trading_class']).contract.strike
        long_call_strike = find_option_by_target_delta(long_call_tickers, 'C', params["target_call_delta"],trading_class=params['trading_class']).contract.strike
        long_put_strike = find_option_by_target_delta(long_put_tickers, 'P', params["target_put_delta"],trading_class=params['trading_class']).contract.strike

        # Submit the trade
        trade = submit_double_calendar(
            symbol=symbol,
            short_put_strike=short_put_strike,
            short_call_strike=short_call_strike,
            long_put_strike=long_put_strike,
            long_call_strike=long_call_strike,
            short_put_expiry_date=short_put_expiry_date,
            long_put_expiry_date=long_put_expiry_date,
            short_call_expiry_date=short_call_expiry_date,
            long_call_expiry_date=long_call_expiry_date,
            is_live=is_live
        )
        logger.info(trade)
    except Exception as e:
        logger.exception(f"Error during trade submission for {symbol}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Process double calendar options strategies.")
    parser.add_argument('-l', '--live', action='store_true', help="Use live orders?")
    parser.add_argument('-t', '--test', action='store_true', help="Use test TWS configuration.")
    args = parser.parse_args()

    # Determine symbols and strategy
    symbols = cfg.weekly_dc_symbols
    strategy = cfg.fri_dc_params

    live_orders = args.live
    use_test_tws = args.test

    logger.info(f"Live trading mode: {'Enabled' if live_orders else 'Disabled'}")
    logger.info(f"Test TWS mode: {'Enabled' if use_test_tws else 'Disabled'}")

    # Connect to the appropriate IBKR instance
    if use_test_tws:
        ib = connect_to_ib(cfg.test_ib_host, cfg.test_ib_port, cfg.test_ib_clientid, 2)
        logger.info("Connected to test TWS configuration.")
    else:
        ib = connect_to_ib(cfg.ib_host, cfg.ib_port, cfg.ib_clientid, 2)
        logger.info("Connected to live TWS configuration.")

    # cache open positions so we can check for collisions later
    #load_positions()

    # Execute the selected action
    for symbol in symbols:
        params = strategy.get(symbol)
        if not params:
            logger.error(f"Parameters for {symbol} not found in strategy configuration.")
            continue
        open_double_calendar(symbol, params, args.live)


if __name__ == "__main__":
    main()