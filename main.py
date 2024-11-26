import logging
from dcal import submit_double_calendar
from market_data import get_current_mid_price
from qualify import qualify_contract
import cfg
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DoubleCalendarMain')

def calculate_expiry_date(days_from_today: int):
    """
    Calculate the expiry date based on the number of days from today.
    Args:
        days_from_today: Number of days from today for the expiry.
    Returns:
        Expiry date in 'YYYYMMDD' format.
    """
    expiry_date = datetime.now() + timedelta(days=days_from_today)
    return expiry_date.strftime('%Y%m%d')

def main():
    # Configuration for the double calendar trade
    symbol = 'SPX'  # Replace with your symbol
    percentage_offset = 2.5  # Percentage offset for short strikes
    short_expiry_days = 5  # Days to expiry for the short legs
    long_expiry_days = 21  # Days to expiry for the long legs
    is_live = False # Set from configuration

    logger.info("Starting Double Calendar Trade Submission")

    try:
        # Qualify the underlying contract
        und_contract = qualify_contract(
            symbol=symbol,
            secType='IND',
            exchange='SMART',
            currency='USD'
        )

        # Fetch the current market mid-price
        current_mid = get_current_mid_price(und_contract)
        logger.info(f"Current market price for {symbol}: {current_mid}")

        # Calculate expiry dates
        short_expiry = calculate_expiry_date(short_expiry_days)
        long_expiry = calculate_expiry_date(long_expiry_days)

        # Calculate strike distances based on percentage offset
        short_call_strike_distance = current_mid * (percentage_offset / 100)
        short_put_strike_distance = current_mid * (percentage_offset / 100)

        # Call the function to submit a double calendar spread
        trade = submit_double_calendar(
            symbol=symbol,
            long_strike_distance=short_call_strike_distance,
            short_strike_distance=short_put_strike_distance,
            short_expiry=short_expiry,
            long_expiry=long_expiry,
            is_live=is_live
        )

        if trade:
            logger.info(f"Trade submitted successfully: {trade}")
        else:
            logger.error("Trade submission failed.")
    except Exception as e:
        logger.exception(f"Error during trade submission: {e}")

if __name__ == "__main__":
    main()