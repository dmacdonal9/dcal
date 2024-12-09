import logging
from dcal import submit_double_calendar
from market_data import get_current_mid_price
from qualify import qualify_contract
import cfg
from datetime import datetime, timedelta
from options import find_option_closest_to_delta, fetch_option_chain
from ib_insync import Ticker
import sys

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DC')
logging.getLogger('ib_insync').setLevel(logging.CRITICAL)


def calculate_expiry_date(days_from_today: int):

    expiry_date = datetime.now() + timedelta(days=days_from_today)
    return expiry_date.strftime('%Y%m%d')

def main():

    logger.info("Starting Double Calendar Trade Submission")
    symbol=cfg.symbol
    und_exchange='CBOE'

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

        short_tickers = fetch_option_chain(und_contract,short_expiry_date,current_mid)

        call_strike = find_option_closest_to_delta(short_tickers,'C',cfg.target_call_delta).contract.strike
        put_strike = find_option_closest_to_delta(short_tickers,'P',cfg.target_put_delta).contract.strike

        #
        trade = submit_double_calendar(
            symbol=symbol,put_strike=put_strike,call_strike=call_strike,exchange=und_exchange,und_price=current_mid,
            quantity=cfg.quantity,short_expiry_date=short_expiry_date,long_expiry_date=long_expiry_date,is_live=True)
        print(trade)

    except Exception as e:
        logger.exception(f"Error during trade submission: {e}")

if __name__ == "__main__":
    main()