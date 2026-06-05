from pathlib import Path
from typing import Iterable
import os

from dotenv import load_dotenv
import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_connection(database: str | None = None):
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=database or os.getenv("MYSQL_DATABASE", "ecommerce_dw"),
        user=os.getenv("MYSQL_USER", "ecommerce_user"),
        password=os.getenv("MYSQL_PASSWORD", "ecommerce_pass"),
        autocommit=False,
    )


def execute_sql_file(path: Path) -> None:
    sql_text = path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql_text.split(";") if statement.strip()]
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        conn.commit()


def truncate_tables(tables: Iterable[str]) -> None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

