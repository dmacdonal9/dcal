import logging
from dcal import submit_double_calendar
from ib_insync import Contract
from market_data import get_current_mid_price
import cfg
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
from ib_instance import ib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("DoubleCalendarMain")

# Define the CBOE market calendar
cboe_calendar = mcal.get_calendar("CBOE_Index_Options")

def calculate_valid_expiry_date(days_from_today: int) -> str:
    """
    Calculate the next valid expiry date based on the number of days from today.

    Args:
        days_from_today: Number of days from today for the initial expiry.

    Returns:
        Valid expiry date in 'YYYYMMDD' format.
    """
    target_date = datetime.now().date() + timedelta(days=days_from_today)

    # Get valid trading days within the range
    schedule = cboe_calendar.schedule(
        start_date=target_date.strftime("%Y-%m-%d"),
        end_date=(target_date + timedelta(days=30)).strftime("%Y-%m-%d"),
    )
    valid_dates = schedule.index.to_pydatetime()

    # Find the next valid trading day
    for valid_date in valid_dates:
        if valid_date.date() >= target_date:
            return valid_date.strftime("%Y%m%d")

    raise ValueError("No valid expiry date found in the specified range.")

def process_symbol(symbol: str):
    """
    Process a single symbol to calculate expiry dates, fetch market data,
    and submit the double calendar trade.
    """
    logger.info(f"Processing symbol: {symbol}")

    # Check if symbol configuration exists
    params = cfg.dc_param.get(symbol)
    if not params:
        logger.error(f"Configuration for symbol {symbol} not found. Skipping.")
        return

    try:
        # Calculate expiry dates
        short_expiry = calculate_valid_expiry_date(params["short_expiry_days"])
        long_expiry = calculate_valid_expiry_date(params["long_expiry_days"])

        # Create contract object
        contract = Contract(
            conId=params["conid"],
            exchange=params.get("exchange", ""),  # Default to empty string for auto-inference
            currency="USD",
            secType=params.get("secType", "IND"),  # Default to "IND"
        )

        # Fetch current mid-price
        current_mid = get_current_mid_price(contract)
        if not current_mid:
            raise ValueError(f"Failed to retrieve market price for {symbol}")
        logger.info(f"Current market price for {symbol}: {current_mid}")

        # Request option chain
        logger.info(f"Requesting option chain for {symbol} with conId={params['conid']}")
        tickers = ib.reqSecDefOptParams(symbol, '', contract.secType, contract.conId)
        print(tickers)
        if not tickers:
            logger.warning(f"No tickers returned for {symbol}. Skipping.")
            return
        logger.info(f"Received {len(tickers)} tickers for {symbol}")

        # Submit the double calendar trade
        submit_double_calendar(
            ib=ib,
            symbol=symbol,
            short_delta=params["short_delta"],
            long_delta=params["long_delta"],
            short_expiry=short_expiry,
            long_expiry=long_expiry,
            tickers=tickers,
            is_live=params["live_order"],
        )
        logger.info(f"Trade submitted successfully for {symbol}.")
    except ValueError as e:
        logger.error(f"Validation error for symbol {symbol}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during trade submission for symbol {symbol}")

def main():
    """
    Main function to process trades for all symbols in the configuration.
    """
    for symbol in cfg.symbol_list:
        process_symbol(symbol)

if __name__ == "__main__":
    main()