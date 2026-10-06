from __future__ import annotations

import os

import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql:///adintel?host=/var/run/postgresql",
)


def connect_db() -> psycopg.Connection:
    """Open a short-lived PostgreSQL connection for one request or seed operation."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)
