import logging
from market_data import get_current_mid_price
from options import get_closest_strike
from qualify import qualify_contract
from orders import submit_adaptive_order, create_bag
import cfg

# Constants
PUT = 'P'
CALL = 'C'

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DoubleCalendar')
logging.getLogger('ib_insync').setLevel(logging.ERROR)

def submit_double_calendar(symbol: str, long_strike_distance: float, short_strike_distance: float,
                           short_expiry_days: int, long_expiry_days: int, is_live: bool = False):
    """
    Submits an order for a Double Calendar Spread.

    Args:
        symbol: The underlying symbol to trade.
        long_strike_distance: Distance from the underlying price for the long strike.
        short_strike_distance: Distance for the short strike.
        short_expiry_days: Days to expiry for the short legs.
        long_expiry_days: Days to expiry for the long legs.
        is_live: Whether to place a live order or a paper trade.

    Returns:
        A Trade object for the submitted order, or None if the order submission fails.
    """
    try:
        quantity = cfg.dc_param[symbol]['quantity']
        exchange = cfg.dc_param[symbol]['exchange']
        opt_exchange = cfg.dc_param[symbol]['opt_exchange']

        # Qualify the underlying contract
        und_contract = qualify_contract(
            symbol=symbol,
            secType='IND',
            exchange=exchange,
            currency='USD'
        )

        # Fetch the current market mid-price
        current_mid = get_current_mid_price(und_contract)

        # Determine strike prices
        short_call_strike = get_closest_strike(und_contract, CALL, opt_exchange, short_expiry_days, current_mid + short_strike_distance)
        short_put_strike = get_closest_strike(und_contract, PUT, opt_exchange, short_expiry_days, current_mid - short_strike_distance)
        long_call_strike = get_closest_strike(und_contract, CALL, opt_exchange, long_expiry_days, current_mid + long_strike_distance)
        long_put_strike = get_closest_strike(und_contract, PUT, opt_exchange, long_expiry_days, current_mid - long_strike_distance)

        if not (short_call_strike and short_put_strike and long_call_strike and long_put_strike):
            logger.error("Failed to fetch valid strikes for Double Calendar.")
            return None

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=symbol, secType='OPT', exchange='CBOE', right=CALL, strike=long_call_strike, lastTradeDateOrContractMonth=long_expiry_days),
            qualify_contract(symbol=symbol, secType='OPT', exchange='CBOE', right=CALL, strike=short_call_strike, lastTradeDateOrContractMonth=short_expiry_days),
            qualify_contract(symbol=symbol, secType='OPT', exchange='CBOE', right=PUT, strike=long_put_strike, lastTradeDateOrContractMonth=long_expiry_days),
            qualify_contract(symbol=symbol, secType='OPT', exchange='CBOE', right=PUT, strike=short_put_strike, lastTradeDateOrContractMonth=short_expiry_days),
        ]

        # Define actions and ratios for the legs
        leg_actions = ['BUY', 'SELL', 'BUY', 'SELL']
        ratios = [quantity] * 4

        # Create the combo bag contract
        bag_contract = create_bag(und_contract, legs, leg_actions, ratios)

        # Submit an adaptive market order for the combo
        trade = submit_adaptive_order(
            order_contract=bag_contract,
            order_type='MKT',
            action='BUY',
            is_live=is_live,
            quantity=quantity
        )

        if not trade:
            logger.error("Failed to submit Double Calendar order.")
            return None

        logger.info(f"Double Calendar Spread submitted successfully. Order ID: {trade.order.orderId}")
        return trade

    except Exception as e:
        logger.exception(f"Error submitting Double Calendar Spread order: {e}")
        return None