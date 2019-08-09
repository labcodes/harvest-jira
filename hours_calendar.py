from cprint import cprint
from datetime import datetime, date, timedelta


LAST_DAY_FILE = '.aux_days'
DATE_FORMAT = '%Y/%m/%d'


def get_date_range():
    try:
        with open(LAST_DAY_FILE, 'r') as f:
            raw_last_day = f.read().strip()
            last_day = datetime.strptime(raw_last_day, DATE_FORMAT).date()
    except FileNotFoundError:
        cprint.warn(f"You don't have a last day configured yet.")
        cprint.warn(f"Please input the start date:\n")
        last_day = None
        while not last_day:
            raw_last_day = input(f"Date as {DATE_FORMAT}: ").strip()
            try:
                last_day = datetime.strptime(raw_last_day, DATE_FORMAT).date()
            except ValueError:
                cprint.err(f"Invalid date format. Please try again...")

    date_to = date.today() - timedelta(days=1)
    return last_day, date_to


def update_last_day(new_last_day):
    with open(LAST_DAY_FILE, 'w') as f:
        f.write(new_last_day.strftime(DATE_FORMAT))
    cprint.ok(f"Next time you run the script, it'll start from {new_last_day.isoformat()}.")
