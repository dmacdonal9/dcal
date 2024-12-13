import logging
from dcal import submit_double_calendar, close_dcal
from market_data import get_current_mid_price
from qualify import qualify_contract
from ib_instance import connect_to_ib
import cfg
from datetime import datetime, timedelta
from options import find_option_closest_to_delta, fetch_option_chain
import sys
import argparse
from orders import show_recently_filled_spreads

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DC')
logging.getLogger('ib_insync').setLevel(logging.CRITICAL)

def calculate_expiry_date(days_from_today: int) -> str:
    # Calculate the initial expiry date
    expiry_date = datetime.now() + timedelta(days=days_from_today)

    # Check if the expiry date falls on a weekend (Saturday or Sunday)
    if expiry_date.weekday() == 5:  # Saturday
        expiry_date += timedelta(days=2)  # Move to Monday
    elif expiry_date.weekday() == 6:  # Sunday
        expiry_date += timedelta(days=1)  # Move to Monday

    # Return the expiry date in the desired format
    return expiry_date.strftime('%Y%m%d')


def open_dcal(symbol: str, is_live: bool, is_test: bool):
    logger.info("Starting Double Calendar Trade Submission")
    und_exchange = cfg.exchange

    # Connect to the appropriate IBKR instance
    connect_to_ib(is_test=is_test)

    try:
        # Qualify the underlying contract
        und_contract = qualify_contract(
            symbol=symbol,
            secType='IND',
            exchange='CBOE',
            currency='USD'
        )

        # Fetch the current market mid-price
        current_mid = get_current_mid_price(und_contract)
        logger.info(f"Current market price for {symbol}: {current_mid}")

        # Calculate expiry dates
        short_expiry_date = calculate_expiry_date(cfg.short_expiry_days)
        long_expiry_date = calculate_expiry_date(cfg.long_expiry_days)

        short_tickers = fetch_option_chain(und_contract, short_expiry_date, current_mid)

        call_strike = find_option_closest_to_delta(short_tickers, 'C', cfg.target_call_delta).contract.strike
        put_strike = find_option_closest_to_delta(short_tickers, 'P', cfg.target_put_delta).contract.strike

        trade = submit_double_calendar(
            symbol=symbol, put_strike=put_strike, call_strike=call_strike, exchange=und_exchange, und_price=current_mid,
            quantity=cfg.quantity, short_expiry_date=short_expiry_date, long_expiry_date=long_expiry_date, is_live=is_live)
        print(trade)

        # Setup the closing order
        try:
            close_dcal(symbol, cfg.time_to_close)
        except Exception as e:
            print(f"An error occurred: {e}")

    except Exception as e:
        logger.exception(f"Error during trade submission: {e}")


def main():
    symbol = cfg.symbol

    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process double calendar options strategies.")

    # Define the arguments
    parser.add_argument('-o', '--open', action='store_true', help="Open a double calendar (DCAL) position.")
    parser.add_argument('-c', '--close', action='store_true', help="Close a double calendar (DCAL) position.")
    parser.add_argument('-l', '--live', action='store_true', help="Use live orders?")
    parser.add_argument('-t', '--test', action='store_true', help="Use test TWS configuration.")

    # Parse the arguments
    args = parser.parse_args()
    connect_to_ib(args.test)

    # Handle the arguments
    if args.open and args.close:
        print("Error: Cannot specify both -o and -c. Choose one.", file=sys.stderr)
        sys.exit(1)
    elif args.open:
        open_dcal(symbol, is_live=args.live, is_test=args.test)
        show_recently_filled_spreads('today', cfg.myStrategyTag)
    elif args.close:
        closing_date_time = datetime.now().strftime('%Y%m%d') + ' ' + cfg.time_to_close  # Full closing time
        close_dcal(symbol, closing_date_time)
        show_recently_filled_spreads(timeframe='today', strategy=cfg.myStrategyTag)
    else:
        print("Error: No action specified. Use -o to open or -c to close.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()