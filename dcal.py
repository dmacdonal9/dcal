import logging
from qualify import qualify_contract, get_front_month_contract_date
from dteutil import calculate_expiry_date
from orders import submit_adaptive_order, create_bag
from ib_insync import TimeCondition, Order, Contract, ComboLeg, TagValue
import cfg
from ib_instance import ib
import pytz
from datetime import datetime, timedelta


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('DoubleCalendar')


def get_symbol_params(symbol: str, strategy_type: str):
    """
    Retrieve the configuration parameters for the given symbol from cfg.py based on the strategy type.

    Args:
        symbol (str): The symbol to look up (e.g., 'SPX', 'NDX', 'RUT').
        strategy_type (str): The type of strategy ('daily' or 'weekly').

    Returns:
        dict: The configuration parameters for the symbol.
    """
    if strategy_type == 'daily':
        params = cfg.daily_dc_params.get(symbol)
    elif strategy_type == 'weekly':
        params = cfg.weekly_dc_params.get(symbol)
    else:
        raise ValueError(f"Invalid strategy_type: {strategy_type}. Must be 'daily' or 'weekly'.")

    if not params:
        raise ValueError(f"Configuration parameters for symbol {symbol} not found in {strategy_type}_dc_params.")

    return params


def submit_double_calendar(symbol: str,
                           short_put_strike: float, short_call_strike: float,
                           long_put_strike: float, long_call_strike: float,
                           short_expiry_date: str, long_expiry_date: str,
                           strategy_type: str, is_live: bool = False):
    """
    Submits an order for a Double Calendar Spread.

    Args:
        symbol: The underlying symbol to trade.
        put_strike: Strike price for the put options.
        call_strike: Strike price for the call options.
        short_expiry_date: Expiry date for the short legs (YYYYMMDD).
        long_expiry_date: Expiry date for the long legs (YYYYMMDD).
        strategy_type: The type of strategy ('daily' or 'weekly').
        is_live: Whether to place a live order or a paper trade.

    Returns:
        A Trade object for the submitted order, or None if the order submission fails.
    """
    try:
        # Retrieve parameters for the symbol and strategy
        params = get_symbol_params(symbol, strategy_type)
        exchange = params["exchange"]
        opt_exchange = params["opt_exchange"]
        quantity = params["quantity"]

        print(f"Preparing Double Calendar Spread for {symbol} ({strategy_type.upper()} strategy):")
        print(f"  Short Call Strike: {short_call_strike}, Short Put Strike: {short_put_strike}")
        print(f"  Long Call Strike: {long_call_strike}, Long Put Strike: {long_put_strike}")
        print(f"  Short Expiry: {short_expiry_date}, Long Expiry: {long_expiry_date}")
        print(f"  Exchange: {opt_exchange}, Quantity: {quantity}")

        if params["sec_type"] == 'FUT':
            fut_date = get_front_month_contract_date(symbol, params["exchange"], params["mult"],
                                                     calculate_expiry_date(params["short_expiry_days"]))
        else:
            fut_date=''

        # Qualify the underlying contract
        und_contract = qualify_contract(
            symbol=symbol,
            secType=params["sec_type"],
            lastTradeDateOrContractMonth=fut_date,
            exchange=exchange,
            currency='USD'
        )

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT', exchange=opt_exchange, right='C', strike=long_call_strike,
                             lastTradeDateOrContractMonth=long_expiry_date,multiplier=und_contract.multiplier),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT', exchange=opt_exchange, right='C', strike=short_call_strike,
                             lastTradeDateOrContractMonth=short_expiry_date,multiplier=und_contract.multiplier),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT', exchange=opt_exchange, right='P', strike=long_put_strike,
                             lastTradeDateOrContractMonth=long_expiry_date,multiplier=und_contract.multiplier),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT', exchange=opt_exchange, right='P', strike=short_put_strike,
                             lastTradeDateOrContractMonth=short_expiry_date,multiplier=und_contract.multiplier),
        ]

        # Define actions and ratios for the legs
        leg_actions = ['BUY', 'SELL', 'BUY', 'SELL']
        ratios = [quantity] * 4

        # Create the combo bag contract
        bag_contract = create_bag(und_contract, legs, leg_actions, ratios)
        bag_contract.exchange = 'SMART'

        logger.info(f"Combo contract created for {symbol}:")
        logger.info(f"  Legs: {len(legs)}")

        # Submit an adaptive market order for the combo
        trade = submit_adaptive_order(
            order_contract=bag_contract,
            order_type='MKT',
            action='BUY',
            is_live=is_live,
            quantity=quantity
        )

        if not trade:
            logger.error(f"Failed to submit Double Calendar order for {symbol}.")
            return None

        logger.info(f"Double Calendar Spread submitted successfully. Order ID: {trade.order.orderId}")
        return trade

    except Exception as e:
        logger.exception(f"Error submitting Double Calendar Spread order for {symbol}: {e}")
        return None

def close_dcal(symbol):
    """
    Close a double calendar (DCAL) position for a given symbol with an adaptive market order
    at a specified time (adjusted for the exchange timezone).

    Args:
        symbol (str): The symbol of the instrument to close (e.g., 'SPX').
        closing_time (str): The time to close the position (e.g., '09:34:00').
    """
    print(f"close_dcal(): {symbol}")

    # Fetch open positions and filter legs matching the symbol
    positions = ib.positions()
    legs = []

    for pos in positions:
        if pos.contract.symbol == symbol and pos.position != 0:
            ib.qualifyContracts(pos.contract)
            legs.append(
                ComboLeg(
                    conId=pos.contract.conId,
                    ratio=abs(int(pos.position)),
                    action='SELL' if pos.position < 0 else 'BUY',
                    exchange=pos.contract.exchange,
                    openClose=1
                )
            )

    if not legs:
        print(f"No open position legs found for symbol: {symbol}")
        return

    # Define the combo contract
    combo_contract = Contract(
        symbol=symbol,
        secType='BAG',
        exchange='SMART',
        currency='USD',
        comboLegs=legs
    )

    # Create the adaptive market order
    close_order = Order(
        orderRef=cfg.myStrategyTag,
        action='SELL',
        orderType='MKT',
        totalQuantity=1,
        algoStrategy='Adaptive',
        algoParams=[TagValue(tag='adaptivePriority', value='Normal')]
    )

    close_order.conditionsIgnoreRth = False

    print(f"Combo Contract: {combo_contract}")
    print(f"Close Order: {close_order}")

    # Submit the order
    trade = ib.placeOrder(combo_contract, close_order)
    ib.sleep(2)

    print(f"Submitted close order for {symbol}")
    print(trade.orderStatus)
