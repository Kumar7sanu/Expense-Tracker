import sqlite3
from pathlib import Path
from typing import Optional

DB_FILE = Path("expenses.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS txns(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        date TEXT NOT NULL,

        month TEXT NOT NULL,

        weekday TEXT NOT NULL,

        merchant TEXT NOT NULL,

        category TEXT NOT NULL,

        amount REAL NOT NULL,

        note TEXT,

        type TEXT NOT NULL,

        chat_id INTEGER NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """)

    conn.commit()
    conn.close()


# ---------------------------------
# Add Transaction
# ---------------------------------

def add_transaction(
    *,
    date,
    month,
    weekday,
    merchant,
    category,
    amount,
    note,
    txn_type,
    chat_id
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO txns(

            date,
            month,
            weekday,
            merchant,
            category,
            amount,
            note,
            type,
            chat_id

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """,

        (
            date,
            month,
            weekday,
            merchant,
            category,
            amount,
            note,
            txn_type,
            chat_id
        )
    )

    conn.commit()
    conn.close()


# ---------------------------------
# Undo
# ---------------------------------

def undo_last(chat_id: int):

    conn = get_connection()

    row = conn.execute(

        """
        SELECT id

        FROM txns

        WHERE chat_id=?

        ORDER BY id DESC

        LIMIT 1

        """,

        (chat_id,)

    ).fetchone()

    if row:

        conn.execute(

            "DELETE FROM txns WHERE id=?",

            (row["id"],)

        )

        conn.commit()

        conn.close()

        return True

    conn.close()

    return False


# ---------------------------------
# Fetch All
# ---------------------------------

def get_all():

    conn = get_connection()

    rows = conn.execute(

        """

        SELECT *

        FROM txns

        ORDER BY date DESC,id DESC

        """

    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ---------------------------------
# Recent Transactions
# ---------------------------------

def recent(limit=10):

    conn = get_connection()

    rows = conn.execute(

        """

        SELECT *

        FROM txns

        ORDER BY id DESC

        LIMIT ?

        """,

        (limit,)

    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ---------------------------------
# Totals
# ---------------------------------

def total_income(month: Optional[str] = None):

    conn = get_connection()

    if month:

        row = conn.execute(

            """

            SELECT SUM(amount) total

            FROM txns

            WHERE type='income'

            AND month=?

            """,

            (month,)

        ).fetchone()

    else:

        row = conn.execute(

            """

            SELECT SUM(amount) total

            FROM txns

            WHERE type='income'

            """

        ).fetchone()

    conn.close()

    return row["total"] or 0


def total_expense(month: Optional[str] = None):

    conn = get_connection()

    if month:

        row = conn.execute(

            """

            SELECT SUM(amount) total

            FROM txns

            WHERE type='expense'

            AND month=?

            """,

            (month,)

        ).fetchone()

    else:

        row = conn.execute(

            """

            SELECT SUM(amount) total

            FROM txns

            WHERE type='expense'

            """

        ).fetchone()

    conn.close()

    return row["total"] or 0


# ---------------------------------
# Category Summary
# ---------------------------------

def category_summary(month=None):

    conn = get_connection()

    if month:

        rows = conn.execute(

            """

            SELECT

                category,

                SUM(amount) total

            FROM txns

            WHERE type='expense'

            AND month=?

            GROUP BY category

            """,

            (month,)

        ).fetchall()

    else:

        rows = conn.execute(

            """

            SELECT

                category,

                SUM(amount) total

            FROM txns

            WHERE type='expense'

            GROUP BY category

            """

        ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ---------------------------------
# Merchant Summary
# ---------------------------------

def merchant_summary(month=None):

    conn = get_connection()

    if month:

        rows = conn.execute(

            """

            SELECT

                merchant,

                SUM(amount) total

            FROM txns

            WHERE type='expense'

            AND month=?

            GROUP BY merchant

            ORDER BY total DESC

            """,

            (month,)

        ).fetchall()

    else:

        rows = conn.execute(

            """

            SELECT

                merchant,

                SUM(amount) total

            FROM txns

            WHERE type='expense'

            GROUP BY merchant

            ORDER BY total DESC

            """

        ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ---------------------------------
# Testing
# ---------------------------------

if __name__ == "__main__":

    init_db()

    print("✓ Database initialized")

    print(get_all())