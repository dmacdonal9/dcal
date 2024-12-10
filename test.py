from dcal import close_dcal
from datetime import datetime, timedelta
import cfg

# Determine the closing date (Monday if Friday, else tomorrow)
today = datetime.now()
if today.weekday() == 4:  # Friday
    closing_date = today + timedelta(days=3)  # Skip to Monday
else:
    closing_date = today + timedelta(days=0)  # Next day

closing_date_time = closing_date.strftime('%Y%m%d') + ' ' + cfg.time_to_close  # Full closing time

close_dcal('SPX',closing_date_time)