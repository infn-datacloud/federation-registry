"""Tests utilities."""
import string
import time
from datetime import date, datetime, timezone
from enum import Enum
from random import choice, choices, getrandbits, randint, random, randrange
from typing import Any, Type

from pycountry import countries
from pydantic import AnyHttpUrl

from fed_reg.image.enum import ImageOS
from fed_reg.models import BaseNodeRead
from fed_reg.provider.enum import ProviderStatus, ProviderType

MOCK_READ_EMAIL = "user@test.it"
MOCK_WRITE_EMAIL = "admin@test.it"


def random_lower_string() -> str:
    """Return a generic random string."""
    return "".join(choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    """Return a generic email."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_int() -> str:
    """Return a generic integer."""
    return randrange(-100, 100)


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


def random_bool() -> bool:
    """Return a random bool."""
    return getrandbits(1)


def random_datetime() -> datetime:
    """Return a random date and time."""
    d = randint(1, int(time.time()))
    return datetime.fromtimestamp(d, tz=timezone.utc)


def random_date() -> date:
    """Return a random date."""
    d = randint(1, int(time.time()))
    return date.fromtimestamp(d)


def random_url() -> AnyHttpUrl:
    """Return a random URL."""
    return "http://" + random_lower_string() + ".com"


def random_float(start: int, end: int) -> float:
    """Return a random float between start and end (included)."""
    return randint(start, end - 1) + random()


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


def detect_public_extended_details(read_class: Type[BaseNodeRead]) -> tuple[bool, bool]:
    """From class name detect if it public or not, extended or not."""
    cls_name = read_class.__name__
    is_public = False
    is_extended = False
    if "Public" in cls_name:
        is_public = True
    if "Extended" in cls_name:
        is_extended = True
    return is_public, is_extended


def random_country() -> str:
    """Return random country."""
    return choice([i.name for i in countries])


def random_latitude() -> float:
    """Return a valid latitude value."""
    return randint(-90, 89) + random()


def random_longitude() -> float:
    """Return a valid longitude value."""
    return randint(-180, 179) + random()


def random_provider_type() -> ProviderType:
    return choice([i for i in ProviderType])


def random_provider_status() -> ProviderStatus:
    return choice([i for i in ProviderStatus])


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


def random_service_name(enum_cls: Enum) -> Any:
    return choice([i for i in enum_cls])


def random_image_os_type() -> ImageOS:
    return choice([i for i in ImageOS])


def random_date_before(end_date: date):
    timestamp = int(time.mktime(end_date.timetuple()))
    return date.fromtimestamp(randrange(0, timestamp))


def random_date_after(start_date: date):
    timestamp = int(time.mktime(start_date.timetuple()))
    return date.fromtimestamp(randrange(timestamp * 2, timestamp * 3))
