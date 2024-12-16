

from ib_insync import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RUT_Option_Qualifier")

# Connect to IBKR
ib = IB()
ib.connect('127.0.0.1', 7500, clientId=1)  # Use 7497 for Paper Trading, 7496 for Live Trading

def qualify_rut_option(expiry: str, strike: float, right: str, exchange: str = 'SMART') -> Option:
    """
    Qualify a RUT option contract.

    Args:
        expiry (str): Option expiration date in 'YYYYMMDD' format.
        strike (float): Option strike price.
        right (str): Option right ('C' for Call, 'P' for Put).
        exchange (str): Exchange where the option trades (default is 'SMART').

    Returns:
        Option: Qualified RUT option contract.
    """
    try:
        logger.info(f"Qualifying RUT Option - Expiry: {expiry}, Strike: {strike}, Right: {right}, Exchange: {exchange}")

        # Define the option contract
        rut_option = Option(
            symbol='RUT',
            lastTradeDateOrContractMonth=expiry,
            strike=strike,
            right=right,
            exchange=exchange,
            currency='USD'
        )

        # Qualify the contract
        qualified_option = ib.qualifyContracts(rut_option)

        if qualified_option:
            logger.info(f"Qualified RUT Option: {qualified_option[0]}")
            return qualified_option[0]
        else:
            logger.error("Failed to qualify the RUT option contract.")
            return None

    except Exception as e:
        logger.exception(f"Error qualifying RUT option: {e}")
        return None


if __name__ == '__main__':
    # Parameters for the RUT option
    expiry_date = '20241220'  # Format YYYYMMDD
    strike_price = 2000.0     # Strike price
    option_right = 'C'        # 'C' for Call, 'P' for Put

    # Qualify the RUT Option
    rut_option_contract = qualify_rut_option(expiry_date, strike_price, option_right)

    # Print result
    if rut_option_contract:
        print("Successfully qualified RUT Option:")
        print(rut_option_contract)
    else:
        print("Failed to qualify RUT Option.")

    # Disconnect from IBKR
    ib.disconnect()