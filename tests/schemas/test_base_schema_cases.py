from datetime import date, datetime

from neo4j.time import Date, DateTime
from pytest_cases import case

from tests.utils import random_date, random_datetime


class CaseDates:
    @case(tags=["date"])
    def case_py_date(self) -> tuple[date, date]:
        d = random_date()
        return d, d

    @case(tags=["date"])
    def case_neo4j_date(self) -> tuple[date, date]:
        d = random_date()
        return Date(d.year, d.month, d.day), d

    @case(tags=["datetime"])
    def case_py_datetime(self) -> tuple[datetime, datetime]:
        d = random_datetime()
        return d, d

    @case(tags=["datetime"])
    def case_neo4j_datetime(self) -> tuple[datetime, datetime]:
        d = random_datetime()
        return DateTime(
            d.year, d.month, d.day, d.hour, d.minute, d.second, tzinfo=d.tzinfo
        ), d
