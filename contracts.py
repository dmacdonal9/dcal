from ib_insync import Stock, Future, FuturesOption, Option, Index
from ib_instance import ib

def get_conid(symbol: str, sec_type: str, exchange='SMART', currency='USD', dynamic_front_month=False):
    """
    Retrieves the conId for the specified symbol and security type.
    If dynamic_front_month is True and sec_type is 'FUT', dynamically determines the front-month contract.

    :param symbol: The symbol to look up.
    :param sec_type: The security type ('STK', 'FUT', 'FOP', 'OPT', 'INDX').
    :param exchange: The exchange (default: 'SMART').
    :param currency: The currency (default: 'USD').
    :param dynamic_front_month: If True, dynamically determines the front month for 'FUT'.
    :return: The conId for the specified contract or None if not found.
    """
    try:
        # Define the contract based on the security type
        if sec_type == 'STK':
            contract = Stock(symbol=symbol, exchange=exchange, currency=currency)
        elif sec_type == 'FUT':
            if dynamic_front_month:
                # Dynamically find the front-month futures contract
                contracts = ib.reqContractDetails(Future(symbol=symbol, exchange=exchange))
                if not contracts:
                    raise ValueError(f"No futures contracts found for {symbol} on exchange {exchange}.")
                # Sort contracts by expiration date
                contracts.sort(key=lambda c: c.contract.lastTradeDateOrContractMonth)
                # Use the earliest expiration contract
                front_month_contract = contracts[0].contract
                print(f"Front-month contract for {symbol} is {front_month_contract.lastTradeDateOrContractMonth}.")
                contract = front_month_contract
            else:
                raise ValueError("dynamic_front_month must be True or specify a lastTradeDateOrContractMonth.")
        elif sec_type == 'FOP':
            contract = FuturesOption(symbol=symbol, exchange=exchange, currency=currency)
        elif sec_type == 'OPT':
            contract = Option(symbol=symbol, exchange=exchange, currency=currency)
        elif sec_type == 'INDX':
            contract = Index(symbol=symbol, exchange=exchange, currency=currency)
        else:
            raise ValueError(f"Unsupported security type: {sec_type}")

        # Qualify the contract to retrieve full details, including conId
        qualified_contract = ib.qualifyContracts(contract)

        if qualified_contract:
            con_id = qualified_contract[0].conId
            #print(f"{symbol} ({sec_type}) conId: {con_id}")
            return con_id
        else:
            print(f"Contract for {symbol} ({sec_type}) not found.")
            return None
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"Error: {e}")
    return None


#conid = get_conid(symbol='ES', sec_type='FUT', exchange='CME', dynamic_front_month=True)
#if conid:
#    print(f"Retrieved conId: {conid}")