import logging
from ibstrat.qualify import qualify_contract, get_front_month_contract_date
from ibstrat.dteutil import calculate_expiry_date
from ibstrat.orders import create_bag
from ibstrat.adaptive import submit_adaptive_order
import cfg


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('DoubleCalendar')


def get_symbol_params(symbol: str):

    params = cfg.fri_dc_params.get(symbol)

    if not params:
        raise ValueError(f"Configuration parameters for symbol {symbol} not found in cfg")

    return params


def submit_double_calendar(symbol: str,
                           short_put_strike: float, short_call_strike: float,
                           long_put_strike: float, long_call_strike: float,
                           short_put_expiry_date: str, long_put_expiry_date: str,
                           short_call_expiry_date: str, long_call_expiry_date: str,
                           is_live: bool = False):

    try:
        # Retrieve parameters for the symbol and strategy
        params = get_symbol_params(symbol)
        exchange = params["exchange"]
        opt_exchange = params["opt_exchange"]
        quantity = params["quantity"]

        print(f"Preparing Double Calendar Spread for {symbol} ")
        print(f"  Short Call Strike: {short_call_strike}, Short Put Strike: {short_put_strike}")
        print(f"  Long Call Strike: {long_call_strike}, Long Put Strike: {long_put_strike}")
        print(f"  Short Put Expiry: {short_put_expiry_date}, Long Put Expiry: {long_put_expiry_date}")
        print(f"  Short Call Expiry: {short_call_expiry_date}, Long Call Expiry: {long_call_expiry_date}")
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
            currency='USD',
            tradingClass=params['trading_class']
        )

        # Qualify contracts for each leg
        legs = [
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=long_call_strike,
                             lastTradeDateOrContractMonth=long_call_expiry_date,multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT',
                             exchange=opt_exchange, right='C', strike=short_call_strike,
                             lastTradeDateOrContractMonth=short_call_expiry_date,multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=long_put_strike,
                             lastTradeDateOrContractMonth=long_put_expiry_date,multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
            qualify_contract(symbol=symbol, secType='FOP' if und_contract.secType=='FUT' else 'OPT',
                             exchange=opt_exchange, right='P', strike=short_put_strike,
                             lastTradeDateOrContractMonth=short_put_expiry_date,multiplier=und_contract.multiplier,
                             tradingClass=params['trading_class']),
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
            quantity=quantity,
            order_ref=cfg.weekly_dcal_tag
        )

        if not trade:
            logger.error(f"Failed to submit Double Calendar order for {symbol}.")
            return None

        logger.info(f"Double Calendar Spread submitted successfully. Order ID: {trade.order.orderId}")
        return trade

    except Exception as e:
        logger.exception(f"Error submitting Double Calendar Spread order for {symbol}: {e}")
        return None
