import logging
from options import find_option_closest_to_delta

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DoubleCalendar')


def submit_double_calendar(ib, symbol, short_delta, long_delta, short_expiry, long_expiry, tickers, is_live):
    """
    Submit a double calendar spread order for a given symbol.

    Args:
        ib: The IB connection object.
        symbol: The underlying symbol for the options.
        short_delta: Target delta for the short options.
        long_delta: Target delta for the long options.
        short_expiry: Expiry date for the short options (in 'YYYYMMDD' format).
        long_expiry: Expiry date for the long options (in 'YYYYMMDD' format).
        tickers: List of option tickers retrieved from IBKR.
        is_live: Whether the order should be submitted as a live order.

    Returns:
        The trade order object if successful, None otherwise.
    """
    try:
        logger.info(f"Finding options for {symbol} with deltas {short_delta} (short) and {long_delta} (long)")

        # Extract tickers with matching expiry dates
        def filter_by_expiry(tickers, target_expiry):
            logger.info(f"Filtering tickers for expiry {target_expiry}")
            filtered_tickers = [
                t for t in tickers if hasattr(t, "contract") and
                                      t.contract.lastTradeDateOrContractMonth.replace("-", "") == target_expiry
            ]
            if not filtered_tickers:
                logger.warning(f"No tickers matched expiry {target_expiry}. Available expiries: "
                               f"{set(t.contract.lastTradeDateOrContractMonth for t in tickers if hasattr(t, 'contract'))}")
            return filtered_tickers

        short_tickers = filter_by_expiry(tickers, short_expiry)
        long_tickers = filter_by_expiry(tickers, long_expiry)

        if not short_tickers:
            logger.error(f"No tickers found for short expiry {short_expiry} for {symbol}")
            return None
        if not long_tickers:
            logger.error(f"No tickers found for long expiry {long_expiry} for {symbol}")
            return None

        # Find the short call and put options
        call_short = find_option_closest_to_delta(short_tickers, "C", short_delta)
        put_short = find_option_closest_to_delta(short_tickers, "P", short_delta)

        # Find the long call and put options
        call_long = find_option_closest_to_delta(long_tickers, "C", long_delta)
        put_long = find_option_closest_to_delta(long_tickers, "P", long_delta)

        logger.info(f"Short call: {call_short.contract}")
        logger.info(f"Short put: {put_short.contract}")
        logger.info(f"Long call: {call_long.contract}")
        logger.info(f"Long put: {put_long.contract}")

        # Construct the combo orders for the calendar spreads
        short_call_order = ib.createOrder("SELL", "LMT", 1, limitPrice=call_short.marketPrice())
        long_call_order = ib.createOrder("BUY", "LMT", 1, limitPrice=call_long.marketPrice())
        short_put_order = ib.createOrder("SELL", "LMT", 1, limitPrice=put_short.marketPrice())
        long_put_order = ib.createOrder("BUY", "LMT", 1, limitPrice=put_long.marketPrice())

        # Submit the orders for the double calendar spread
        if is_live:
            ib.placeOrder(call_short.contract, short_call_order)
            ib.placeOrder(call_long.contract, long_call_order)
            ib.placeOrder(put_short.contract, short_put_order)
            ib.placeOrder(put_long.contract, long_put_order)

            logger.info(f"Double Calendar Spread orders submitted successfully for {symbol}")
        else:
            logger.info(f"Simulated orders (not live):\n"
                        f"Short Call: {short_call_order}\n"
                        f"Long Call: {long_call_order}\n"
                        f"Short Put: {short_put_order}\n"
                        f"Long Put: {long_put_order}")

        return {
            "short_call": short_call_order,
            "long_call": long_call_order,
            "short_put": short_put_order,
            "long_put": long_put_order,
        }

    except Exception as e:
        logger.exception(f"Error submitting Double Calendar Spread order for {symbol}: {e}")
        return None