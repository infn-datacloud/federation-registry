"""Database configuration utilities for Neo4j connections."""

from logging import Logger

from neomodel import config
from pydantic import AnyUrl


def set_neo4j_db_url(neo4j_db_url: str, logger: Logger) -> AnyUrl:
    """Set the Neo4j database URL in the configuration.

    Args:
        neo4j_db_url (str): The new database URL to set.
        logger (Logger): Logger instance for logging the database URL.

    Returns:
        AnyUrl: The same URL that was provided as input.

    """
    logger.info("Neo4j database URL: %s", neo4j_db_url)
    config.DATABASE_URL = neo4j_db_url
