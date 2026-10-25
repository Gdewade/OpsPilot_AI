import os
import psycopg # psycopg is a PostgreSQL adapter for Python. It allows Python applications to connect to PostgreSQL and execute SQL queries.
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing from .env")

    return psycopg.connect(database_url)
