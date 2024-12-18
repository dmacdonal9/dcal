from ib_insync import LimitOrder, Order, TagValue, ComboLeg, Contract
from ib_instance import ib
from datetime import datetime, timedelta, timezone
from typing import Optional
import cfg
import mintick

def get_min_tick(symbol: str, price: float) -> Optional[float]:
    """
    Retrieve the minimum tick size for a given symbol and price from mintick.py.

    Args:
        symbol: The symbol of the instrument (e.g., 'ES', 'SPX').
        price: The price of the instrument.

    Returns:
        The minimum tick size for the given symbol and price, or None if not found.
    """
    thresholds = mintick.min_tick_data.get(symbol, {}).get("thresholds", [])
    for threshold in thresholds:
        if price <= threshold["max_price"]:
            return threshold["tick_size"]
    return None


def show_recently_filled_spreads(timeframe='today', strategy=''):
    """
    Retrieve recently filled orders and display spread details, using the combo summary for the net fill price.
    """
    if not ib:
        print(f"Error: No IB instance connected.")
        return []

    try:
        executions = ib.reqExecutions()
        current_utc_time = datetime.now(timezone.utc)

        if timeframe == 'today':
            start_time = current_utc_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timeframe == 'yesterday':
            start_time = (current_utc_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            try:
                start_time = datetime.strptime(timeframe, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                print("Error: Invalid date format. Use 'today', 'yesterday', or 'YYYY-MM-DD'.")
                return []

        end_time = start_time + timedelta(days=1)

        # Filter executions by timestamp
        filtered_executions = [
            fill for fill in executions if start_time <= fill.execution.time < end_time
        ]

        executions_by_order = {}
        for fill in filtered_executions:
            order_id = fill.execution.orderId
            executions_by_order.setdefault(order_id, []).append(fill)

        for order_id, fills in executions_by_order.items():
            combo_summary = next(
                (fill for fill in fills if getattr(fill.contract, 'strike', 0) == 0), None
            )
            legs = [
                {
                    "symbol": fill.contract.symbol,
                    "strike": getattr(fill.contract, 'strike', None),
                    "type": getattr(fill.contract, 'right', None),
                    "side": fill.execution.side,
                    "price": fill.execution.price,
                }
                for fill in fills if getattr(fill.contract, 'strike', 0) != 0
            ]

            if combo_summary:
                net_fill_price = combo_summary.execution.price
                print(f"  Spread: {combo_summary.contract.symbol} Net Fill Price: {net_fill_price:.2f}")
            else:
                print(f"  Spread: {legs[0]['symbol']} (Combo Summary Missing)")

            for leg in legs:
                print(f"    {leg['symbol']} {leg['side']} {leg['type']} {leg['strike']} at {leg['price']}")

        return executions_by_order
    except Exception as e:
        print(f"Error: Failed to retrieve filled orders: {e}")
        return []


def submit_limit_order(order_contract, limit_price: float, action: str, is_live: bool, quantity: int,
                       order_ref: str = ''):
    """
    Submits a limit order for the given contract and dynamically adjusts the price based on the minimum tick size.

    Args:
        order_contract: The contract for which the order is being placed.
        limit_price: The limit price for the order.
        action: 'BUY' or 'SELL'.
        is_live: Whether to transmit the order.
        quantity: Number of contracts.

    Returns:
        The status of the order submission.
    """
    # Adjust the limit price to align with the minimum tick size
    min_tick = get_min_tick(order_contract.symbol, limit_price)
    if not min_tick:
        print(f"Warning: No tick size found for symbol {order_contract.symbol} at price {limit_price}. Using original price.")
    else:
        # Round limit price to the nearest valid tick
        limit_price = round(limit_price / min_tick) * min_tick
        print(f"Adjusted limit price for {order_contract.symbol}: {limit_price} (Min Tick: {min_tick})")

    order = LimitOrder(action=action, lmtPrice=limit_price, transmit=is_live, totalQuantity=quantity)
    order.orderRef = order_ref

    try:
        trade = ib.placeOrder(order_contract, order)
        ib.sleep(2)

        if trade.orderStatus.status in ('Submitted', 'PendingSubmit', 'PreSubmitted', 'Filled'):
            return f"Order sent with status: {trade.orderStatus.status}"
        else:
            return f"Order failed with status: {trade.orderStatus.status}"
    except Exception as e:
        return f"Error: Order placement failed with error: {str(e)}"


def submit_adaptive_order(order_contract, limit_price: float = None, order_type: str = 'MKT', action: str = 'BUY',
                          is_live: bool = False, quantity: int = 1, order_ref: str = ''):
    """
    Submits an adaptive order (limit or market) for the given contract and checks the status.

    Args:
        order_contract: The contract for which the order is being placed.
        limit_price: The limit price for the order (if None, a market order is placed).
        order_type: Type of order ('MKT' or 'LMT').
        action: 'BUY' or 'SELL'.
        is_live: Whether to transmit the order.
        quantity: Number of contracts.

    Returns:
        The Trade object for the submitted order or None in case of an error.
    """
    try:
        order_contract.exchange = 'SMART' # override for adaptive order type.
        print("---- Starting submit_adaptive_order ----")
        print(f"Contract Details: {order_contract}")
        print(f"Parameters -> Limit Price: {limit_price}, Order Type: {order_type}, Action: {action}, Is Live: {is_live}, Quantity: {quantity}")

        # Define Adaptive Algo parameters
        algo_params = [TagValue(tag='adaptivePriority', value='Normal')]
        print(f"Algo Params: {algo_params}")

        # Create the order object
        order = Order(
            action=action,
            orderType=order_type,
            totalQuantity=quantity,
            lmtPrice=limit_price if limit_price is not None else None,
            algoStrategy='Adaptive',
            algoParams=algo_params,
            transmit=is_live,
            orderRef=order_ref
        )
        print(f"Order created: {order}")

        # Place the order using IB
        trade = ib.placeOrder(order_contract, order)
        print("Order submitted to IB API. Waiting for status update...")

        # Sleep for 2 seconds to allow order status to propagate
        ib.sleep(2)

        # Fetch and log the final order status
        final_status = trade.orderStatus.status
        print(f"Order submitted successfully:")
        print(f"    Order ID: {trade.order.orderId}")
        print(f"    Final Status: {final_status}")
        print(f"    Filled Quantity: {trade.orderStatus.filled}, Remaining Quantity: {trade.orderStatus.remaining}")

        return trade

    except Exception as e:
        print("Error occurred during submit_adaptive_order execution:")
        print(f"    Error: {e}")
        return None

def create_bag(und_contract: Contract, legs: list, actions: list, ratios: list) -> Contract:
    print(f"Creating combo bag with parameters: {locals()}")
    bag_contract = Contract()
    bag_contract.symbol = und_contract.symbol
    bag_contract.secType = 'BAG'
    bag_contract.currency = und_contract.currency
    bag_contract.exchange = und_contract.exchange
    bag_contract.comboLegs = []

    for leg, action, ratio in zip(legs, actions, ratios):
        combo_leg = ComboLeg()
        combo_leg.conId = leg.conId
        combo_leg.action = action
        combo_leg.ratio = ratio
        combo_leg.exchange = leg.exchange
        combo_leg.openClose = 0
        bag_contract.comboLegs.append(combo_leg)

    return bag_contract