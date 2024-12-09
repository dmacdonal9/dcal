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

def submit_double_calendar(symbol: str, put_strike: float, call_strike: float, exchange,
                           und_price: float, quantity: int,
                           short_expiry_date: str, long_expiry_date: str, is_live: bool = False):
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

        # Qualify the underlying contract
        und_contract = qualify_contract(
            symbol=symbol,
            secType='IND',
            exchange=exchange,
            currency='USD'
        )

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=symbol, secType='OPT', exchange=exchange, right=CALL, strike=call_strike, lastTradeDateOrContractMonth=long_expiry_date),
            qualify_contract(symbol=symbol, secType='OPT', exchange=exchange, right=CALL, strike=call_strike, lastTradeDateOrContractMonth=short_expiry_date),
            qualify_contract(symbol=symbol, secType='OPT', exchange=exchange, right=PUT, strike=put_strike, lastTradeDateOrContractMonth=long_expiry_date),
            qualify_contract(symbol=symbol, secType='OPT', exchange=exchange, right=PUT, strike=put_strike, lastTradeDateOrContractMonth=short_expiry_date),
        ]

        # Define actions and ratios for the legs
        leg_actions = ['BUY', 'SELL', 'BUY', 'SELL']
        ratios = [quantity] * 4

        # Create the combo bag contract
        bag_contract = create_bag(und_contract, legs, leg_actions, ratios)
        bag_contract.exchange = 'SMART'

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