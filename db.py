# Standard libraries imports
from contextlib import contextmanager
from sqlite3 import Connection, Cursor, connect
from typing import Iterator

# Moduls imports
from schema import Statistics, User, UserStatistics

DB_PATH: str = "/data/database.db"

@contextmanager
def db_connection() -> Iterator[Cursor]:
    conn: Connection = connect(DB_PATH)
    cursor: Cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with db_connection() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                tg_name TEXT DEFAULT '',
                name TEXT DEFAULT '',
                desire TEXT DEFAULT '',
                is_registered BOOLEAN DEFAULT 0
            )
        """)

def add_user(user_id: int, tg_name: str) -> None:
    with db_connection() as cursor:
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, tg_name)
            VALUES (?, ?)
        """, (user_id, tg_name))

def update_name(user_id: int, name: str) -> None:
    with db_connection() as cursor:
        cursor.execute("""
            UPDATE users SET name = ?
            WHERE id = ?
        """, (name, user_id))

def update_desire(user_id: int, desire: str) -> None:
    with db_connection() as cursor:
        cursor.execute("""
            UPDATE users SET desire = ?, is_registered = 1
            WHERE id = ?
        """, (desire, user_id))

def get_user(user_id: int) -> User | None:
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row: tuple[int, str , str , str, int] | None = cursor.fetchone()
    if row is None:
        return None
    user: User = User(id=row[0], tg_name=row[1], name=row[2], desire=row[3])
    return user

def get_statistics() -> Statistics:
    with db_connection() as cursor:
        cursor.execute("SELECT tg_name, name, is_registered FROM users")
        rows: list[tuple[str, str, int]] = cursor.fetchall()
        statistics: Statistics = Statistics(users=[
            UserStatistics(tg_name=row[0], name=row[1], is_registered=bool(row[2])) for row in rows
        ])
    return statistics

def get_data() -> list[User]:
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM users WHERE is_registered = 1")
        rows: list[tuple[int, str , str , str, int]] = cursor.fetchall()
        users: list[User] = [
            User(id=row[0], tg_name=row[1], name=row[2], desire=row[3]) for row in rows
        ]
    return users
