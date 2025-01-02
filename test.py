
from ibstrat.orders import create_bag
from ibstrat.ib_instance import ib
import logging

from ibstrat.qualify import qualify_contract


def check_for_dcal(symbol: str):
    """
    Searches through open positions for a Double Calendar Spread (4 legs: short call, short put, long call, long put)
    with differing expiry dates for the shorts and longs. Returns a bag contract if found.

    :param symbol: The underlying symbol to search for.
    :return: Bag contract with all 4 legs if found, None otherwise.
    """

    try:
        positions = ib.positions()
        double_calendar_legs = []

        for pos in positions:
            if pos.contract.symbol == symbol and pos.contract.secType in {'OPT', 'FOP'}:
                # Collect relevant contract details
                contract = pos.contract
                expiry = contract.lastTradeDateOrContractMonth
                strike = contract.strike
                right = contract.right
                position = pos.position

                # Classify legs based on criteria
                leg = {
                    "contract": contract,
                    "expiry": expiry,
                    "strike": strike,
                    "right": right,
                    "position": position
                }
                double_calendar_legs.append(leg)

        # Filter to ensure we have exactly 4 legs
        if len(double_calendar_legs) < 4:
            return None

        # Group by expiry date and option type
        call_legs = [leg for leg in double_calendar_legs if leg["right"] == 'C']
        put_legs = [leg for leg in double_calendar_legs if leg["right"] == 'P']

        if len(call_legs) != 2 or len(put_legs) != 2:
            return None

        # Ensure shorts and longs have different expiry dates
        short_calls = [leg for leg in call_legs if leg["position"] < 0]
        long_calls = [leg for leg in call_legs if leg["position"] > 0]
        short_puts = [leg for leg in put_legs if leg["position"] < 0]
        long_puts = [leg for leg in put_legs if leg["position"] > 0]

        if len(short_calls) != 1 or len(long_calls) != 1 or len(short_puts) != 1 or len(long_puts) != 1:
            return None

        if short_calls[0]["expiry"] == long_calls[0]["expiry"] or short_puts[0]["expiry"] == long_puts[0]["expiry"]:
            return None

        # qualify the underlying
        und_contract = qualify_contract(
            symbol=symbol,
            secType='FUT' if short_calls[0]["contract"].secType == 'FOP' else 'IND',
            exchange=short_calls[0]["contract"].exchange,
            lastTradeDateOrContractMonth=short_calls[0]["expiry"],
            multiplier=short_calls[0]["contract"].multiplier,
            tradingClass=short_calls[0]["contract"].tradingClass)

        # Create a bag contract for the Double Calendar Spread
        legs = [
            {"action": "SELL", "contract": short_calls[0]["contract"]},
            {"action": "BUY", "contract": long_calls[0]["contract"]},
            {"action": "SELL", "contract": short_puts[0]["contract"]},
            {"action": "BUY", "contract": long_puts[0]["contract"]},
        ]
        bag_contract = create_bag(und_contract=und_contract, legs=legs)

        return bag_contract

    except Exception as e:
        logging.exception(f"Error checking for Double Calendar Spread: {e}")
        return None

    finally:
        ib.disconnect()
