"""Tests utilities."""
import string
import time
from datetime import date, datetime, timezone
from random import choices, getrandbits, randint, randrange

from pydantic import AnyHttpUrl

MOCK_READ_EMAIL = "user@test.it"
MOCK_WRITE_EMAIL = "admin@test.it"


def random_bool() -> bool:
    """Return a random bool."""
    return getrandbits(1)


def random_lower_string() -> str:
    """Return a generic random string."""
    return "".join(choices(string.ascii_lowercase, k=32))


def random_url() -> AnyHttpUrl:
    """Return a random URL."""
    return "http://" + random_lower_string() + ".com"


def random_email() -> str:
    """Return a generic email."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_int(start: int = -100, end: int = 100) -> str:
    """Return a generic integer."""
    return randrange(start, end)


def random_non_negative_int() -> int:
    """Return a generic non negative integer.

    0 included.
    """
    return randrange(100)


def random_positive_int() -> int:
    """Return a generic positive integer.

    0 excluded.
    """
    return randrange(1, 100)


def random_float(start: int = -100, end: int = 100) -> float:
    """Return a random float between start and end (included)."""
    return float(random_int(start, end))


def random_positive_float() -> float:
    """Return a generic positive float.

    0 excluded.
    """
    return float(random_positive_int())


def random_non_negative_float() -> float:
    """Return a generic positive float.

    0 included.
    """
    return float(random_non_negative_int())


def random_datetime() -> datetime:
    """Return a random date and time."""
    d = randint(1, int(time.time()))
    return datetime.fromtimestamp(d, tz=timezone.utc)


def random_date() -> date:
    """Return a random date."""
    d = randint(1, int(time.time()))
    return date.fromtimestamp(d)


def random_start_end_dates() -> tuple[date, date]:
    """Return a random couples of valid start and end dates (in order)."""
    d1 = random_date()
    d2 = random_date()
    while d1 == d2:
        d2 = random_date()
    if d1 < d2:
        start_date = d1
        end_date = d2
    else:
        start_date = d2
        end_date = d1
    return start_date, end_date


def random_date_before(end_date: date):
    timestamp = int(time.mktime(end_date.timetuple()))
    return date.fromtimestamp(randrange(0, timestamp))


def random_date_after(start_date: date):
    timestamp = int(time.mktime(start_date.timetuple()))
    return date.fromtimestamp(randrange(timestamp * 2, timestamp * 3))
