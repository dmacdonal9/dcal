import logging
from market_data import get_current_mid_price
from options import get_closest_strike
from qualify import qualify_contract
from orders import submit_adaptive_order, create_bag
import cfg
from ib_insync import *
from ib_instance import ib

# Constants
PUT = 'P'
CALL = 'C'

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger('DoubleCalendar')
logging.getLogger('ib_insync').setLevel(logging.WARN)

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


def close_dcal(symbol, closing_date_time):
    """
    Close a double calendar (DCAL) position for a given symbol with an adaptive market order
    at a specified time (e.g., 9:35 AM next trading day).

    Args:
        symbol (str): The symbol of the instrument to close (e.g., 'SPX').
        closing_date_time (str): The time to close the position (e.g., '20241210 08:30:00' in YYYYMMDD HH:MM:SS format).
    """

    # Fetch open positions and filter legs matching the symbol
    positions = ib.positions()
    legs = []

    for pos in positions:
        if pos.contract.symbol == symbol:
            details = ib.reqContractDetails(pos.contract)
            print(details)

    for pos in positions:
        if pos.contract.symbol == symbol and pos.position != 0:
            # Ensure legs are fully qualified
            ib.qualifyContracts(pos.contract)
            legs.append(
                ComboLeg(
                    conId=pos.contract.conId,
                    ratio=abs(int(pos.position)),  # Convert position to integer ratio
                    action='SELL' if pos.position < 0 else 'BUY',  # Reverse action to close
                    exchange=pos.contract.exchange,
                    openClose=1
                )
            )

    if not legs:
        raise ValueError(f"No open position legs found for symbol: {symbol}")

    for leg in legs:
        print(
            f"Leg details: conId={leg.conId}, action={leg.action}, ratio={leg.ratio}, exchange={leg.exchange}, openClose={leg.openClose}")

    # Create the BAG combo contract
    combo_contract = Contract(
        symbol=symbol,
        secType='BAG',
        exchange='SMART',
        currency='USD',
        comboLegs=legs
    )

    # validate BAG
    #contract_details = ib.reqContractDetails(combo_contract)
    #print(contract_details)

    # Create the adaptive market order
    close_order = Order(
        action='SELL',  # Adaptive market order to close the position
        orderType='MKT',
        totalQuantity=1,  # Quantity for combo orders is typically 1 (not per leg)
        algoStrategy='Adaptive',
        algoParams=[
            TagValue(tag='adaptivePriority', value='Normal')  # Adjust to 'Patient' or 'Urgent' as needed
        ]
    )

    # Attach a time condition
    time_condition = TimeCondition(
        isMore=True,  # Order activates after the specified time
        time=closing_date_time  # Time in 'YYYYMMDD HH:MM:SS' format
    )
    close_order.conditions.append(time_condition)
    close_order.conditionsIgnoreRth = False  # Respect regular trading hours

    print(f"Combo Contract: {combo_contract}")
    print(f"Close Order: {close_order}")

    # Submit the order
    trade = ib.placeOrder(combo_contract, close_order)
    ib.sleep(2)

    print(f"Submitted close order for {symbol} with time condition: {closing_date_time}")
    print(trade.orderStatus)
