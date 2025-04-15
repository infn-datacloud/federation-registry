"""File to set tests configuration parameters and common fixtures."""

import os

import pytest
from neomodel import config, db


def pytest_addoption(parser):
    """
    Adds the command line option --resetdb.

    :param parser: The parser object. Please see <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_addoption>`_
    :type Parser object: For more information please see <https://docs.pytest.org/en/latest/reference.html#_pytest.config.Parser>`_
    """
    parser.addoption(
        "--resetdb",
        action="store_true",
        help="Ensures that the database is clear prior to running tests for neomodel",
        default=False,
    )


@pytest.fixture(scope="session", autouse=True)
def setup_neo4j_session(request):
    """
    Provides initial connection to the database and sets up the rest of the test suite

    :param request: The request object. Please see <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_sessionstart>`_
    :type Request object: For more information please see <https://docs.pytest.org/en/latest/reference.html#request>`_
    """
    config.DATABASE_URL = os.environ.get(
        "NEO4J_TEST_URL", "bolt://neo4j:password@localhost:7687"
    )

    # Clear the database if required
    database_is_populated, _ = db.cypher_query(
        "MATCH (a) return count(a)>0 as database_is_populated"
    )
    if database_is_populated[0][0]:
        if not request.config.getoption("resetdb"):
            raise SystemError(
                "Please note: The database seems to be populated.\n"
                + "\tEither delete all nodesand edges manually, or set the "
                + "--resetdb parameter when calling pytest\n\n"
                + "\tpytest --resetdb."
            )

        db.clear_neo4j_database(clear_constraints=True, clear_indexes=True)
        db.install_all_labels()

    db.cypher_query(
        "CREATE OR REPLACE USER test SET PASSWORD 'foobarbaz' CHANGE NOT REQUIRED"
    )
    if db.database_edition == "enterprise":
        db.cypher_query("GRANT ROLE publisher TO test")
        db.cypher_query("GRANT IMPERSONATE (test) ON DBMS TO admin")


@pytest.fixture(autouse=True)
def cleanup():
    """Clear DB after every test

    Yields:
        Generator[None, Any, None]: Nothing
    """
    yield
    db.clear_neo4j_database()


# @pytest.fixture(autouse=True)
# def clear_os_environment(monkeypatch) -> None:
#     """Clear the OS environment."""
#     for k in Settings.__fields__.keys():
#         monkeypatch.delenv(k, None)
#     if "test_settings_default" not in os.environ.get("PYTEST_CURRENT_TEST", None):
#         settings.NEO4J_DB_URL = os.environ.get(
#             "NEO4J_TEST_URL", "bolt://neo4j:password@localhost:7687"
#         )
