import logging
from ibstrat.qualify import qualify_contract
from ibstrat.orders import create_bag, submit_limit_order, adjustOrders, submit_order_at_time, wait_for_order_fill
from ibstrat.adaptive import submit_adaptive_order
from ibstrat.positions import check_positions
from ibstrat.market_data import get_combo_prices
from ibstrat.ticksize import get_tick_size, adjust_to_tick_size
import cfg
from ib_async import Order, Contract
from ib_insync import ib

logger = logging.getLogger('DC')

def submit_double_calendar(und_contract,
                           short_put_strike: float, short_call_strike: float,
                           long_put_strike: float, long_call_strike: float,
                           short_put_expiry_date: str, long_put_expiry_date: str,
                           short_call_expiry_date: str, long_call_expiry_date: str,
                           is_live: bool,
                           strategy_params: dict):
    print(f"submit_double_calendar, params are: {strategy_params}")
    try:
        # Extract parameters from the strategy configuration
        opt_exchange = strategy_params["opt_exchange"]
        quantity = strategy_params["quantity"]
        strategy_tag = strategy_params["strategy_tag"]
        trading_class = strategy_params.get("trading_class")
        submit_auto_close = strategy_params.get("submit_auto_close")

        print(f"Preparing Double Calendar Spread for {und_contract.symbol} with strategy {strategy_tag}")
        print(f"  Short Call Strike: {short_call_strike}, Short Put Strike: {short_put_strike}")
        print(f"  Long Call Strike: {long_call_strike}, Long Put Strike: {long_put_strike}")
        print(f"  Short Put Expiry: {short_put_expiry_date}, Long Put Expiry: {long_put_expiry_date}")
        print(f"  Short Call Expiry: {short_call_expiry_date}, Long Call Expiry: {long_call_expiry_date}")
        print(f"  Exchange: {opt_exchange}, Quantity: {quantity}")

        # Check existing positions
        pos_check_list = [
            {'strike': short_put_strike, 'right': 'P', 'expiry': short_put_expiry_date, 'position_type': 'long'},
            {'strike': short_call_strike, 'right': 'C', 'expiry': short_call_expiry_date, 'position_type': 'long'},
            {'strike': long_put_strike, 'right': 'P', 'expiry': long_put_expiry_date, 'position_type': 'short'},
            {'strike': long_call_strike, 'right': 'C', 'expiry': long_call_expiry_date, 'position_type': 'short'},
        ]
        if check_positions(und_contract.symbol, pos_check_list):
            logger.warning(f"Collisions detected on strikes, aborting trade.")
            return None

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=long_call_strike,
                             lastTradeDateOrContractMonth=long_call_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=trading_class),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=short_call_strike,
                             lastTradeDateOrContractMonth=short_call_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=trading_class),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=long_put_strike,
                             lastTradeDateOrContractMonth=long_put_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=trading_class),
            qualify_contract(symbol=und_contract.symbol, secType='FOP' if und_contract.secType == 'FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=short_put_strike,
                             lastTradeDateOrContractMonth=short_put_expiry_date, multiplier=und_contract.multiplier,
                             tradingClass=trading_class),
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
            logger.info(f"Submitting adaptive order for {und_contract.symbol}")
            trade = submit_adaptive_order(
                order_contract=bag_contract,
                order_type='MKT',
                action='BUY',
                is_live=is_live,
                quantity=quantity,
                order_ref=strategy_tag,
                adaptive_priority=cfg.adaptive_priority
            )
            if trade and submit_auto_close and False: # temp patch, this timecondition doesn;t work as expected
                if wait_for_order_fill(trade.order.orderId,60):
                    #submit close order
                    time_condition = f"{short_put_expiry_date} {cfg.dcal_close_time}"
                    logger.info(f"Submitting auto close order with time condition {time_condition}")
                    auto_close_trade = submit_order_at_time(
                        order_contract=bag_contract,
                        limit_price=None,
                        order_type='MKT',
                        action='SELL',
                        is_live=True,
                        quantity=quantity,
                        order_ref=strategy_tag,
                        time_condition=time_condition
                    )
                    logger.debug(f"Submitted auto close order, status is {auto_close_trade}")
        else:
            # Get combo prices for futures
            bid, mid, ask = get_combo_prices([(legs[i], leg_actions[i], ratios[i]) for i in range(len(legs))])
            logger.info(f"Combo prices: Bid: {bid}, Mid: {mid}, Ask: {ask}")

            # Submit a limit order using the mid price less 1 tick
            contract_tick = get_tick_size(und_contract.symbol, mid)
            order_limit_price = adjust_to_tick_size(mid, contract_tick) - contract_tick
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

