import logging
from dcal import submit_double_calendar, close_dcal
from market_data import get_current_mid_price
from qualify import qualify_contract, get_front_month_contract_date
from ib_instance import connect_to_ib
import cfg
from options import find_option_closest_to_delta, fetch_option_chain
import sys
import argparse
from dteutil import calculate_expiry_date

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DC')
logging.getLogger('ib_insync').setLevel(logging.CRITICAL)

def open_double_calendar(symbol: str, params: dict, is_live: bool, strategy_type: str = 'daily'):
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
        short_expiry_date = calculate_expiry_date(params["short_expiry_days"])
        long_expiry_date = calculate_expiry_date(params["long_expiry_days"])

        # Fetch option chain and find strikes
        opt_exchange = params["opt_exchange"]
        short_tickers = fetch_option_chain(und_contract, opt_exchange, short_expiry_date, current_mid)
        long_tickers = fetch_option_chain(und_contract, opt_exchange, long_expiry_date, current_mid)

        short_call_strike = find_option_closest_to_delta(short_tickers, 'C', params["target_call_delta"]).contract.strike
        short_put_strike = find_option_closest_to_delta(short_tickers, 'P', params["target_put_delta"]).contract.strike

        long_call_strike = find_option_closest_to_delta(long_tickers, 'C', params["target_call_delta"]).contract.strike
        long_put_strike = find_option_closest_to_delta(long_tickers, 'P', params["target_put_delta"]).contract.strike

        # Submit the trade
        trade = submit_double_calendar(
            symbol=symbol,
            short_put_strike=short_put_strike,
            short_call_strike=short_call_strike,
            long_put_strike=long_put_strike,
            long_call_strike=long_call_strike,
            short_expiry_date=short_expiry_date,
            long_expiry_date=long_expiry_date,
            strategy_type=strategy_type,
            is_live=is_live
        )
        logger.info(trade)
    except Exception as e:
        logger.exception(f"Error during trade submission for {symbol}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process double calendar options strategies.")
    parser.add_argument('-d', '--open_daily', action='store_true', help="Open a daily double calendar (DCAL) position.")
    parser.add_argument('-c', '--close_daily', action='store_true', help="Close a daily double calendar (DCAL) position.")
    parser.add_argument('-w', '--open_weekly', action='store_true', help="Open a weekly double calendar (DCAL) position.")
    parser.add_argument('-l', '--live', action='store_true', help="Use live orders?")
    parser.add_argument('-t', '--test', action='store_true', help="Use test TWS configuration.")
    args = parser.parse_args()

    # Ensure mutually exclusive arguments
    if sum([args.open_daily, args.open_weekly, args.close_daily]) > 1:
        logger.error("Error: Cannot specify more than one action. Use only one of -d (open daily), -w (open weekly), or -c (close daily).")
        sys.exit(1)

    # Determine symbols and strategy
    if args.open_weekly:
        print("Opening weekly DCs")
        symbols = cfg.weekly_dc_symbols
        strategy = cfg.weekly_dc_params
    elif args.open_daily:
        print("Opening daily DCs")
        symbols = cfg.daily_dc_symbols
        strategy = cfg.daily_dc_params
    elif args.close_daily:
        print("Closing daily DCs")
        symbols = cfg.daily_dc_symbols
        strategy = cfg.daily_dc_params
    else:
        logger.error("Error: No action specified. Use -d, -w, or -c.")
        sys.exit(1)

    connect_to_ib(is_test=args.test)

    # Execute the selected action
    if args.open_daily or args.open_weekly:
        for symbol in symbols:
            params = strategy.get(symbol)
            if not params:
                logger.error(f"Parameters for {symbol} not found in strategy configuration.")
                continue
            open_double_calendar(symbol, params, args.live, strategy_type='weekly' if args.open_weekly else 'daily')
    elif args.close_daily:
        for symbol in symbols:
            close_dcal(symbol)

if __name__ == "__main__":
    main()