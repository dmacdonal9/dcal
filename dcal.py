import logging
from ibstrat.qualify import qualify_contract
from ibstrat.orders import create_bag, submit_limit_order, adjustOrders
from ibstrat.adaptive import submit_adaptive_order
from ibstrat.market_data import get_combo_prices
from ibstrat.ticksize import get_tick_size, adjust_to_tick_size
import cfg

logger = logging.getLogger('DoubleCalendar')


def get_symbol_params(symbol: str, strategy: str='fri'):

    if strategy == 'fri':
        params = cfg.fri_dc_params.get(symbol)
    else:
        params = cfg.mon_dc_params.get(symbol)

    if not params:
        raise ValueError(f"Configuration parameters for symbol {symbol} not found in cfg")

    return params


def submit_double_calendar(und_contract,
                           short_put_strike: float, short_call_strike: float,
                           long_put_strike: float, long_call_strike: float,
                           short_put_expiry_date: str, long_put_expiry_date: str,
                           short_call_expiry_date: str, long_call_expiry_date: str,
                           is_live: bool = False,
                           strategy: str = 'fri'):
    try:
        # Retrieve parameters for the strategy
        params = get_symbol_params(und_contract.symbol, strategy=strategy)
        opt_exchange = params["opt_exchange"]
        quantity = params["quantity"]
        strategy_tag = params["strategy_tag"]

        print(f"Preparing Double Calendar Spread for {und_contract.symbol}")
        print(f"  Short Call Strike: {short_call_strike}, Short Put Strike: {short_put_strike}")
        print(f"  Long Call Strike: {long_call_strike}, Long Put Strike: {long_put_strike}")
        print(f"  Short Put Expiry: {short_put_expiry_date}, Long Put Expiry: {long_put_expiry_date}")
        print(f"  Short Call Expiry: {short_call_expiry_date}, Long Call Expiry: {long_call_expiry_date}")
        print(f"  Exchange: {opt_exchange}, Quantity: {quantity}")

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=long_call_strike,
                             lastTradeDateOrContractMonth=long_call_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=short_call_strike,
                             lastTradeDateOrContractMonth=short_call_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=long_put_strike,
                             lastTradeDateOrContractMonth=long_put_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=short_put_strike,
                             lastTradeDateOrContractMonth=short_put_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
        ]

        # Define actions and ratios for the legs
        leg_actions = ['BUY', 'SELL', 'BUY', 'SELL']
        ratios = [quantity] * 4

        # Create the combo bag contract
        bag_contract = create_bag(und_contract, legs, leg_actions, ratios)
        bag_contract.exchange = 'SMART'

        logger.info(f"Combo contract created for {und_contract.symbol} with {len(legs)} legs.")

        # Handle futures and options differently
        if und_contract.secType != 'FUT':
            # Submit an adaptive market order for non-futures
            trade = submit_adaptive_order(
                order_contract=bag_contract,
                order_type='MKT',
                action='BUY',
                is_live=is_live,
                quantity=quantity,
                order_ref=strategy_tag
            )
        else:
            # Get combo prices for futures
            bid, mid, ask = get_combo_prices([(legs[i], leg_actions[i], ratios[i]) for i in range(len(legs))])
            logger.info(f"Combo prices: Bid: {bid}, Mid: {mid}, Ask: {ask}")

            # Submit a limit order using the mid price less 1 tick
            contract_tick = get_tick_size(und_contract.symbol, mid)
            order_limit_price = adjust_to_tick_size(mid,contract_tick) - contract_tick
            logger.debug(f"Limit order price adjusted from {mid} to {order_limit_price} for {und_contract.symbol}")
            trade = submit_limit_order(
                order_contract=bag_contract,
                limit_price=order_limit_price,
                action='BUY',
                is_live=is_live,
                quantity=quantity,
                strategy_tag=strategy_tag
            )

            # Adjust orders if necessary
            adjustOrders([bag_contract.symbol])

        # Handle trade submission results
        if not trade:
            logger.error(f"Failed to submit Double Calendar order for {und_contract.symbol}.")
            return None

        logger.info(f"Double Calendar Spread submitted successfully. Order ID: {trade.order.orderId}")
        return trade

    except Exception as e:
        logger.exception(f"Error submitting Double Calendar Spread order for {und_contract.symbol}: {e}")
        return None